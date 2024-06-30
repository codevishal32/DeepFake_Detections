import os
import librosa
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
import joblib


class AudioAnalyzer:
    def __init__(self):
        self.model_filename = "audio_model/svm_model.pkl"
        self.scaler_filename = "audio_model/scaler.pkl"
        self.scaler = joblib.load(self.scaler_filename)
        self.svm_classifier = joblib.load(self.model_filename)

    def extract_mfcc_feature(self, audio_path, n_mfcc=13, n_fft=2048, hop_length=512):
        try:
            audio_data, sr = librosa.load(audio_path, sr=None)
        except Exception as e:
            print(f"Error loading audio file {audio_path}: {e}")
            return None

        mfccs = librosa.feature.mfcc(
            y=audio_data, sr=sr, n_mfcc=n_mfcc, n_fft=n_fft, hop_length=hop_length
        )
        return np.mean(mfccs.T, axis=0)

    def analyze_audio(self, input_audio_path):
        if not os.path.exists(input_audio_path):
            return "Error: The specified file does not exist."
        elif not input_audio_path.lower().endswith(".wav"):
            return "Error: The specified file is not a .wav file."

        mfcc_feature = self.extract_mfcc_feature(input_audio_path)
        if mfcc_feature is not None:
            mfcc_feature_scaled = self.scaler.transform(mfcc_feature.reshape(1, -1))
            prediction = self.svm_classifier.predict(mfcc_feature_scaled)

            if prediction[0] == 0:
                return "real"
            else:
                return "fake"
        else:
            return "Error: Unable to process the input audio."