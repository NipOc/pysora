from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSpinBox, QDoubleSpinBox

class FrequencyInput(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.start_freq = QSpinBox()
        self.start_freq.setRange(20, 20000)
        self.start_freq.setValue(20)

        self.end_freq = QSpinBox()
        self.end_freq.setRange(20, 20000)
        self.end_freq.setValue(20000)

        self.duration = QDoubleSpinBox()
        self.duration.setRange(0.1, 10)
        self.duration.setValue(5)
        self.duration.setSingleStep(0.1)

        layout.addWidget(self.start_freq)
        layout.addWidget(self.end_freq)
        layout.addWidget(self.duration)