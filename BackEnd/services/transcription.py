# -*- coding: utf-8 -*-
# services/transcription.py
#
# SERVICIO DE TRANSCRIPCIÓN DE PIANO (VERSION GOLD)
#
# Características Fusionadas:
# 1. Seguridad: Carga de pesos con 'build_modelo_definitivo' (Fix Lambda).
# 2. Eficiencia: Sliding Window View + GPU Memory Growth.
# 3. Robustez: Filtro Nyquist seguro + Ordenamiento MIDI.
# 4. Feedback: Reporte de notas descartadas y logs detallados.

import os
import sys
import numpy as np
import librosa
import pretty_midi
from scipy.signal import butter, sosfilt
import time
import gc
import tensorflow as tf
from typing import Dict, List, Tuple, Optional

# Configurar GPU para uso eficiente de memoria
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print(f"✅ GPU configurada: {len(gpus)} dispositivo(s)")
    except RuntimeError as e:
        print(f"⚠️ Error configurando GPU: {e}")

# Importar arquitectura y parámetros del modelo
try:
    from modelos.modelo_definitivo import build_modelo_definitivo, SEQ_LEN, N_MELS, N_KEYS
    print(f"✅ Modelo importado: SEQ_LEN={SEQ_LEN}, N_MELS={N_MELS}, N_KEYS={N_KEYS}")
except ImportError as e:
    print(f"❌ ERROR: No se pudo importar modelo_definitivo.py - {e}")
    raise

# Importar configuración
from config import settings

# Variable global para cache del modelo (evitar recargar en cada petición)
_cached_model = None
_cached_model_path = None


def get_model():
    """
    Obtiene el modelo de transcripción (con cache para eficiencia).
    Si ya está cargado, retorna la instancia en caché.
    """
    global _cached_model, _cached_model_path
    
    model_path = settings.MODEL_PATH
    
    # Si el modelo ya está en caché y no ha cambiado la ruta, retornarlo
    if _cached_model is not None and _cached_model_path == model_path:
        print(f"♻️ Usando modelo en caché")
        return _cached_model
    
    # Validar que exista el archivo de pesos
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Modelo no encontrado: {model_path}")
    
    print(f"🔧 Cargando modelo desde: {model_path}")
    
    # Construir arquitectura
    model = build_modelo_definitivo(seq_len=SEQ_LEN, n_mels=N_MELS, n_keys=N_KEYS)
    
    # Cargar pesos
    model.load_weights(model_path)
    print(f"✅ Pesos cargados exitosamente")
    
    # Guardar en caché
    _cached_model = model
    _cached_model_path = model_path
    
    return model


# ===================================================================
# ========= PROCESAMIENTO DE SEÑAL =================================
# ===================================================================

def butter_bandpass_filter(y: np.ndarray, lowcut: float, highcut: float, 
                          sr: int, order: int = 5) -> np.ndarray:
    """
    Aplica un filtro pasabanda Butterworth a la señal de audio.
    Incluye protección contra errores de Nyquist.
    
    Args:
        y: Señal de audio
        lowcut: Frecuencia de corte inferior (Hz)
        highcut: Frecuencia de corte superior (Hz)
        sr: Sample rate
        order: Orden del filtro
        
    Returns:
        Señal filtrada y normalizada
    """
    nyq = 0.5 * sr
    low = max(0.001, lowcut / nyq)
    high = min(0.999999, highcut / nyq)  # Protección Nyquist
    
    if low >= high:
        raise ValueError(f"Filtro inválido: low={low}, high={high}")
    
    sos = butter(order, [low, high], btype='band', output='sos')
    filtered = sosfilt(sos, y.astype(np.float32))
    
    return librosa.util.normalize(filtered)


def load_and_prep_audio(path: str) -> np.ndarray:
    """
    Carga y preprocesa el archivo de audio.
    
    Args:
        path: Ruta al archivo WAV
        
    Returns:
        Señal de audio procesada
    """
    print(f"🎵 Cargando audio: {os.path.basename(path)}")
    
    try:
        # Cargar audio con el sample rate del modelo
        y, _ = librosa.load(path, sr=settings.SAMPLE_RATE, mono=True)
        
        # Aplicar filtro pasabanda
        y = butter_bandpass_filter(
            y, 
            settings.LOW_CUT, 
            settings.HIGH_CUT, 
            settings.SAMPLE_RATE, 
            settings.FILTER_ORDER
        )
        
        print(f"   ✅ Audio cargado: {len(y)/settings.SAMPLE_RATE:.2f}s")
        return y
        
    except Exception as e:
        print(f"❌ Error cargando audio: {e}")
        raise


