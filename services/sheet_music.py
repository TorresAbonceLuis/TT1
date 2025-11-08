# -*- coding: utf-8 -*-
# services/sheet_music.py
#
# Servicio para convertir archivos MIDI a partituras en PDF

import os
import pretty_midi as pm
from music21 import converter, stream, note, chord, instrument, meter, tempo
from typing import Optional


def midi_to_pdf_sheet_music(
    midi_path: str,
    output_pdf_path: str,
    title: str = "Transcripción de Piano",
    composer: str = "Generado por IA"
) -> str:
    """
    Convierte un archivo MIDI a una partitura en formato PDF usando MuseScore directamente.
    
    Args:
        midi_path: Ruta al archivo MIDI
        output_pdf_path: Ruta donde guardar el PDF
        title: Título de la partitura
        composer: Compositor/autor
        
    Returns:
        Ruta al archivo PDF generado
    """
    
    import subprocess
    
    try:
        print(f"🎵 Convirtiendo MIDI a PDF con MuseScore...")
        musescore_path = '/opt/homebrew/bin/mscore'
        
        # Convertir MIDI directamente a PDF usando MuseScore
        # -o especifica el archivo de salida
        # Redirigir stderr a /dev/null para suprimir warnings de Qt (que no afectan la conversión)
        result = subprocess.run(
            [musescore_path, midi_path, '-o', output_pdf_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # MuseScore 4 siempre genera warnings de Qt/QML en stderr, pero funcionan correctamente
        # Solo nos importa si el PDF se creó exitosamente
        if os.path.exists(output_pdf_path) and os.path.getsize(output_pdf_path) > 0:
            print(f"✅ PDF generado exitosamente: {output_pdf_path} ({os.path.getsize(output_pdf_path)} bytes)")
            return output_pdf_path
        else:
            # Si no se creó el PDF, hay un error real
            # Filtrar solo líneas que NO sean warnings de qt.qml
            real_errors = [line for line in result.stderr.split('\n') 
                          if line and not line.startswith('qt.qml')]
            error_msg = '\n'.join(real_errors) if real_errors else "MuseScore no generó el PDF"
            raise Exception(f"MuseScore falló: {error_msg}")
        
    except subprocess.TimeoutExpired:
        raise Exception("MuseScore tardó demasiado tiempo (timeout 30s)")
    except FileNotFoundError:
        raise Exception("MuseScore no está instalado en /opt/homebrew/bin/mscore")
    except Exception as e:
        # Última verificación: ¿se creó el PDF de todas formas?
        if os.path.exists(output_pdf_path) and os.path.getsize(output_pdf_path) > 0:
            print(f"✅ PDF generado exitosamente: {output_pdf_path} ({os.path.getsize(output_pdf_path)} bytes)")
            return output_pdf_path
        raise Exception(f"Error al generar partitura PDF: {str(e)}")


def midi_to_musicxml(midi_path: str, output_xml_path: str) -> str:
    """
    Convierte MIDI a MusicXML (formato intermedio útil).
    
    Args:
        midi_path: Ruta al archivo MIDI
        output_xml_path: Ruta donde guardar el MusicXML
        
    Returns:
        Ruta al archivo MusicXML generado
    """
    try:
        midi_stream = converter.parse(midi_path)
        midi_stream.write('musicxml', fp=output_xml_path)
        return output_xml_path
    except Exception as e:
        raise Exception(f"Error al generar MusicXML: {str(e)}")


def create_simple_pdf_with_lilypond(
    midi_path: str,
    output_pdf_path: str
) -> str:
    """
    Método alternativo usando Lilypond directamente si music21 falla.
    Requiere tener Lilypond instalado en el sistema.
    
    Args:
        midi_path: Ruta al archivo MIDI
        output_pdf_path: Ruta donde guardar el PDF
        
    Returns:
        Ruta al archivo PDF generado
    """
    import subprocess
    
    try:
        # Generar archivo .ly temporal
        ly_path = output_pdf_path.replace('.pdf', '.ly')
        
        # Crear archivo Lilypond básico
        ly_content = f'''
\\version "2.24.0"
\\score {{
  \\new PianoStaff <<
    \\new Staff {{
      \\clef treble
      \\articulate
      \\midi2ly "{os.path.abspath(midi_path)}"
    }}
    \\new Staff {{
      \\clef bass
      \\articulate
      \\midi2ly "{os.path.abspath(midi_path)}"
    }}
  >>
  \\layout {{ }}
  \\midi {{ }}
}}
'''
        
        # Usar midi2ly para convertir
        subprocess.run([
            'midi2ly',
            midi_path,
            '-o', ly_path
        ], check=True)
        
        # Compilar a PDF
        subprocess.run([
            'lilypond',
            '--pdf',
            '-o', output_pdf_path.replace('.pdf', ''),
            ly_path
        ], check=True)
        
        # Limpiar archivos temporales
        if os.path.exists(ly_path):
            os.remove(ly_path)
        
        return output_pdf_path
        
    except FileNotFoundError:
        raise Exception("Lilypond no está instalado. Por favor instala Lilypond para generar PDFs.")
    except Exception as e:
        raise Exception(f"Error al generar PDF con Lilypond: {str(e)}")


def generate_sheet_music_pdf(
    midi_path: str,
    output_pdf_path: str,
    title: str = "Transcripción de Piano",
    composer: str = "Generado por IA",
    method: str = "music21"
) -> str:
    """
    Función principal para generar partituras en PDF.
    Intenta múltiples métodos automáticamente.
    
    Args:
        midi_path: Ruta al archivo MIDI
        output_pdf_path: Ruta donde guardar el PDF
        title: Título de la partitura
        composer: Compositor/autor
        method: Método preferido ("music21" o "lilypond")
        
    Returns:
        Ruta al archivo PDF generado
    """
    
    if not os.path.exists(midi_path):
        raise FileNotFoundError(f"El archivo MIDI no existe: {midi_path}")
    
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)
    
    # Intentar método preferido primero
    if method == "music21":
        try:
            result = midi_to_pdf_sheet_music(midi_path, output_pdf_path, title, composer)
            # Verificar que el PDF se creó correctamente
            if os.path.exists(output_pdf_path) and os.path.getsize(output_pdf_path) > 0:
                print(f"✅ PDF generado exitosamente con music21: {output_pdf_path}")
                return result
            else:
                raise Exception("El PDF no se generó correctamente")
        except Exception as e:
            # Solo intentar Lilypond si realmente falló (no se creó el PDF)
            if not (os.path.exists(output_pdf_path) and os.path.getsize(output_pdf_path) > 0):
                print(f"Falló music21, intentando Lilypond: {e}")
                try:
                    return create_simple_pdf_with_lilypond(midi_path, output_pdf_path)
                except Exception as e2:
                    raise Exception(f"Todos los métodos fallaron. music21: {e}, Lilypond: {e2}")
            else:
                # Si el PDF se creó a pesar del error, retornarlo
                print(f"✅ PDF generado exitosamente con music21 (con warnings ignorados)")
                return output_pdf_path
    else:
        try:
            return create_simple_pdf_with_lilypond(midi_path, output_pdf_path)
        except Exception as e:
            print(f"Falló Lilypond, intentando music21: {e}")
            try:
                return midi_to_pdf_sheet_music(midi_path, output_pdf_path, title, composer)
            except Exception as e2:
                # Verificar si el PDF se creó de todas formas
                if os.path.exists(output_pdf_path) and os.path.getsize(output_pdf_path) > 0:
                    print(f"✅ PDF generado exitosamente con music21 (con warnings ignorados)")
                    return output_pdf_path
                raise Exception(f"Todos los métodos fallaron. Lilypond: {e}, music21: {e2}")
