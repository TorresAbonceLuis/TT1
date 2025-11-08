# -*- coding: utf-8 -*-
# services/transcription.py
#
# Servicio de transcripción de piano usando CNN-LSTM
# Adaptado para backend con reporte de progreso

import os
import numpy as np
import keras
import pretty_midi as pm
import math
from typing import Tuple, List, Callable
import librosa
import scipy.signal as signal

# --- Parámetros del Modelo ---
SEQ_LEN = 100
N_MELS = 128
N_KEYS = 88
LOW_MIDI = 21
SR = 22050  # Sample rate
HOP_LENGTH = 512
N_FFT = 2048

# Parámetros para Chunking (evitar OOM)
CHUNK_SIZE_FRAMES = 10000
pad_width = SEQ_LEN // 2  # 50 frames

# Umbrales de detección
T_ONSETS = 0.15
T_FRAMES = 0.30

# Configuración del modelo
NOMBRE_MODELO_CAMPEON = "modelo.keras"
MODELO_CAMPEON_PATH = os.path.join("modelos", NOMBRE_MODELO_CAMPEON)


# --- Funciones de Preprocesamiento ---

def load_audio_mono(audio_path: str, sr: int = SR) -> Tuple[np.ndarray, int]:
    """Carga un archivo de audio en mono."""
    y, sr_loaded = librosa.load(audio_path, sr=sr, mono=True)
    return y.astype(np.float32), sr_loaded


def aplicar_filtro_paso_bajo(audio: np.ndarray, sr: int, corte_hz: int = 6000) -> np.ndarray:
    """Aplica un filtro Butterworth de paso bajo (5to orden)."""
    nyquist = sr * 0.5
    frecuencia_normalizada = corte_hz / nyquist
    b, a = signal.butter(N=5, Wn=frecuencia_normalizada, btype='low', analog=False)
    audio_filtrado = signal.filtfilt(b, a, audio)
    return audio_filtrado.astype(np.float32)


