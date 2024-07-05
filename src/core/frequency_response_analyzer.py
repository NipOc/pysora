import numpy as np
from scipy.signal import chirp, correlate
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication
from .audio_io import AudioIO
from models.analyzer_settings import AnalyzerSettings

class FrequencyResponseAnalyzer:
    def __init__(self, settings: AnalyzerSettings):
        self.settings = settings
        self.audio_io = AudioIO(settings.sample_rate, settings.buffer_size)

    def generate_sweep(self):
        t = np.linspace(0, self.settings.duration, int(self.settings.sample_rate * self.settings.duration), False)
        sweep = chirp(t, f0=self.settings.start_freq, f1=self.settings.end_freq, t1=self.settings.duration, method='logarithmic')
        return sweep.astype(np.float32)

    def measure_response(self, input_device, output_device, progress_callback):
        sweep = self.generate_sweep()
        recorded = self.audio_io.play_and_record(sweep, input_device, output_device, progress_callback)
        
        delay_samples, delay_ms = self._calculate_delay(recorded, sweep)
        freqs, magnitudes = self._calculate_frequency_response(recorded, sweep, delay_samples)

        debug_info = {
            'total_duration': self.audio_io.last_operation_duration,
            'delay_samples': delay_samples,
            'delay_ms': delay_ms,
            'recorded_length': len(recorded),
            'expected_length': len(sweep)
        }

        return freqs, magnitudes, delay_ms, debug_info

    def _calculate_delay(self, recorded, sweep):
        correlation = correlate(recorded, sweep, mode='full')
        delay_samples = np.argmax(correlation) - (len(sweep) - 1)
        delay_ms = (delay_samples / self.settings.sample_rate) * 1000
        return delay_samples, delay_ms

    def _calculate_frequency_response(self, recorded, sweep, delay_samples):
        if delay_samples > 0:
            recorded = recorded[delay_samples:]
        elif delay_samples < 0:
            recorded = np.pad(recorded, (abs(delay_samples), 0))
        recorded = recorded[:len(sweep)]  # Ensure same length as sweep

        fft_result = np.fft.rfft(recorded)
        freqs = np.fft.rfftfreq(len(recorded), 1 / self.settings.sample_rate)
        magnitudes = np.abs(fft_result)
        return freqs, magnitudes