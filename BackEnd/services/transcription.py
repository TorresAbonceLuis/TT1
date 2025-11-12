# -*- coding: utf-8 -*-
# services/transcription.py (VERSIÓN FINAL CORREGIDA)
#
# Objetivo: Garantizar la coherencia de pre-procesamiento (normalización) 
# y la carga del modelo para igualar el rendimiento de la consola.

import os
import numpy as np
import keras
import pretty_midi as pm
import math
from typing import Tuple, List

# Importamos librosa y scipy para el procesamiento de audio
import librosa
import scipy.signal as signal 

# --- Parámetros del Modelo ---
SEQ_LEN = 100
N_MELS_FEATURE = 128  # Base para el cálculo de Mel
N_MELS_MODELO = 384   # 128 * 3 (Mel + Delta + Delta-Delta)
N_KEYS = 88
LOW_MIDI = 21
SR = 22050
HOP_LENGTH = 512
N_FFT = 2048
F_MIN = 25.0
F_MAX = 6000.0

# Parámetros para Chunking
CHUNK_SIZE_FRAMES = 10000
pad_width = SEQ_LEN // 2

# Umbrales de detección (Óptimos según tu último entrenamiento)
T_ONSETS = 0.35
T_FRAMES = 0.40

# Configuración del modelo
NOMBRE_MODELO_CAMPEON = "modelo.keras" 
MODELO_CAMPEON_PATH = os.path.join("modelos", NOMBRE_MODELO_CAMPEON)


# --- Funciones de Preprocesamiento ---

def load_audio_mono(audio_path: str, sr: int = SR) -> Tuple[np.ndarray, int]:
    """Carga un archivo de audio en mono y normaliza el peak."""
    y, sr_loaded = librosa.load(audio_path, sr=sr, mono=True)
    peak = np.max(np.abs(y)) if y.size else 1.0
    if peak > 0:
        y = y / peak
    return y.astype(np.float32), sr_loaded


def aplicar_filtro_paso_bajo(y: np.ndarray, sr: int, corte_hz: int = 6000) -> np.ndarray:
    """
    Aplica un filtro paso bajo a un array de audio en memoria.
    (Basado en 1limpiarAudio.py - Consistencia con entrenamiento)
    """
    nyquist = sr * 0.5
    frecuencia_normalizada = corte_hz / nyquist
    
    # Crear filtro Butterworth (orden N=5)
    b, a = signal.butter(
        N=5,
        Wn=frecuencia_normalizada,
        btype='low',
        analog=False
    )
    
    # Aplicar el filtro
    audio_filtrado = signal.filtfilt(b, a, y)
    return audio_filtrado.astype(np.float32)


