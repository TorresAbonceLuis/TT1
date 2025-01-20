import { useState, useContext, useEffect } from "react";
import AuthContext from "../context/AuthContext";
import AuthForm from "../components/AuthForm";
import { useRouter } from "next/router";
import Navbar from "../components/Navbar";

export default function Login() {
  const { login } = useContext(AuthContext);
  const router = useRouter();
  const [error, setError] = useState(""); // Estado para manejar errores

  useEffect(() => {
    // Ocultar el botón "Login" en la Navbar solo en esta página
    const loginButton = document.querySelectorAll(".navbar-buttons a[href='/login']");
    loginButton.forEach(button => {
      button.style.display = "none";
    });

    return () => {
      // Restaurar el botón cuando el usuario salga de login.js
      loginButton.forEach(button => {
        button.style.display = "inline";
      });
    };
  }, []);

  const handleLogin = async (email, password) => {
    setError(""); // Limpiar errores previos
    const res = await login(email, password);

    if (res.message === "Login exitoso") {
      router.push("/dashboard");
    } else {
      setError(res.message); // Guardar el mensaje de error en el estado
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-900 text-white">
      {/* Navbar */}
      <Navbar />

      {/* Contenido de la página de login */}
      <div className="flex flex-grow items-center justify-center">
        <div className="w-full max-w-md p-6 bg-gray-800 rounded-lg shadow-lg">
          <AuthForm type="login" onSubmit={handleLogin} />
          {error && <p className="text-red-500 text-center mt-4">{error}</p>} {/* Mensaje de error */}
        </div>
      </div>
    </div>
  );
}
