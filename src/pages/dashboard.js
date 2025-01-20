import { useContext, useEffect, useState } from "react";
import AuthContext from "../context/AuthContext";
import { useRouter } from "next/router";
import Navbar from "../components/Navbar";

export default function Dashboard() {
  const { user } = useContext(AuthContext);
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [uploadSuccess, setUploadSuccess] = useState("");

  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (!storedUser) {
      router.push("/login");
    } else {
      setLoading(false);
    }
  }, [router]);

  if (loading) {
    return null;
  }

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];

    if (selectedFile) {
      const allowedExtensions = ["audio/mpeg", "audio/wav", "audio/ogg"];
      if (!allowedExtensions.includes(selectedFile.type)) {
        setError("Solo se permiten archivos de audio (MP3, WAV, OGG).");
        setFile(null);
        return;
      }

      setFile(selectedFile);
      setError("");
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Por favor, selecciona un archivo de audio antes de subir.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      if (res.ok) {
        setUploadSuccess(`Archivo subido correctamente: ${data.filePath}`);
      } else {
        setError("Error al subir el archivo.");
      }
    } catch (error) {
      setError("Error en la subida.");
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-900 text-white">
      <Navbar />

      <div className="flex flex-grow items-center justify-center">
        <div className="bg-gray-800 p-6 rounded-lg shadow-lg text-center w-full max-w-md">
          <h2 className="text-2xl font-bold mb-4">Subir Archivo de Audio 🎵</h2>
          <input
            type="file"
            accept="audio/*"
            onChange={handleFileChange}
            className="w-full p-2 bg-gray-700 text-white rounded cursor-pointer"
          />
          {error && <p className="text-red-500 mt-2">{error}</p>}
          {uploadSuccess && <p className="text-green-500 mt-2">{uploadSuccess}</p>}
          <button
            onClick={handleUpload}
            className="mt-4 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded"
          >
            Subir Archivo
          </button>
        </div>
      </div>
    </div>
  );
}
