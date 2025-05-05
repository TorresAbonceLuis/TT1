import Head from 'next/head';
import Link from 'next/link';
import Image from 'next/image';

export default function Home() {
  return (
    <>
      <Head>
        <title>Audio a Notación | ESCOM</title>
        <meta name="description" content="Transforma tus interpretaciones de piano en partituras profesionales" />
      </Head>

      <header className="bg-gradient-to-br from-gray-900 to-red-900 text-white py-16 px-4 text-center relative overflow-hidden">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-center text-4xl md:text-5xl font-bold mb-6">
            <span className="mr-3">🎵</span>
            <h1>Audio a Notación</h1>
          </div>
          <p className="text-xl md:text-2xl font-light max-w-2xl mx-auto mb-8">
            Transforma tus interpretaciones de piano en partituras profesionales de forma automática
          </p>
          <Link href="/dashboard" className="inline-block bg-yellow-500 hover:bg-yellow-400 text-gray-900 font-semibold px-8 py-3 rounded-full transition-all duration-300 transform hover:-translate-y-1 shadow-lg">
            Ver demostración
          </Link>
        </div>
      </header>

      <section className="py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center text-red-700 mb-12 relative">
            Sobre el Proyecto
            <span className="block w-24 h-1 bg-yellow-500 mx-auto mt-4"></span>
          </h2>
          <p className="text-center max-w-3xl mx-auto text-lg mb-12">
            Audio a Notación es una innovadora solución web desarrollada como Trabajo Terminal para la carrera de Ingeniería en Sistemas Computacionales en ESCOM-IPN. Nuestro sistema utiliza algoritmos avanzados de procesamiento de audio y aprendizaje automático para convertir grabaciones de piano en partituras musicales en formato PDF.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-12">
            <div className="bg-gray-800 rounded-xl p-8 shadow-lg transition-all duration-300 hover:-translate-y-2">
              <div className="text-5xl mb-6 text-red-600">🎹</div>
              <h3 className="text-2xl font-semibold mb-4">Fácil de usar</h3>
              <p className="text-gray-300">Interfaz intuitiva diseñada para músicos de todos los niveles. Solo sube tu audio y obtén tu partitura en segundos.</p>
            </div>
            
            <div className="bg-gray-800 rounded-xl p-8 shadow-lg transition-all duration-300 hover:-translate-y-2">
              <div className="text-5xl mb-6 text-red-600">⚡</div>
              <h3 className="text-2xl font-semibold mb-4">Procesamiento avanzado</h3>
              <p className="text-gray-300">Técnicas de transformación de tiempo-frecuencia y reconocimiento de patrones para una transcripción precisa.</p>
            </div>
            
            <div className="bg-gray-800 rounded-xl p-8 shadow-lg transition-all duration-300 hover:-translate-y-2">
              <div className="text-5xl mb-6 text-red-600">📄</div>
              <h3 className="text-2xl font-semibold mb-4">PDF descargable</h3>
              <p className="text-gray-300">Genera partituras en formato PDF listas para imprimir, compartir o editar en software especializado.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="py-20 px-4 bg-gray-900">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center text-white mb-12 relative">
            Demostración
            <span className="block w-24 h-1 bg-yellow-500 mx-auto mt-4"></span>
          </h2>
          <div className="max-w-4xl mx-auto bg-gray-800 rounded-xl overflow-hidden shadow-2xl">
            <Image 
              src="/screenshot.jpg" 
              alt="Interfaz de Audio a Notación" 
              width={800}
              height={450}
              layout="responsive"
              quality={80}
              priority
            />
          </div>
        </div>
      </section>

      <section className="py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center text-red-700 mb-12 relative">
            Nuestro Equipo
            <span className="block w-24 h-1 bg-yellow-500 mx-auto mt-4"></span>
          </h2>
          
          <div className="flex flex-wrap justify-center gap-8">
            <div className="bg-gray-800 rounded-xl p-8 text-center w-full md:w-80">
              <div className="w-32 h-32 rounded-full mx-auto border-4 border-yellow-500 mb-4 overflow-hidden">
                <Image 
                  src="/team/jeshua.jpg" 
                  alt="Jeshua Jonathan" 
                  width={128}
                  height={128}
                  objectFit="cover"
                />
              </div>
              <h3 className="text-2xl font-semibold text-red-600">Salazar Carreón Jeshua Jonathan</h3>
              <p className="text-gray-300 mt-2">Ing. en Sistemas Computacionales</p>
              <p className="text-gray-400">Boleta: 2021630656</p>
            </div>
            
            <div className="bg-gray-800 rounded-xl p-8 text-center w-full md:w-80">
              <div className="w-32 h-32 rounded-full mx-auto border-4 border-yellow-500 mb-4 overflow-hidden">
                <Image 
                  src="/team/luis.jpg" 
                  alt="Luis Miguel" 
                  width={128}
                  height={128}
                  objectFit="cover"
                />
              </div>
              <h3 className="text-2xl font-semibold text-red-600">Torres Abonce Luis Miguel</h3>
              <p className="text-gray-300 mt-2">Ing. en Sistemas Computacionales</p>
              <p className="text-gray-400">Boleta: 2021630738</p>
            </div>
          </div>
          
          <div className="mt-16">
            <h3 className="text-2xl font-bold text-center text-red-700 mb-8">Directores</h3>
            <div className="flex flex-wrap justify-center gap-8">
              <div className="bg-gray-800 rounded-xl p-8 text-center w-full md:w-96">
                <h3 className="text-xl font-semibold text-red-600">M. en C. César Mújica Ascencio</h3>
                <p className="text-gray-300 mt-2">Director</p>
                <p className="text-gray-400">Profesor de ESCOM/IPN</p>
              </div>
              
              <div className="bg-gray-800 rounded-xl p-8 text-center w-full md:w-96">
                <h3 className="text-xl font-semibold text-red-600">Tania Rodríguez Sarabia</h3>
                <p className="text-gray-300 mt-2">Directora</p>
                <p className="text-gray-400">Profesora de ESCOM/IPN</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <footer className="py-12 px-4 bg-gray-900 text-center">
        <div className="max-w-4xl mx-auto">
          <div className="text-3xl font-bold mb-4">🎵 Audio a Notación</div>
          <p className="text-gray-300">Trabajo Terminal | Ingeniería en Sistemas Computacionales | ESCOM-IPN</p>
          <p className="text-gray-500 mt-4">© {new Date().getFullYear()} Todos los derechos reservados</p>
        </div>
      </footer>
    </>
  );
}