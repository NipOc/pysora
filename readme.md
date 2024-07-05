# Sound Output Response Analyzer

This application measures and visualizes the frequency response of audio devices (speakers or microphones) using a swept sine technique.

## Features

- Real-time audio analysis
- Configurable frequency range and sweep duration
- Multiple smoothing options for the frequency response graph
- Low-latency audio I/O
- Cross-platform compatibility (Windows, macOS, Linux)

## Requirements

- Python 3.7 or higher
- PyQt6
- NumPy
- SciPy
- Matplotlib
- SoundDevice

## Installation

1. Clone this repository:

   ```cmd
   git clone https://github.com/yourusername/audio-frequency-response-analyzer.git
   cd audio-frequency-response-analyzer
   ```

2. Create a virtual environment (optional but recommended):

   ```cmd
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:

   ```cmd
   pip install -r requirements.txt
   ```

## Usage

Run the application with:

```cmd
python src/main.py
```

1. Select input and output devices from the dropdown menus.
2. Set the desired start frequency, end frequency, and sweep duration.
3. Choose a smoothing method and window size if desired.
4. Click "Run Test" to start the analysis.
5. The frequency response graph will be displayed, and the audio delay will be shown.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
