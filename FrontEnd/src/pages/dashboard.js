import { useState } from "react";
import Head from "next/head";
import Navbar from "../components/NavBar";

export default function Dashboard() {
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [pdfUrl, setPdfUrl] = useState(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    setPdfUrl(null); // Resetear PDF anterior al seleccionar nuevo archivo
    setError("");

    if (selectedFile) {
      const allowedTypes = ["audio/mpeg", "audio/wav", "audio/ogg"];
      const maxSize = 10 * 1024 * 1024; // 10MB

      if (!allowedTypes.includes(selectedFile.type)) {
        setError("Formato no soportado. Sube archivos MP3, WAV u OGG.");
        setFile(null);
        return;
      }

      if (selectedFile.size > maxSize) {
        setError("El archivo es demasiado grande (máximo 10MB)");
        setFile(null);
        return;
      }

      setFile(selectedFile);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Por favor, selecciona un archivo de audio");
      return;
    }

    setIsUploading(true);
    setError("");
    setProgress(0);
    setPdfUrl(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      // Simular progreso de subida
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          const newProgress = prev + 10;
          if (newProgress >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return newProgress;
        });
      }, 300);

      // Enviar archivo al backend
      const response = await fetch("http://localhost:8000/upload/", {
        method: "POST",
        body: formData,
      });

      clearInterval(progressInterval);
      setProgress(100);

      if (!response.ok) {
        throw new Error(await response.text());
      }

      // Recibir el PDF y crear URL para descarga
      const pdfBlob = await response.blob();
      const pdfUrl = URL.createObjectURL(pdfBlob);
      setPdfUrl(pdfUrl);

    } catch (err) {
      setError(err.message || "Error al subir el archivo. Intenta nuevamente.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-900 text-white">
      <Head>
        <title>Dashboard | Audio a Notación</title>
      </Head>

      <Navbar />

      <main className="flex-grow container mx-auto px-4 py-12">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-red-600 mb-4 relative">
              Panel de Transcripción
              <span className="block w-24 h-1 bg-yellow-500 mx-auto mt-4"></span>
            </h1>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Convierte tus grabaciones de piano en partituras
            </p>
          </div>
          <div className="bg-gray-800 rounded-xl shadow-2xl overflow-hidden">
            <div className="p-8">
              <div className="mb-8">
                <div className="flex items-center justify-center mb-6">
                  <div className="mr-4 text-5xl">🎹</div>
                  <h2 className="text-2xl font-semibold">Sube tu archivo de audio</h2>
                </div>
                
                <div className="space-y-6">
                  <div>
                    <label className="block text-lg font-medium mb-3" htmlFor="audio-upload">
                      Selecciona un archivo de audio (MP3, WAV, OGG)
                    </label>
                    <div className="relative">
                      <input
                        id="audio-upload"
                        type="file"
                        accept="audio/*"
                        onChange={handleFileChange}
                        className="block w-full text-lg text-gray-400
                          file:mr-6 file:py-3 file:px-6
                          file:rounded-xl file:border-0
                          file:text-lg file:font-semibold
                          file:bg-red-600 file:text-white
                          hover:file:bg-red-700
                          cursor-pointer transition-all"
                        disabled={isUploading}
                      />
                    </div>
                  </div>

                  {file && (
                    <div className="bg-gray-700 rounded-lg p-4 border-l-4 border-yellow-500">
                      <h3 className="font-medium text-lg mb-2">Archivo seleccionado:</h3>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-gray-400">Nombre:</p>
                          <p className="truncate">{file.name}</p>
                        </div>
                        <div>
                          <p className="text-gray-400">Tamaño:</p>
                          <p>{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {error && (
                    <div className="p-4 bg-red-900/50 border border-red-700 text-red-300 rounded-lg flex items-start">
                      <span className="text-xl mr-2">⚠️</span>
                      <p>{error}</p>
                    </div>
                  )}

                  {!pdfUrl ? (
                    <button
                      onClick={handleUpload}
                      disabled={!file || isUploading}
                      className={`w-full py-3 px-6 rounded-xl font-semibold text-lg flex items-center justify-center ${
                        !file || isUploading
                          ? "bg-gray-600 cursor-not-allowed"
                          : "bg-red-600 hover:bg-red-700"
                      } text-white transition-all duration-300 shadow-lg`}
                    >
                      {isUploading ? (
                        <>
                          <div className="w-full bg-gray-700 rounded-full h-4 mr-4">
                            <div
                              className="bg-yellow-500 h-4 rounded-full"
                              style={{ width: `${progress}%` }}
                            ></div>
                          </div>
                          Procesando... {progress}%
                        </>
                      ) : (
                        "Subir y Transcribir"
                      )}
                    </button>
                  ) : (
                    <a
                      href={pdfUrl}
                      download="partitura.pdf"
                      className="w-full py-3 px-6 rounded-xl font-semibold text-lg flex items-center justify-center bg-green-600 hover:bg-green-700 text-white transition-all duration-300 shadow-lg"
                    >
                      ↓ Descargar Partitura (PDF)
                    </a>
                  )}
                </div>
              </div>

              <div className="border-t border-gray-700 pt-8">
                <h3 className="text-xl font-semibold mb-4 flex items-center">
                  <span className="mr-2">📝</span> Instrucciones
                </h3>
                <ol className="list-decimal list-inside space-y-2 text-gray-300">
                  <li>Selecciona un archivo de audio de piano (hasta 10MB)</li>
                  <li>Haz clic en Subir y Transcribir</li>
                  <li>Espera a que se procese el audio</li>
                  <li>Descarga tu partitura en formato PDF</li>
                </ol>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}