def extract_mel_spectrogram(y: np.ndarray, sr: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Extrae el Mel Spectrogram de un audio.
    Retorna: (features, frame_times)
        - features: shape (n_frames, n_mels)
        - frame_times: shape (n_frames,)
    """
    # Calcular mel spectrogram
    mel_spec = librosa.feature.melspectrogram(
        y=y,
        sr=sr,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH,
        n_mels=N_MELS,
        fmin=27.5,  # A0
        fmax=4186.0  # C8
    )
    
    # Convertir a dB
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
    
    # Transponer para tener forma (n_frames, n_mels)
    features = mel_spec_db.T
    
    # Calcular tiempos de cada frame
    frame_times = librosa.frames_to_time(
        np.arange(features.shape[0]),
        sr=sr,
        hop_length=HOP_LENGTH
    )
    
    return features.astype(np.float32), frame_times


# --- Funciones de Secuenciamiento y Predicción ---

def create_sequences(input_features: np.ndarray, start_idx: int, end_idx: int) -> np.ndarray:
    """Crea las secuencias de 100 frames para el chunk especificado."""
    
    # Padding global
    padded_input = np.pad(
        input_features,
        ((pad_width, pad_width), (0, 0)),
        mode='constant',
        constant_values=input_features.min()
    )
    
    # Crear secuencias solo para el rango [start_idx, end_idx)
    X_sequences = np.stack([
        padded_input[i : i + SEQ_LEN]
        for i in range(start_idx, end_idx)
    ], axis=0)
    
    return X_sequences


def run_inference_in_chunks(
    model: keras.Model,
    input_features: np.ndarray,
    progress_callback: Callable[[int, int, str], None] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Realiza la inferencia procesando la entrada en chunks para evitar OOM.
    
    Args:
        model: Modelo Keras cargado
        input_features: Features de entrada (n_frames, n_mels)
        progress_callback: Función para reportar progreso (chunk_actual, total_chunks, mensaje)
        
    Returns:
        (Y_onsets_full, Y_frames_full): Pianorolls binarios
    """
    total_frames = input_features.shape[0]
    
    Y_onsets_full = np.zeros((total_frames, N_KEYS), dtype=np.uint8)
    Y_frames_full = np.zeros((total_frames, N_KEYS), dtype=np.uint8)
    
    num_chunks = math.ceil(total_frames / CHUNK_SIZE_FRAMES)
    
    for i in range(num_chunks):
        start_idx = i * CHUNK_SIZE_FRAMES
        end_idx = min((i + 1) * CHUNK_SIZE_FRAMES, total_frames)
        
        # Reportar progreso
        if progress_callback:
            progress_callback(i + 1, num_chunks, f"Procesando bloque {i + 1}/{num_chunks}")
        
        # 1. Crear secuencias para el chunk actual
        X_sequences_chunk = create_sequences(input_features, start_idx, end_idx)
        
        # 2. Predicción
        P_onsets, P_frames = model.predict(X_sequences_chunk, batch_size=32, verbose=0)
        
        # 3. Alineación: Extraer solo la predicción del frame central (índice 50)
        center_idx = SEQ_LEN // 2
        P_onsets_chunk = P_onsets[:, center_idx, :]
        P_frames_chunk = P_frames[:, center_idx, :]
        
        # 4. Aplicar Umbrales
        Y_onsets_chunk = (P_onsets_chunk > T_ONSETS).astype(np.uint8)
        Y_frames_chunk = (P_frames_chunk > T_FRAMES).astype(np.uint8)
        
        # 5. Guardar los resultados del chunk en el array completo
        Y_onsets_full[start_idx:end_idx, :] = Y_onsets_chunk
        Y_frames_full[start_idx:end_idx, :] = Y_frames_chunk
        
        # 6. Limpieza de memoria (CRUCIAL para OOM)
        del X_sequences_chunk, P_onsets, P_frames, P_onsets_chunk, P_frames_chunk
    
    return Y_onsets_full, Y_frames_full


# --- Decodificación a MIDI ---

def decode_to_notes(
    Y_onsets: np.ndarray,
    Y_frames: np.ndarray,
    frame_times: np.ndarray
) -> pm.PrettyMIDI:
    """
    Decodifica los pianorolls binarios a una lista de notas PrettyMIDI.
    Aplica limpieza para ignorar notas muy cortas.
    """
    notes = []
    
    hop_t = frame_times[1] - frame_times[0] if len(frame_times) > 1 else 0.0
    MIN_NOTE_DURATION_FRAMES = 5
    
    for k in range(N_KEYS):
        pitch = LOW_MIDI + k
        is_note_on = False
        start_frame = -1
        
        for n in range(Y_frames.shape[0]):
            is_onset = Y_onsets[n, k] == 1
            is_frame_active = Y_frames[n, k] == 1
            
            # Note ON: Solo si detectamos un ONSET Y la nota no está encendida
            if is_onset and not is_note_on:
                is_note_on = True
                start_frame = n
            
            # Note OFF: Si la nota está encendida Y el frame YA NO está activo
            if is_note_on and (not is_frame_active):
                end_frame = n
                duration_frames = end_frame - start_frame
                
                if duration_frames >= MIN_NOTE_DURATION_FRAMES:
                    start_time = frame_times[start_frame]
                    end_time = frame_times[end_frame]
                    
                    notes.append(pm.Note(
                        velocity=80, pitch=pitch, start=start_time, end=end_time
                    ))
                
                is_note_on = False
                start_frame = -1
        
        # Cierre final (si la nota llegó al final del audio)
        if is_note_on and start_frame != -1 and (Y_frames.shape[0] - start_frame) >= MIN_NOTE_DURATION_FRAMES:
            start_time = frame_times[start_frame]
            end_time = frame_times[-1] + hop_t
            
            notes.append(pm.Note(
                velocity=80, pitch=pitch, start=start_time, end=end_time
            ))
    
    midi_obj = pm.PrettyMIDI()
    piano = pm.Instrument(program=pm.instrument_name_to_program('Acoustic Grand Piano'))
    piano.notes.extend(notes)
    midi_obj.instruments.append(piano)
    
    return midi_obj


# --- Función Principal de Transcripción ---

def transcribe_piano_audio(
    audio_path: str,
    output_midi_path: str,
    progress_callback: Callable[[int, str], None] = None
) -> dict:
    """
    Transcribe un archivo de audio de piano a MIDI.
    
    Args:
        audio_path: Ruta al archivo de audio
        output_midi_path: Ruta donde guardar el MIDI resultante
        progress_callback: Función para reportar progreso (porcentaje, mensaje)
        
    Returns:
        dict con información del resultado
    """
    
    # Verificar que existe el modelo
    if not os.path.exists(MODELO_CAMPEON_PATH):
        raise FileNotFoundError(f"No se encontró el modelo en: {MODELO_CAMPEON_PATH}")
    
    try:
        # 1. Cargar y Filtrar Audio (10%)
        if progress_callback:
            progress_callback(10, "Cargando y filtrando audio...")
        
        y_mono, sr_loaded = load_audio_mono(audio_path, sr=SR)
        y_filtered = aplicar_filtro_paso_bajo(y_mono, sr_loaded)
        
        # 2. Extraer Características (20%)
        if progress_callback:
            progress_callback(20, "Extrayendo características Mel Spectrogram...")
        
        X_features, frame_times = extract_mel_spectrogram(y_filtered, sr_loaded)
        total_frames = X_features.shape[0]
        
        # 3. Cargar Modelo (25%)
        if progress_callback:
            progress_callback(25, "Cargando modelo CNN-LSTM...")
        
        model = keras.models.load_model(MODELO_CAMPEON_PATH)
        
        # 4. Inferencia (25% - 85%)
        if progress_callback:
            progress_callback(30, "Iniciando inferencia del modelo...")
        
        def chunk_progress_callback(chunk_num, total_chunks, msg):
            # Mapear progreso de chunks a 30-85%
            progress = 30 + int((chunk_num / total_chunks) * 55)
            if progress_callback:
                progress_callback(progress, msg)
        
        Y_onsets, Y_frames = run_inference_in_chunks(
            model, X_features, chunk_progress_callback
        )
        
        # 5. Decodificación a MIDI (90%)
        if progress_callback:
            progress_callback(90, "Decodificando a formato MIDI...")
        
        midi_predicho = decode_to_notes(Y_onsets, Y_frames, frame_times)
        
        # 6. Guardar MIDI (95%)
        if progress_callback:
            progress_callback(95, "Guardando archivo MIDI...")
        
        midi_predicho.write(output_midi_path)
        
        # 7. Completado (100%)
        if progress_callback:
            progress_callback(100, "Transcripción completada")
        
        return {
            "success": True,
            "midi_path": output_midi_path,
            "total_frames": total_frames,
            "duration_seconds": float(frame_times[-1]),
            "total_notes": len(midi_predicho.instruments[0].notes)
        }
        
    except Exception as e:
        raise Exception(f"Error en la transcripción: {str(e)}")
