// pages/transcription.js
//
// Página para la transcripción de piano

import Head from 'next/head';
import NavBar from '../components/NavBar';
import PianoTranscription from '../components/PianoTranscription';

export default function TranscriptionPage() {
  return (
    <>
      <Head>
        <title>Transcripción de Piano | Audio a Notación</title>
        <meta name="description" content="Transcribe automáticamente tus grabaciones de piano a partituras MIDI y PDF" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-red-900">
        <NavBar />
        
        <main className="container mx-auto px-4 py-12">
          {/* Hero Section */}
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Transcripción Automática de Piano
            </h1>
            <p className="text-lg text-gray-300 max-w-2xl mx-auto">
              Convierte tus grabaciones de piano en partituras digitales usando 
              inteligencia artificial avanzada (CNN-LSTM).
            </p>
          </div>

          {/* Componente Principal */}
          <PianoTranscription />

          {/* Información Adicional */}
          <div className="mt-16 grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
              <div className="text-3xl mb-3">🎼</div>
              <h3 className="text-xl font-semibold mb-2 text-red-500">Precisión IA</h3>
              <p className="text-gray-300 text-sm">
                Modelo CNN-LSTM entrenado específicamente para detectar notas de piano 
                con alta precisión.
              </p>
            </div>

            <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
              <div className="text-3xl mb-3">⚡</div>
              <h3 className="text-xl font-semibold mb-2 text-red-500">Procesamiento Rápido</h3>
              <p className="text-gray-300 text-sm">
                Sistema optimizado con procesamiento por bloques para manejar 
                archivos largos sin problemas de memoria.
              </p>
            </div>

            <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
              <div className="text-3xl mb-3">�</div>
              <h3 className="text-xl font-semibold mb-2 text-red-500">Partitura PDF</h3>
              <p className="text-gray-300 text-sm">
                Descarga tus transcripciones como partituras PDF profesionales, 
                listas para imprimir o compartir.
              </p>
            </div>
          </div>

          {/* Instrucciones */}
          <div className="mt-12 max-w-3xl mx-auto bg-gray-800 rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-bold mb-4 text-white">
              📖 Cómo usar
            </h2>
            <ol className="space-y-3 text-gray-300">
              <li className="flex items-start">
                <span className="font-bold text-red-500 mr-3">1.</span>
                <span>Selecciona un archivo de audio de piano en formato WAV</span>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-red-500 mr-3">2.</span>
                <span>Haz clic en &quot;Iniciar Transcripción&quot; y espera mientras la IA procesa tu audio</span>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-red-500 mr-3">3.</span>
                <span>Observa el progreso en tiempo real con la barra de avance</span>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-red-500 mr-3">4.</span>
                <span>Una vez completado, descarga tu partitura en formato PDF</span>
              </li>
            </ol>

            <div className="mt-6 p-4 bg-yellow-900/30 border border-yellow-500 rounded-lg">
              <p className="text-sm text-yellow-300">
                <strong>💡 Consejo:</strong> Solo se aceptan archivos WAV. Para mejores resultados, usa grabaciones de piano 
                solo (sin otros instrumentos) con buena calidad de audio.
              </p>
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="mt-20 py-12 bg-gray-900 border-t border-gray-800">
          <div className="container mx-auto px-4 text-center">
            <div className="text-3xl font-bold mb-4 text-white">🎵 Audio a Notación</div>
            <p className="text-gray-300">Trabajo Terminal | Ingeniería en Sistemas Computacionales | ESCOM-IPN</p>
            <p className="text-gray-500 mt-4">© {new Date().getFullYear()} Todos los derechos reservados</p>
          </div>
        </footer>
      </div>
    </>
  );
}
