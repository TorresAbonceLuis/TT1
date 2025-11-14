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

      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 relative">
        {/* Notas musicales flotantes en el fondo */}
        <FloatingNotes />
        
        {/* Contenido principal con z-index mayor */}
        <div className="relative z-10">
          {/* Header con descripción */}
          <header className="pt-20 pb-16 px-4 text-center">
          <div className="max-w-4xl mx-auto">
            {/* Título con icono musical */}
            <div className="flex items-center justify-center mb-4">
              <span className="text-5xl md:text-6xl mr-3">🎵</span>
              <h1 className="text-4xl md:text-6xl font-bold text-white tracking-tight">
                Audio a Notación
              </h1>
              <span className="text-3xl md:text-4xl ml-2 text-cyan-400">✨</span>
            </div>
            
            {/* Subtítulo */}
            <p className="text-lg md:text-xl text-blue-200 mb-12 font-light max-w-2xl mx-auto">
              Convierte tus interpretaciones de piano a partituras con nuestra herramienta inteligente
            </p>
          </div>
        </header>

          {/* Componente de transcripción */}
          <main className="container mx-auto px-4 pb-20">
            <PianoTranscription />
          </main>
        </div>
      </div>
    </>
  );
}