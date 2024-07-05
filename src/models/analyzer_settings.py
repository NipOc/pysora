class AnalyzerSettings:
    def __init__(self, start_freq, end_freq, duration, sample_rate, buffer_size):
        self.start_freq = start_freq
        self.end_freq = end_freq
        self.duration = duration
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size