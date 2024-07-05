from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QObject, pyqtSlot, QUrl
import json
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import numpy as np

class PlotlyBridge(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fig = self.create_initial_figure()

    def create_initial_figure(self):
        fig = make_subplots()
        fig.add_trace(go.Scatter(
            x=[20, 20000],  # Min and max frequency
            y=[0, 0],       # Initial flat line at 0 dB
            mode='lines',
            name='Frequency Response',
            fill='tozeroy'
        ))
        fig.add_trace(go.Scatter(
            x=[20, 20000],
            y=[0, 0],
            mode='lines',
            name='Smoothed Response',
            visible=False
        ))
        fig.update_layout(
            title='Frequency Response',
            xaxis_title='Frequency (Hz)',
            yaxis_title='Magnitude (dB)',
            xaxis_type='log',
            xaxis_range=[np.log10(20), np.log10(20000)],
            yaxis_range=[-60, 20],  # Typical range for audio measurements
            hovermode='closest',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        return fig

    @pyqtSlot(result=str)
    def get_initial_figure(self):
        return json.dumps(self.fig.to_dict())

    @pyqtSlot(str, str, result=str)
    def update_plot(self, freqs, magnitudes):
        freqs = json.loads(freqs)
        magnitudes = json.loads(magnitudes)
        with self.fig.batch_update():
            self.fig.data[0].x = freqs
            self.fig.data[0].y = magnitudes
        return json.dumps(self.fig.to_dict())

    @pyqtSlot(str, str, result=str)
    def add_smoothed_data(self, freqs, magnitudes):
        freqs = json.loads(freqs)
        magnitudes = json.loads(magnitudes)
        with self.fig.batch_update():
            self.fig.data[1].x = freqs
            self.fig.data[1].y = magnitudes
            self.fig.data[1].visible = True
        return json.dumps(self.fig.to_dict())

class FrequencyResponseGraph(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.web_view = QWebEngineView()
        self.layout.addWidget(self.web_view)

        self.channel = QWebChannel()
        self.bridge = PlotlyBridge()
        self.channel.registerObject('bridge', self.bridge)
        self.web_view.page().setWebChannel(self.channel)

        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
        </head>
        <body>
            <div id="plot"></div>
            <script>
                var bridge;
                new QWebChannel(qt.webChannelTransport, function (channel) {
                    bridge = channel.objects.bridge;
                    // Initialize the plot
                    bridge.get_initial_figure(function(fig) {
                        Plotly.newPlot('plot', JSON.parse(fig));
                    });
                });

                function updatePlot(freqs, magnitudes) {
                    bridge.update_plot(JSON.stringify(freqs), JSON.stringify(magnitudes), function(fig) {
                        Plotly.react('plot', JSON.parse(fig));
                    });
                }

                function addSmoothedData(freqs, magnitudes) {
                    bridge.add_smoothed_data(JSON.stringify(freqs), JSON.stringify(magnitudes), function(fig) {
                        Plotly.react('plot', JSON.parse(fig));
                    });
                }
            </script>
        </body>
        </html>
        """
        self.web_view.setHtml(html_content)

    def update_plot(self, freqs, magnitudes):
        freqs_list = freqs.tolist() if isinstance(freqs, np.ndarray) else list(freqs)
        magnitudes_list = magnitudes.tolist() if isinstance(magnitudes, np.ndarray) else list(magnitudes)
        js_code = f"updatePlot({json.dumps(freqs_list)}, {json.dumps(magnitudes_list)})"
        self.web_view.page().runJavaScript(js_code)

    def add_smoothed_data(self, freqs, magnitudes):
        freqs_list = freqs.tolist() if isinstance(freqs, np.ndarray) else list(freqs)
        magnitudes_list = magnitudes.tolist() if isinstance(magnitudes, np.ndarray) else list(magnitudes)
        js_code = f"addSmoothedData({json.dumps(freqs_list)}, {json.dumps(magnitudes_list)})"
        self.web_view.page().runJavaScript(js_code)

    def clear_plot(self):
        self.web_view.page().runJavaScript("Plotly.purge('plot')")