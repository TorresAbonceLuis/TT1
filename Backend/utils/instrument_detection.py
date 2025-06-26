import wave
import math
import struct
import numpy as np

def read_wav(file_path):
    """Lee un archivo WAV y devuelve los datos de audio y la tasa de muestreo"""
    with wave.open(file_path, 'rb') as wav_file:
        n_channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        framerate = wav_file.getframerate()
        n_frames = wav_file.getnframes()
        frames = wav_file.readframes(n_frames)
        
        # Convertir los datos binarios a valores numéricos
        if sample_width == 1:
            fmt = f"{n_frames * n_channels}b"  # 8-bit signed
        elif sample_width == 2:
            fmt = f"{n_frames * n_channels}h"  # 16-bit signed
        else:
            raise ValueError("Solo soportamos archivos WAV de 8 o 16 bits")
            
        samples = struct.unpack(fmt, frames)
        
        # Si es estéreo, promediar los canales
        if n_channels == 2:
            samples = [(samples[i] + samples[i+1])/2 for i in range(0, len(samples), 2)]
            
        return samples, framerate

def compute_fft(samples, framerate):
    """Calcula la FFT y devuelve las frecuencias y magnitudes"""
    n = len(samples)
    fft_result = np.fft.fft(samples)
    magnitudes = np.abs(fft_result)[:n//2] * 2 / n
    frequencies = np.fft.fftfreq(n, 1/framerate)[:n//2]
    return frequencies, magnitudes

def analyze_instrument(file_path):
    """Analiza el archivo de audio para determinar el instrumento y frecuencia"""
    samples, framerate = read_wav(file_path)
    
    # Calcular la envolvente del sonido
    envelope = [abs(s) for s in samples]
    
    # Calcular estadísticas de la envolvente
    attack_time = len(envelope) // 10  # Tiempo de ataque (primer 10%)
    attack_slope = (max(envelope[:attack_time]) - envelope[0]) / attack_time
    
    # Calcular FFT
    frequencies, magnitudes = compute_fft(samples, framerate)
    
    # Encontrar la frecuencia fundamental
    fundamental_idx = np.argmax(magnitudes)
    fundamental_freq = frequencies[fundamental_idx]
    
    # Determinar el instrumento
    is_flute = (
        attack_slope < 0.01 and 
        max(magnitudes) / np.mean(magnitudes) > 10
    )
    
    return {
        "instrument": "Flauta" if is_flute else "Piano",
        "frequency": fundamental_freq  # Frecuencia en Hz
    }