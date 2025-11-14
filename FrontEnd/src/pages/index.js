import Head from 'next/head';
import PianoTranscription from '../components/PianoTranscription';

export default function Home() {
  return (
    <>
      <Head>
        <title>Audio a Notación | Piano a Partitura</title>
        <meta name="description" content="Convierte tus interpretaciones de piano a partituras" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-red-900">
        {/* Header con descripción */}
        <header className="pt-16 pb-12 px-4 text-center">
          <div className="max-w-3xl mx-auto">
            <div className="flex items-center justify-center text-4xl md:text-5xl font-bold mb-6 text-white">
              <span className="mr-3">�</span>
              <h1>Audio a Notación</h1>
            </div>
            
            <p className="text-xl md:text-2xl text-gray-200 mb-6 font-light">
              Convierte tus interpretaciones de piano a partituras con nuestra herramienta
            </p>
            
            <div className="bg-yellow-900/30 border border-yellow-500 rounded-lg p-6 max-w-2xl mx-auto">
              <p className="text-gray-200 text-lg">
                <strong className="text-yellow-400">⚠️ Importante:</strong> Deberá subir <strong>única y exclusivamente</strong> archivos con interpretaciones de piano en <strong>formato WAV</strong>.
              </p>
            </div>
          </div>
        </header>

        {/* Componente de transcripción */}
        <main className="container mx-auto px-4 pb-20">
          <PianoTranscription />
        </main>
      </div>
    </>
  );
}