import numpy as np
import librosa
import soundfile as sf
from scipy import signal
import pickle
import os
from datetime import datetime
import threading
import queue
import noisereduce as nr

class AdvancedAcousticDetector:
    def __init__(self, sensor_id="sensor_01", location="unknown", sampling_rate=44100):
        """
        Initialize advanced acoustic sensor for mining activity detection
        """
        self.sensor_id = sensor_id
        self.location = location
        self.sampling_rate = sampling_rate
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.use_deep_audio = True
        
        # Frequency ranges for mining equipment
        self.equipment_freq_ranges = {
            'excavator': (50, 200),
            'drill': (500, 2000),
            'conveyor': (20, 100),
            'generator': (100, 400)
        }
        
    def denoise_audio(self, audio):
        """Remove environmental noise using spectral gating"""
        reduced_noise = nr.reduce_noise(
            y=audio, 
            sr=self.sampling_rate,
            prop_decrease=0.8
        )
        return reduced_noise

    def extract_deep_features(self, audio):
        """Use pretrained YAMNet model for feature extraction"""
        try:
            import tensorflow_hub as hub
            # Note: In a real environment, this would load from a local cache or URL
            # For this implementation, we assume hub is available or handle the absence
            yamnet = hub.load('https://tfhub.dev/google/yamnet/1')
            scores, embeddings, spectrogram = yamnet(audio)
            return embeddings.numpy()
        except Exception as e:
            print(f"Deep feature extraction failed: {e}. Falling back to MFCC.")
            return self.extract_mfcc_features(audio)

    def extract_mfcc_features(self, audio_data):
        """Extract standard acoustic features as fallback"""
        mfccs = librosa.feature.mfcc(y=audio_data, sr=self.sampling_rate, n_mfcc=13)
        return np.mean(mfccs, axis=1)

    def detect_equipment(self, audio_data, duration):
        """Detect equipment bands in spectrogram"""
        detections = []
        # Spectral analysis
        frequencies, times, Sxx = signal.spectrogram(audio_data, fs=self.sampling_rate)
        
        for equipment, (low_freq, high_freq) in self.equipment_freq_ranges.items():
            freq_mask = (frequencies >= low_freq) & (frequencies <= high_freq)
            if np.any(freq_mask):
                band_energy = np.sum(Sxx[freq_mask, :], axis=0)
                threshold = np.mean(band_energy) + 2 * np.std(band_energy)
                
                # Check for sustained activity
                samples_per_second = len(band_energy) / duration
                min_samples = int(5 * samples_per_second)
                
                sustained = False
                for i in range(len(band_energy) - min_samples):
                    if np.all(band_energy[i:i+min_samples] > threshold):
                        sustained = True
                        break
                
                if sustained:
                    detections.append({
                        'equipment': equipment,
                        'confidence': float(np.mean(band_energy) / np.max(band_energy)),
                        'timestamp': datetime.now().isoformat()
                    })
        return detections

    def process_chunk(self, audio_chunk, duration=10):
        """Full processing pipeline for an audio chunk"""
        denoised = self.denoise_audio(audio_chunk)
        features = self.extract_deep_features(denoised)
        equipment = self.detect_equipment(denoised, duration)
        
        return {
            'features': features,
            'equipment': equipment,
            'status': 'success'
        }
