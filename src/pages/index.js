import React, { useEffect } from "react";
import Navbar from "../components/Navbar";

export default function Home() {
  useEffect(() => {
    // Ocultar los botones de Login y Register solo en Index.js
    const navbarButtons = document.querySelectorAll(".navbar-buttons");
    navbarButtons.forEach(button => {
      button.style.display = "none";
    });

    return () => {
      // Restaurar los botones cuando salgas de index.js
      navbarButtons.forEach(button => {
        button.style.display = "block";
      });
    };
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-gray-900 text-white overflow-hidden">
      {/* Navbar */}
      <Navbar />

      {/* Contenido principal */}
      <div className="flex flex-grow items-center justify-center flex-col text-center">
        <h1 className="text-4xl font-bold">
          <span role="img" aria-label="music">🎵</span> AudioTranscriber
        </h1>
        <p className="text-lg mt-4">Convierte tus grabaciones en partituras de piano automáticamente.</p>
        <div className="mt-6">
          <a href="/login" className="bg-red-600 hover:bg-red-700 text-white p-3 rounded mr-4">Iniciar Sesión</a>
          <a href="/register" className="bg-gray-700 hover:bg-gray-800 text-white p-3 rounded">Registrarse</a>
        </div>
      </div>
    </div>
  );
}
