#!/usr/bin/env python
# -*- coding: utf-8 -*-
# test_transcription.py
#
# Script de prueba rápida para verificar que el servicio de transcripción funciona

import os
import sys

# Agregar el directorio Backend al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.transcription import (
    transcribe_piano_audio,
    MODELO_CAMPEON_PATH
)

def test_transcription(audio_file: str):
    """
    Prueba rápida del servicio de transcripción.
    
    Args:
        audio_file: Ruta al archivo de audio de prueba
    """
    
    print("=" * 60)
    print("TEST DE TRANSCRIPCIÓN DE PIANO")
    print("=" * 60)
    
    # 1. Verificar que existe el modelo
    if not os.path.exists(MODELO_CAMPEON_PATH):
        print(f"\n❌ ERROR: No se encontró el modelo en:")
        print(f"   {MODELO_CAMPEON_PATH}")
        print(f"\n📌 Por favor, coloca el archivo del modelo en:")
        print(f"   Backend/modelos/modelo.keras")
        return False
    
    print(f"✅ Modelo encontrado: {MODELO_CAMPEON_PATH}")
    
    # 2. Verificar que existe el archivo de audio
    if not os.path.exists(audio_file):
        print(f"\n❌ ERROR: No se encontró el archivo de audio:")
        print(f"   {audio_file}")
        return False
    
    print(f"✅ Archivo de audio encontrado: {audio_file}")
    
    # 3. Definir archivo de salida
    output_midi = audio_file.replace('.wav', '_test_output.mid')
    output_midi = output_midi.replace('.mp3', '_test_output.mid')
    
    print(f"\n🎵 Iniciando transcripción...")
    print(f"   Entrada: {audio_file}")
    print(f"   Salida:  {output_midi}")
    print()
    
    # 4. Callback para mostrar progreso
    def progress_callback(progress: int, message: str):
        bar_length = 40
        filled = int(bar_length * progress / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        print(f"\r[{bar}] {progress}% - {message}", end='', flush=True)
    
    try:
        # 5. Ejecutar transcripción
        result = transcribe_piano_audio(
            audio_file,
            output_midi,
            progress_callback
        )
        
        print("\n")
        print("=" * 60)
        print("✅ TRANSCRIPCIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print(f"📊 Resultados:")
        print(f"   • Duración: {result['duration_seconds']:.2f} segundos")
        print(f"   • Frames procesados: {result['total_frames']}")
        print(f"   • Notas detectadas: {result['total_notes']}")
        print(f"   • Archivo MIDI: {output_midi}")
        print()
        
        if result['total_notes'] == 0:
            print("⚠️  ADVERTENCIA: No se detectaron notas.")
            print("   Posibles causas:")
            print("   - El audio no contiene piano")
            print("   - El audio tiene muy bajo volumen")
            print("   - El modelo requiere ajuste de umbrales")
        
        return True
        
    except Exception as e:
        print("\n")
        print("=" * 60)
        print("❌ ERROR EN LA TRANSCRIPCIÓN")
        print("=" * 60)
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    
    # Verificar argumentos
    if len(sys.argv) < 2:
        print("Uso: python test_transcription.py <archivo_audio.wav>")
        print()
        print("Ejemplo:")
        print("  python test_transcription.py audio5.wav")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    
    # Ejecutar prueba
    success = test_transcription(audio_file)
    
    sys.exit(0 if success else 1)
