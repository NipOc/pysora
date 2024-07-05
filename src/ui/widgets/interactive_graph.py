from PyQt6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg
import numpy as np

class InteractiveGraph(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create a PlotWidget
        self.plot_widget = pg.PlotWidget()
        layout.addWidget(self.plot_widget)
        
        # Set up the plot
        self.plot_widget.setBackground('w')
        self.plot_widget.setLogMode(x=True, y=False)
        self.plot_widget.setLabel('left', 'Magnitude', units='dB')
        self.plot_widget.setLabel('bottom', 'Frequency', units='Hz')
        self.plot_widget.showGrid(x=True, y=True)
        
        # Create a PlotDataItem for the frequency response curve
        self.curve = self.plot_widget.plot(pen='b')
        
        # Add legend
        self.legend = self.plot_widget.addLegend()
        self.legend.addItem(self.curve, 'Frequency Response')

    def update_plot(self, freqs, magnitudes):
        self.curve.setData(freqs, magnitudes)
        self.plot_widget.setXRange(min(freqs), max(freqs))
        self.plot_widget.setYRange(min(magnitudes), max(magnitudes))

    def clear_plot(self):
        self.curve.clear()

    def set_title(self, title):
        self.plot_widget.setTitle(title)

    def enable_auto_range(self):
        self.plot_widget.enableAutoRange()

    def disable_auto_range(self):
        self.plot_widget.disableAutoRange()

    def add_region(self, xmin, xmax, color):
        region = pg.LinearRegionItem([xmin, xmax], brush=color)
        self.plot_widget.addItem(region)
        return region

    def remove_region(self, region):
        self.plot_widget.removeItem(region)