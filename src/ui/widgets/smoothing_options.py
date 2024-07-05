from PyQt6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QSpinBox

class SmoothingOptions(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.smoothing_method = QComboBox()
        self.smoothing_method.addItems(["None", "Moving Average", "Savitzky-Golay", "Gaussian", "ERB"])

        self.smoothing_window = QSpinBox()
        self.smoothing_window.setRange(3, 101)
        self.smoothing_window.setValue(11)
        self.smoothing_window.setSingleStep(2)

        layout.addWidget(self.smoothing_method)
        layout.addWidget(self.smoothing_window)

        self.smoothing_method.currentIndexChanged.connect(self.update_window_settings)
        self.update_window_settings()

    def update_window_settings(self):
        method = self.smoothing_method.currentText()
        if method in ["None", "ERB"]:
            self.smoothing_window.setEnabled(False)
        else:
            self.smoothing_window.setEnabled(True)

        if method == "Savitzky-Golay":
            self.smoothing_window.setRange(5, 101)
            self.smoothing_window.setSingleStep(2)
            if self.smoothing_window.value() % 2 == 0:
                self.smoothing_window.setValue(self.smoothing_window.value() + 1)
        elif method in ["Moving Average", "Gaussian"]:
            self.smoothing_window.setRange(3, 101)
            self.smoothing_window.setSingleStep(2)