def compute_spectrogram(y: np.ndarray) -> np.ndarray:
    """
    Calcula el espectrograma mel del audio.
    
    Args:
        y: Señal de audio
        
    Returns:
        Espectrograma mel normalizado (frames, n_mels)
    """
    print(f"📊 Calculando espectrograma mel...")
    
    # Calcular espectrograma mel
    S = librosa.feature.melspectrogram(
        y=y,
        sr=settings.SAMPLE_RATE,
        n_fft=settings.N_FFT,
        hop_length=settings.HOP_LENGTH,
        n_mels=settings.N_MELS,
        fmin=settings.F_MIN,
        fmax=settings.F_MAX
    )
    
    # Convertir a dB
    S_db = librosa.power_to_db(S, ref=np.max)
    
    # Normalizar a rango [0, 1] aproximadamente
    # (espectrograma típico: -80 dB a 0 dB)
    S_normalized = ((S_db.T / 80.0) + 1.0).astype(np.float32)
    
    print(f"   ✅ Espectrograma: {S_normalized.shape[0]} frames")
    return S_normalized


# ===================================================================
# ========= DECODIFICACIÓN (CON REPORTE DE ESTADÍSTICAS) ===========
# ===================================================================

def predictions_to_notes(p_onsets: np.ndarray, p_frames: np.ndarray, 
                        n_frames: int) -> List[Tuple[int, float, float]]:
    """
    Convierte las predicciones del modelo a una lista de notas MIDI.
    
    Args:
        p_onsets: Predicciones de onsets (n_frames, n_keys)
        p_frames: Predicciones de frames (n_frames, n_keys)
        n_frames: Número de frames a procesar
        
    Returns:
        Lista de tuplas (pitch_midi, start_time, end_time)
    """
    print(f"🎼 Decodificando notas...")
    print(f"   Umbrales: Onsets>{settings.UMBRAL_ONSETS}, Frames>{settings.UMBRAL_FRAMES}")
    
    frame_dur = settings.HOP_LENGTH / settings.SAMPLE_RATE
    
    # Aplicar umbrales
    b_onsets = (p_onsets > settings.UMBRAL_ONSETS)
    b_frames = (p_frames > settings.UMBRAL_FRAMES)
    
    # Estado de las notas
    note_state = np.zeros(N_KEYS, dtype=bool)
    note_start = np.zeros(N_KEYS, dtype=int)
    notes = []
    discarded_count = 0
    
    # Procesar frame por frame
    for t in range(n_frames):
        for k in range(N_KEYS):
            is_onset = b_onsets[t, k]
            is_frame = b_frames[t, k]
            
            # Detectar onset (inicio de nota)
            if is_onset:
                # Si había una nota activa, cerrarla
                if note_state[k]:
                    start_t = note_start[k] * frame_dur
                    end_t = t * frame_dur
                    duration = end_t - start_t
                    
                    if duration >= settings.DURACION_MINIMA_S:
                        notes.append((k + settings.LOW_MIDI, start_t, end_t))
                    else:
                        discarded_count += 1
                
                # Iniciar nueva nota
                note_state[k] = True
                note_start[k] = t
            
            # Detectar offset (fin de nota)
            elif not is_frame and note_state[k]:
                start_t = note_start[k] * frame_dur
                end_t = t * frame_dur
                duration = end_t - start_t
                
                if duration >= settings.DURACION_MINIMA_S:
                    notes.append((k + settings.LOW_MIDI, start_t, end_t))
                else:
                    discarded_count += 1
                
                note_state[k] = False
    
    # Cerrar notas pendientes al final
    total_dur = n_frames * frame_dur
    for k in range(N_KEYS):
        if note_state[k]:
            start_t = note_start[k] * frame_dur
            duration = total_dur - start_t
            
            if duration >= settings.DURACION_MINIMA_S:
                notes.append((k + settings.LOW_MIDI, start_t, total_dur))
            else:
                discarded_count += 1
    
    # Ordenar notas cronológicamente (importante para MIDI)
    notes.sort(key=lambda x: x[1])
    
    print(f"   ✅ Notas detectadas: {len(notes)}")
    print(f"   ⚠️ Notas descartadas (ruido < {settings.DURACION_MINIMA_S*1000:.0f}ms): {discarded_count}")
    
    return notes


def save_midi(notes_list: List[Tuple[int, float, float]], output_path: str) -> Dict:
    """
    Guarda la lista de notas en un archivo MIDI.
    
    Args:
        notes_list: Lista de tuplas (pitch, start, end)
        output_path: Ruta donde guardar el MIDI
        
    Returns:
        Diccionario con información del MIDI generado
    """
    print(f"💾 Guardando MIDI...")
    
    # Crear objeto MIDI
    pm = pretty_midi.PrettyMIDI()
    piano = pretty_midi.Instrument(program=0)  # Acoustic Grand Piano
    
    # Agregar notas
    for pitch, start, end in notes_list:
        note = pretty_midi.Note(
            velocity=100,
            pitch=int(pitch),
            start=start,
            end=end
        )
        piano.notes.append(note)
    
    pm.instruments.append(piano)
    pm.write(output_path)
    
    # Calcular estadísticas
    total_duration = pm.get_end_time()
    note_density = len(notes_list) / total_duration if total_duration > 0 else 0
    
    # Obtener rango de notas
    if notes_list:
        pitches = [n[0] for n in notes_list]
        lowest_note = min(pitches)
        highest_note = max(pitches)
        pitch_range = highest_note - lowest_note
    else:
        lowest_note = highest_note = pitch_range = 0
    
    info = {
        "total_notes": len(notes_list),
        "duration_seconds": round(total_duration, 2),
        "note_density": round(note_density, 2),
        "lowest_note": int(lowest_note),
        "highest_note": int(highest_note),
        "pitch_range": int(pitch_range)
    }
    
    print(f"   ✅ MIDI guardado: {output_path}")
    print(f"   📊 Estadísticas: {info['total_notes']} notas, {info['duration_seconds']}s")
    
    return info


