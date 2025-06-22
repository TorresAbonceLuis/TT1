import { useState } from "react";
import Head from "next/head";
import Navbar from "../components/NavBar";

export default function Dashboard() {
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [uploadSuccess, setUploadSuccess] = useState("");
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    setUploadSuccess("");

    if (selectedFile) {
      const allowedTypes = ["audio/mpeg", "audio/wav", "audio/ogg"];
      const maxSize = 10 * 1024 * 1024;

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
      setError("");
    }
  };

const handleUpload = async () => {
    if (!file) {
        setError("Por favor, selecciona un archivo de audio");
        return;
    }

    setIsUploading(true);
    setError("");
    
    try {
        const formData = new FormData();
        formData.append("file", file);

        // Cambia esta URL según donde esté alojado tu backend
        const response = await fetch("http://localhost:8000/upload/", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error(await response.text());
        }

        const data = await response.json();
        setUploadSuccess(`¡Archivo subido correctamente! Transcripción: ${data.transcription}`);
        setFile(null);
        document.getElementById("audio-upload").value = "";
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

                  {uploadSuccess && (
                    <div className="p-4 bg-green-900/50 border border-green-700 text-green-300 rounded-lg flex items-start">
                      <span className="text-xl mr-2">🎉</span>
                      <p>{uploadSuccess}</p>
                    </div>
                  )}

                  <button
                    onClick={handleUpload}
                    disabled={!file || isUploading}
                    className={`w-full py-3 px-6 rounded-xl font-semibold text-lg flex items-center justify-center ${
                      !file || isUploading
                        ? "bg-gray-600 cursor-not-allowed"
                        : "bg-red-600 hover:bg-red-700 transform hover:-translate-y-1"
                    } text-white transition-all duration-300 shadow-lg`}
                  >
                    {isUploading ? (
                      <>
                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Procesando...
                      </>
                    ) : (
                      "Subir y Transcribir"
                    )}
                  </button>
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