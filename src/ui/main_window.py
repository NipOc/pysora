from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
                             QWidget, QPushButton, QMessageBox, QLabel, QProgressDialog,
                             QApplication, QGroupBox, QFileDialog, QInputDialog)
from PyQt6.QtCore import Qt
import numpy as np

from .widgets.device_selector import DeviceSelector
from .widgets.frequency_input import FrequencyInput
from .widgets.smoothing_options import SmoothingOptions
from .widgets.frequency_response_graph import FrequencyResponseGraph
from core.frequency_response_analyzer import FrequencyResponseAnalyzer
from models.analyzer_settings import AnalyzerSettings
from utilities.signal_processing import apply_smoothing
from utilities.curve_operations import CurveOperations

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.freqs = None
        self.magnitudes = None
        self.delay = None
        self.progress_dialog = None
        self.target_freqs = None
        self.target_mags = None
        self.curve_ops = CurveOperations()

        self.setWindowTitle("PySora - Audio Frequency Response Analyzer")
        self.setGeometry(100, 100, 1200, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.setup_ui()

    def setup_ui(self):
        # Control panel
        control_panel = QGroupBox("Control Panel")
        control_layout = QGridLayout()
        control_panel.setLayout(control_layout)

        # Device selection
        device_group = QGroupBox("Device Selection")
        device_layout = QVBoxLayout()
        self.device_selector = DeviceSelector()
        device_layout.addWidget(self.device_selector)
        device_group.setLayout(device_layout)
        control_layout.addWidget(device_group, 0, 0, 1, 2)

        # Frequency input
        freq_group = QGroupBox("Frequency Settings")
        freq_layout = QFormLayout()
        self.frequency_input = FrequencyInput()
        freq_layout.addRow("Start Frequency (Hz):", self.frequency_input.start_freq)
        freq_layout.addRow("End Frequency (Hz):", self.frequency_input.end_freq)
        freq_layout.addRow("Duration (s):", self.frequency_input.duration)
        freq_group.setLayout(freq_layout)
        control_layout.addWidget(freq_group, 0, 2, 1, 1)

        # Smoothing options
        smoothing_group = QGroupBox("Smoothing Options")
        smoothing_layout = QFormLayout()
        self.smoothing_options = SmoothingOptions()
        smoothing_layout.addRow("Method:", self.smoothing_options.smoothing_method)
        smoothing_layout.addRow("Window:", self.smoothing_options.smoothing_window)
        smoothing_group.setLayout(smoothing_layout)
        control_layout.addWidget(smoothing_group, 0, 3, 1, 1)

        # Run button
        self.run_button = QPushButton("Run Test")
        self.run_button.clicked.connect(self.run_test)
        control_layout.addWidget(self.run_button, 1, 0, 1, 4)

        self.main_layout.addWidget(control_panel)

        # Graph
        self.graph = FrequencyResponseGraph()
        self.main_layout.addWidget(self.graph)

        # Status bar
        self.status_bar = self.statusBar()
        self.delay_label = QLabel("Audio Delay: N/A")
        self.status_bar.addPermanentWidget(self.delay_label)

        # Connect smoothing options to plot update
        self.smoothing_options.smoothing_method.currentIndexChanged.connect(self.update_plot)
        self.smoothing_options.smoothing_window.valueChanged.connect(self.update_plot)

        # Add new buttons for loading target curve and saving measurement
        button_layout = QHBoxLayout()
        self.load_target_button = QPushButton("Load Target Curve")
        self.load_target_button.clicked.connect(self.load_target_curve)
        self.save_measurement_button = QPushButton("Save Measurement")
        self.save_measurement_button.clicked.connect(self.save_measurement)
        button_layout.addWidget(self.load_target_button)
        button_layout.addWidget(self.save_measurement_button)
        self.main_layout.addLayout(button_layout)

        # Add pass/fail label
        self.pass_fail_label = QLabel("Pass/Fail: N/A")
        self.main_layout.addWidget(self.pass_fail_label)


    def load_target_curve(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Target Curve", "", "JSON Files (*.json)")
        if file_path:
            try:
                self.target_freqs, self.target_mags, metadata = self.curve_ops.load_target_curve(file_path)
                self.graph.add_target_curve(self.target_freqs, self.target_mags)
                QMessageBox.information(self, "Success", "Target curve loaded successfully.")
                
                # If there's a current measurement, compare it to the target
                if self.freqs is not None and self.magnitudes is not None:
                    self.compare_to_target()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load target curve: {str(e)}")

    def save_measurement(self):
        if self.freqs is None or self.magnitudes is None:
            QMessageBox.warning(self, "Warning", "No measurement data available to save.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save Measurement", "", "JSON Files (*.json)")
        if file_path:
            metadata = {
                "start_freq": self.frequency_input.start_freq.value(),
                "end_freq": self.frequency_input.end_freq.value(),
                "duration": self.frequency_input.duration.value(),
                "smoothing_method": self.smoothing_options.smoothing_method.currentText(),
                "smoothing_window": self.smoothing_options.smoothing_window.value(),
                "delay": self.delay
            }
            try:
                self.curve_ops.save_measurement(file_path, self.freqs, self.magnitudes, metadata)
                QMessageBox.information(self, "Success", "Measurement saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save measurement: {str(e)}")

    def run_test(self):
        self.show_progress_dialog("Running test...")

        settings = AnalyzerSettings(
            self.frequency_input.start_freq.value(),
            self.frequency_input.end_freq.value(),
            self.frequency_input.duration.value(),
            48000,  # Sample rate
            256     # Buffer size
        )
        
        analyzer = FrequencyResponseAnalyzer(settings)

        input_device = self.device_selector.input_devices.currentData()
        output_device = self.device_selector.output_devices.currentData()

        try:
            self.freqs, self.magnitudes, self.delay, debug_info = analyzer.measure_response(input_device, output_device, self.update_progress)
            self.close_progress_dialog()
            self.update_plot()
            self.delay_label.setText(f"Audio Delay: {self.delay:.2f} ms")
            
            if self.target_freqs is not None and self.target_mags is not None:
                self.compare_to_target()
            
            debug_msg = (f"Total Duration: {debug_info['total_duration']:.2f}s\n"
                         f"Delay Samples: {debug_info['delay_samples']}\n"
                         f"Delay: {debug_info['delay_ms']:.2f} ms\n"
                         f"Recorded Length: {debug_info['recorded_length']} samples\n"
                         f"Expected Length: {debug_info['expected_length']} samples")
            QMessageBox.information(self, "Debug Info", debug_msg)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
        finally:
            self.close_progress_dialog()

    def compare_to_target(self):
        compare_freqs, difference = self.curve_ops.compare_to_target(
            self.freqs, self.magnitudes, self.target_freqs, self.target_mags)
        
        self.graph.add_difference_curve(compare_freqs, difference)
        
        tolerance, ok = QInputDialog.getDouble(self, "Set Tolerance", "Enter maximum allowed deviation (dB):", 3.0, 0.1, 20.0, 1)
        if ok:
            passed = self.curve_ops.check_pass_fail(difference, tolerance)
            self.pass_fail_label.setText(f"Pass/Fail: {'PASS' if passed else 'FAIL'}")
            self.pass_fail_label.setStyleSheet("color: green;" if passed else "color: red;")

    def show_progress_dialog(self, title):
        self.close_progress_dialog()  # Ensure any existing dialog is closed
        self.progress_dialog = QProgressDialog(title, "Cancel", 0, 100, self)
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setAutoClose(False)
        self.progress_dialog.setAutoReset(False)
        self.progress_dialog.setValue(0)
        self.progress_dialog.setMinimumDuration(0)  # Show immediately
        self.progress_dialog.show()
        QApplication.processEvents()  # Ensure the dialog is displayed immediately

    def close_progress_dialog(self):
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        QApplication.processEvents()  # Ensure the UI updates after closing the dialog

    def update_progress(self, value):
        if self.progress_dialog:
            self.progress_dialog.setValue(value)
            QApplication.processEvents()  # Ensure UI updates

    def update_plot(self):
        if self.freqs is None or self.magnitudes is None:
            return

        self.show_progress_dialog("Applying smoothing...")

        # Convert magnitude to dB
        mag_db = 20 * np.log10(np.abs(self.magnitudes))

        try:
            self.graph.update_plot(self.freqs, mag_db)
            smoothed_magnitudes = apply_smoothing(
                self.freqs,
                mag_db,
                self.smoothing_options.smoothing_method.currentText(),
                self.smoothing_options.smoothing_window.value(),
                self.update_progress
            )
            self.graph.add_smoothed_data(self.freqs, smoothed_magnitudes)
        finally:
            self.close_progress_dialog()