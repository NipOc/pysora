import numpy as np
from scipy.signal import savgol_filter
from scipy.ndimage import gaussian_filter1d

def erb_bandwidth(center_freq):
    return 24.7 * (4.37 * center_freq / 1000 + 1)

def apply_smoothing(freqs, magnitudes, method, window, progress_callback=None):
    if method == "None":
        return magnitudes
    elif method == "Moving Average":
        return np.convolve(magnitudes, np.ones(window)/window, mode='same')
    elif method == "Savitzky-Golay":
        return savgol_filter(magnitudes, window, 3)
    elif method == "Gaussian":
        return gaussian_filter1d(magnitudes, window/5)
    elif method == "ERB":
        return erb_smoothing(freqs, magnitudes, progress_callback)
    else:
        raise ValueError(f"Unknown smoothing method: {method}")

def erb_smoothing(freqs, magnitudes, progress_callback=None):
    smoothed = np.zeros_like(magnitudes)
    total_steps = len(freqs)
    for i, freq in enumerate(freqs):
        erb = erb_bandwidth(freq)
        lower = freq - erb / 2
        upper = freq + erb / 2
        mask = (freqs >= lower) & (freqs <= upper)
        if np.sum(mask) > 0:
            smoothed[i] = np.mean(magnitudes[mask])
        else:
            smoothed[i] = magnitudes[i]
        
        if progress_callback and i % (total_steps // 100) == 0:
            progress_callback(int(100 * i / total_steps))
    
    if progress_callback:
        progress_callback(100)
    
    return smoothed