from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QObject, pyqtSlot, QUrl, QTimer
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
            ),
            margin=dict(l=50, r=50, t=50, b=50),  # Add some margin
            autosize=True  # Enable auto-sizing
        )
        return fig
    
    @pyqtSlot(str, str, result=str)
    def add_target_curve(self, freqs, magnitudes):
        freqs = json.loads(freqs)
        magnitudes = json.loads(magnitudes)
        with self.fig.batch_update():
            self.fig.add_trace(go.Scatter(
                x=freqs,
                y=magnitudes,
                mode='lines',
                name='Target Curve',
                line=dict(color='red', dash='dash')
            ))
        return json.dumps(self.fig.to_dict())

    @pyqtSlot(str, str, result=str)
    def add_difference_curve(self, freqs, difference):
        freqs = json.loads(freqs)
        difference = json.loads(difference)
        with self.fig.batch_update():
            self.fig.add_trace(go.Scatter(
                x=freqs,
                y=difference,
                mode='lines',
                name='Difference',
                line=dict(color='purple')
            ))
            self.fig.update_layout(
                yaxis2=dict(
                    title="Difference (dB)",
                    overlaying="y",
                    side="right"
                )
            )
        return json.dumps(self.fig.to_dict())

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

    @pyqtSlot(int, int, result=str)
    def resize_plot(self, width, height):
        with self.fig.batch_update():
            self.fig.update_layout(
                width=width,
                height=height
            )
        return json.dumps(self.fig.to_dict())

class FrequencyResponseGraph(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)  # Remove layout margins
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
            <style>
                body, html, #plot {
                    width: 100%;
                    height: 100%;
                    margin: 0;
                    padding: 0;
                }
            </style>
        </head>
        <body>
            <div id="plot"></div>
            <script>
                var bridge;
                new QWebChannel(qt.webChannelTransport, function (channel) {
                    bridge = channel.objects.bridge;
                    // Initialize the plot
                    bridge.get_initial_figure(function(fig) {
                        Plotly.newPlot('plot', JSON.parse(fig), {responsive: true});
                    });
                });

                function updatePlot(freqs, magnitudes) {
                    bridge.update_plot(JSON.stringify(freqs), JSON.stringify(magnitudes), function(fig) {
                        Plotly.react('plot', JSON.parse(fig), {responsive: true});
                    });
                }

                function addSmoothedData(freqs, magnitudes) {
                    bridge.add_smoothed_data(JSON.stringify(freqs), JSON.stringify(magnitudes), function(fig) {
                        Plotly.react('plot', JSON.parse(fig), {responsive: true});
                    });
                }

                function addTargetCurve(freqs, magnitudes) {
                    bridge.add_target_curve(JSON.stringify(freqs), JSON.stringify(magnitudes), function(fig) {
                        Plotly.react('plot', JSON.parse(fig), {responsive: true});
                    });
                }

                function addDifferenceCurve(freqs, difference) {
                    bridge.add_difference_curve(JSON.stringify(freqs), JSON.stringify(difference), function(fig) {
                        Plotly.react('plot', JSON.parse(fig), {responsive: true});
                    });
                }

                function resizePlot() {
                    var width = window.innerWidth;
                    var height = window.innerHeight;
                    bridge.resize_plot(width, height, function(fig) {
                        Plotly.react('plot', JSON.parse(fig), {responsive: true});
                    });
                }

                window.addEventListener('resize', resizePlot);
                // Initial resize
                resizePlot();
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

    def add_target_curve(self, freqs, magnitudes):
        freqs_list = freqs.tolist() if isinstance(freqs, np.ndarray) else list(freqs)
        magnitudes_list = magnitudes.tolist() if isinstance(magnitudes, np.ndarray) else list(magnitudes)
        js_code = f"addTargetCurve({json.dumps(freqs_list)}, {json.dumps(magnitudes_list)})"
        self.web_view.page().runJavaScript(js_code)

    def add_difference_curve(self, freqs, difference):
        freqs_list = freqs.tolist() if isinstance(freqs, np.ndarray) else list(freqs)
        difference_list = difference.tolist() if isinstance(difference, np.ndarray) else list(difference)
        js_code = f"addDifferenceCurve({json.dumps(freqs_list)}, {json.dumps(difference_list)})"
        self.web_view.page().runJavaScript(js_code)

    def clear_plot(self):
        self.web_view.page().runJavaScript("Plotly.purge('plot')")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Use a short timer to allow the layout to settle before resizing the plot
        self.resize_plot
        QTimer.singleShot(100, self.resize_plot)

    def resize_plot(self):
        size = self.web_view.size()
        self.web_view.page().runJavaScript(f"resizePlot({size.width()}, {size.height()})")