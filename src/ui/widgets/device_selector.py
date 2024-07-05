from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox
import sounddevice as sd

class DeviceSelector(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.input_devices = QComboBox()
        self.output_devices = QComboBox()

        layout.addWidget(QLabel("Input Device:"))
        layout.addWidget(self.input_devices)
        layout.addWidget(QLabel("Output Device:"))
        layout.addWidget(self.output_devices)

        self.populate_device_lists()

    def populate_device_lists(self):
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                self.input_devices.addItem(f"{device['name']}", i)
            if device['max_output_channels'] > 0:
                self.output_devices.addItem(f"{device['name']}", i)