# ===================================================================
# ========= FUNCIÓN PRINCIPAL (API PARA EL BACKEND) =================
# ===================================================================

def transcribe_piano_audio(audio_path: str, output_midi_path: str) -> Dict:
    """
    Función principal de transcripción para el backend.
    
    Args:
        audio_path: Ruta al archivo de audio WAV
        output_midi_path: Ruta donde guardar el MIDI resultante
        
    Returns:
        Diccionario con información de la transcripción
    """
    print("="*60)
    print("🎹 INICIANDO TRANSCRIPCIÓN DE PIANO 🎹")
    print("="*60)
    
    t_start = time.time()
    
    try:
        # 1. Validar entrada
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Archivo de audio no encontrado: {audio_path}")
        
        # 2. Cargar y procesar audio
        y = load_and_prep_audio(audio_path)
        spectrogram = compute_spectrogram(y)
        n_frames = spectrogram.shape[0]
        
        # 3. Crear ventanas deslizantes (sliding window)
        print(f"🪟 Creando ventanas deslizantes...")
        pad_width = SEQ_LEN // 2
        padded_S = np.pad(spectrogram, ((pad_width, pad_width), (0, 0)), mode='constant')
        
        # Usar stride tricks para eficiencia
        windows = np.lib.stride_tricks.sliding_window_view(
            padded_S, (SEQ_LEN, N_MELS)
        )[:, 0, :, :]
        windows = windows[:n_frames]
        
        print(f"   ✅ Ventanas creadas: {len(windows)}")
        
        # 4. Cargar modelo
        model = get_model()
        
        # 5. Inferencia
        print(f"🔮 Ejecutando inferencia...")
        preds = model.predict(windows, batch_size=settings.INFER_BATCH_SIZE, verbose=0)
        
        # Manejar diferentes formatos de salida
        if isinstance(preds, list):
            p_onsets, p_frames = preds[0], preds[1]
        else:
            p_onsets = preds['output_onsets']
            p_frames = preds['output_frames']
        
        # Extraer predicción del centro de cada ventana
        center_idx = SEQ_LEN // 2
        p_onsets = p_onsets[:, center_idx, :]
        p_frames = p_frames[:, center_idx, :]
        
        print(f"   ✅ Inferencia completada")
        
        # 6. Liberar memoria
        del windows
        gc.collect()
        
        # 7. Decodificar notas
        notes = predictions_to_notes(p_onsets, p_frames, n_frames)
        
        # 8. Guardar MIDI
        midi_info = save_midi(notes, output_midi_path)
        
        # 9. Calcular tiempo total
        total_time = time.time() - t_start
        
        print(f"\n⏱️ Tiempo total: {total_time:.2f}s")
        print("✨ ¡Transcripción completada exitosamente!")
        print("="*60)
        
        # Retornar información completa
        return {
            "success": True,
            "processing_time": round(total_time, 2),
            "audio_duration": round(len(y) / settings.SAMPLE_RATE, 2),
            "midi_path": output_midi_path,
            **midi_info
        }
        
    except Exception as e:
        print(f"\n❌ ERROR EN TRANSCRIPCIÓN: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "error": str(e),
            "processing_time": round(time.time() - t_start, 2)
        }


# ===================================================================
# ========= TEST INDEPENDIENTE ======================================
# ===================================================================

if __name__ == "__main__":
    """
    Test independiente del servicio de transcripción.
    """
    print("🧪 MODO TEST - Servicio de Transcripción")
    
    # Archivo de prueba
    test_wav = "temp_uploads/test_audio.wav"
    test_midi = "temp_uploads/test_output.mid"
    
    if not os.path.exists(test_wav):
        print(f"❌ Archivo de prueba no encontrado: {test_wav}")
        print(f"   Coloca un archivo WAV en esa ubicación para probar.")
        sys.exit(1)
    
    # Ejecutar transcripción
    result = transcribe_piano_audio(test_wav, test_midi)
    
    # Mostrar resultado
    print(f"\n📋 RESULTADO:")
    for key, value in result.items():
        print(f"   {key}: {value}")