def extract_mel_spectrogram(y: np.ndarray, sr: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calcula el Mel Spectrogram logarítmico (en dB) + Delta + Delta-Delta.
    Exactamente como en el pipeline de entrenamiento.
    """
    # 1. Calcular el Mel Spectrogram (Potencia)
    S = librosa.feature.melspectrogram(
        y=y,
        sr=sr,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH,
        n_mels=N_MELS_FEATURE,
        fmin=F_MIN,
        fmax=F_MAX
    )
    
    # 2. Convertir a Decibelios
    S_db = librosa.power_to_db(S, ref=np.max)
    
    # 3. Calcular Delta (Velocidad) y Delta-Delta (Aceleración)
    S_delta = librosa.feature.delta(S_db)
    S_delta2 = librosa.feature.delta(S_db, order=2)
    
    # 4. Concatenar las 3 matrices
    S_full = np.concatenate((S_db, S_delta, S_delta2), axis=0)

    # 5. Transponer a (n_frames, 3 * n_mels) = (n_frames, 384)
    X = S_full.T
    
    # 6. Generar los tiempos de frame
    frame_times = librosa.frames_to_time(
        np.arange(X.shape[0]), 
        sr=sr, 
        hop_length=HOP_LENGTH
    )
    
    # 7. Normalizar los datos
    X = (X / 80.0) + 1.0 
    
    return X.astype(np.float32), frame_times


# --- Función de Predicción con Ventanas Deslizantes ---

def run_inference_with_sliding_window(
    model: keras.Model,
    input_features: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Realiza la inferencia usando ventanas deslizantes, igual que en 6inferencia.py.
    """
    total_frames = input_features.shape[0]
    
    # 1. Añadir padding al inicio y fin para centrar las ventanas
    X_padded = np.pad(input_features, ((pad_width, pad_width), (0, 0)), 'constant')
    
    # 2. Crear el dataset de ventanas deslizantes usando Keras
    dataset = keras.utils.timeseries_dataset_from_array(
        data=X_padded,
        targets=None,
        sequence_length=SEQ_LEN,
        sequence_stride=1,      # Una ventana por cada frame
        batch_size=64           # Ajusta según memoria disponible
    )
    
    # 3. Obtener predicciones
    # La salida tendrá forma (total_frames + padding, 100, 88)
    P_onsets_full, P_frames_full = model.predict(dataset, verbose=0)
    
    # 4. Extraer solo la predicción del frame central (índice 50)
    P_onsets_all = P_onsets_full[:, pad_width, :]
    P_frames_all = P_frames_full[:, pad_width, :]

    # 5. Truncar predicciones al tamaño original de frames
    P_onsets_flat = P_onsets_all[:total_frames]
    P_frames_flat = P_frames_all[:total_frames]
    
    # 6. Aplicar Umbrales
    Y_onsets_binary = (P_onsets_flat > T_ONSETS).astype(np.uint8)
    Y_frames_binary = (P_frames_flat > T_FRAMES).astype(np.uint8)
    
    return Y_onsets_binary, Y_frames_binary


# --- Decodificación a MIDI ---

def piano_roll_to_midi(
    P_onsets_binary: np.ndarray,
    P_frames_binary: np.ndarray,
    frame_times: np.ndarray
) -> pm.PrettyMIDI:
    """
    Convierte los piano rolls binarios (Onsets y Frames) en un objeto PrettyMIDI.
    Usa Onsets para INICIAR notas y Frames para SOSTENER/TERMINAR notas.
    Exactamente como en 6inferencia.py
    """
    n_frames, n_keys = P_frames_binary.shape
    hop_duration_s = HOP_LENGTH / SR
    
    pm_obj = pm.PrettyMIDI()
    instrument = pm.Instrument(program=0, name="Piano (Transcripción)")
    
    for k in range(n_keys):
        pitch = LOW_MIDI + k
        note_active = False
        start_time = 0.0
        
        for frame_idx in range(n_frames):
            frame_time = frame_times[frame_idx]
            is_onset = P_onsets_binary[frame_idx, k] == 1
            is_active = P_frames_binary[frame_idx, k] == 1
            
            # Caso 1: Inicia una nota (Hay onset y no hay nota activa)
            if is_onset and not note_active:
                note_active = True
                start_time = frame_time
            
            # Caso 2: Termina una nota (No hay frame activo y SÍ había nota activa)
            if not is_active and note_active:
                note_active = False
                end_time = frame_time
                # Evitar notas de duración cero
                if end_time > start_time:
                    note = pm.Note(velocity=100, pitch=pitch, start=start_time, end=end_time)
                    instrument.notes.append(note)

        # Caso 3: La nota estaba activa hasta el final del audio
        if note_active:
            end_time = frame_times[-1] + hop_duration_s
            if end_time > start_time:
                note = pm.Note(velocity=100, pitch=pitch, start=start_time, end=end_time)
                instrument.notes.append(note)
                
    pm_obj.instruments.append(instrument)
    return pm_obj


# --- Función Principal de Transcripción (Síncrona) ---

def transcribe_piano_audio(
    audio_path: str,
    output_midi_path: str
) -> dict:
    """
    Transcribe un archivo de audio de piano a MIDI.
    """
    
    if not os.path.exists(MODELO_CAMPEON_PATH):
        # NOTA: En la web, esto puede fallar si la ruta es relativa.
        raise FileNotFoundError(f"No se encontró el modelo en: {MODELO_CAMPEON_PATH}")
    
    try:
        # 1. Cargar Audio
        y_mono, sr_loaded = load_audio_mono(audio_path, sr=SR)
        
        # 2. Aplicar filtro paso bajo (para consistencia con entrenamiento)
        y_filtrado = aplicar_filtro_paso_bajo(y_mono, sr_loaded, corte_hz=F_MAX)
        
        # 3. Extraer Características (Mel + Delta + Delta-Delta + NORMALIZADAS)
        X_features, frame_times = extract_mel_spectrogram(y_filtrado, sr_loaded)
        total_frames = X_features.shape[0]
        
        # 4. Cargar Modelo
        model = keras.models.load_model(MODELO_CAMPEON_PATH)
        
        # 5. Inferencia (usando ventanas deslizantes, como en 6inferencia.py)
        Y_onsets, Y_frames = run_inference_with_sliding_window(model, X_features)
        
        # 6. Decodificación a MIDI
        midi_predicho = piano_roll_to_midi(Y_onsets, Y_frames, frame_times)
        
        # 7. Guardar MIDI
        midi_predicho.write(output_midi_path)
        
        return {
            "success": True,
            "midi_path": output_midi_path,
            "total_frames": total_frames,
            "duration_seconds": float(frame_times[-1]),
            "total_notes": len(midi_predicho.instruments[0].notes)
        }
        
    except Exception as e:
        # En producción, usa logging.error(e)
        raise Exception(f"Error en la transcripción: {str(e)}")