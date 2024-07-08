import numpy as np
from scipy import interpolate
from typing import List, Tuple
import json

class CurveOperations:
    @staticmethod
    def load_target_curve(file_path: str) -> Tuple[np.ndarray, np.ndarray, dict]:
        """
        Load a target curve from a JSON file.
        
        :param file_path: Path to the JSON file containing the target curve
        :return: Tuple of frequency array, magnitude array, and metadata dictionary
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        freqs = np.array(data['frequencies'])
        magnitudes = np.array(data['magnitudes'])
        metadata = data.get('metadata', {})
        return freqs, magnitudes, metadata

    @staticmethod
    def save_measurement(file_path: str, freqs: np.ndarray, magnitudes: np.ndarray, metadata: dict):
        """
        Save the current measurement to a JSON file.
        
        :param file_path: Path to save the JSON file
        :param freqs: Array of frequencies
        :param magnitudes: Array of magnitude values
        :param metadata: Dictionary containing metadata about the measurement
        """
        data = {
            'frequencies': freqs.tolist(),
            'magnitudes': magnitudes.tolist(),
            'metadata': metadata
        }
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def compare_to_target(measured_freqs: np.ndarray, measured_mags: np.ndarray, 
                          target_freqs: np.ndarray, target_mags: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compare the measured response to the target curve.
        
        :param measured_freqs: Frequencies of the measured response
        :param measured_mags: Magnitudes of the measured response
        :param target_freqs: Frequencies of the target curve
        :param target_mags: Magnitudes of the target curve
        :return: Tuple of frequencies and difference in magnitudes
        """
        # Interpolate the target curve to match the measured frequencies
        interp_func = interpolate.interp1d(target_freqs, target_mags, kind='linear', fill_value='extrapolate')
        interpolated_target_mags = interp_func(measured_freqs)
        
        # Calculate the difference
        difference = measured_mags - interpolated_target_mags
        
        return measured_freqs, difference

    @staticmethod
    def check_pass_fail(difference: np.ndarray, tolerance: float) -> bool:
        """
        Check if the measurement passes or fails based on the difference from the target curve.
        
        :param difference: Array of differences between measured and target magnitudes
        :param tolerance: Maximum allowed deviation in dB
        :return: True if passed, False if failed
        """
        return np.all(np.abs(difference) <= tolerance)