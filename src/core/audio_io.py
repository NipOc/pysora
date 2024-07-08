import time
import numpy as np
import sounddevice as sd
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

class AudioIO:
    def __init__(self, sample_rate, buffer_size):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.last_operation_duration = 0

    def play_and_record(self, signal, input_device, output_device, progress_callback):
        recorded = np.zeros_like(signal)
        total_frames = len(signal)
        
        def callback(indata, outdata, frames, time, status):
            if status:
                print(status)
            current_frame = callback.frame
            if current_frame + frames > total_frames:
                frames = total_frames - current_frame
                raise sd.CallbackStop
            outdata[:frames, 0] = signal[current_frame:current_frame+frames]
            recorded[current_frame:current_frame+frames] = indata[:frames, 0]
            callback.frame += frames
            progress = int(100 * callback.frame / total_frames)
            QTimer.singleShot(0, lambda: progress_callback(progress))

        callback.frame = 0

        try:
            with sd.Stream(samplerate=self.sample_rate, blocksize=self.buffer_size,
                           device=(input_device, output_device), channels=1,
                           callback=callback, latency='low') as stream:
                start_time = time.perf_counter()
                stream.start()
                
                # Use a timer to update progress more frequently
                update_interval = 50  # ms
                def update_progress():
                    if stream.active:
                        progress = int(100 * callback.frame / total_frames)
                        progress_callback(progress)
                        QTimer.singleShot(update_interval, update_progress)
                
                QTimer.singleShot(0, update_progress)
                
                while stream.active:
                    sd.sleep(100)
                    QApplication.processEvents()
                
                end_time = time.perf_counter()
            
            self.last_operation_duration = end_time - start_time
        except sd.PortAudioError as e:
            raise RuntimeError(f"Error during audio playback and recording: {str(e)}")

        return recorded