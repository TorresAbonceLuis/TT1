import Head from 'next/head';
import PianoTranscription from '../components/PianoTranscription';
import FloatingNotes from '../components/FloatingNotes';

export default function Home() {
  return (
    <>
      <Head>
        <title>Audio a Notación | Piano a Partitura</title>
        <meta name="description" content="Convierte tus interpretaciones de piano a partituras" />
      </Head>

      <div className="h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 relative overflow-hidden flex items-center justify-center">
        {/* Notas musicales flotantes en el fondo */}
        <FloatingNotes />
        
        {/* Contenido principal con z-index mayor */}
        <div className="relative z-10 w-full max-w-6xl px-4">
          {/* Header con descripción */}
          <header className="text-center mb-8">
            <div className="max-w-4xl mx-auto">
              {/* Título con icono musical */}
              <div className="flex items-center justify-center mb-3">
                <h1 className="text-3xl md:text-5xl font-bold text-white tracking-tight">
                  Audio a Notación
                </h1>
              </div>
              
              {/* Subtítulo */}
              <p className="text-base md:text-lg text-blue-200 font-light max-w-2xl mx-auto">
                Convierte tus interpretaciones de piano a partituras con nuestra herramienta inteligente
              </p>
            </div>
          </header>

          {/* Componente de transcripción */}
          <main>
            <PianoTranscription />
          </main>
        </div>
      </div>
    </>
  );
}