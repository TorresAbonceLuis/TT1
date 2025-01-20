import { useContext, useEffect } from "react";
import AuthContext from "../context/AuthContext";
import AuthForm from "../components/AuthForm";
import { useRouter } from "next/router";
import Navbar from "../components/Navbar";

export default function Register() {
  const { register } = useContext(AuthContext);
  const router = useRouter();

  useEffect(() => {
    // Ocultar el botón "Register" en la Navbar solo en esta página
    const registerButton = document.querySelectorAll(".navbar-buttons a[href='/register']");
    registerButton.forEach(button => {
      button.style.display = "none";
    });

    return () => {
      // Restaurar el botón cuando el usuario salga de register.js
      registerButton.forEach(button => {
        button.style.display = "inline";
      });
    };
  }, []);

  const handleRegister = async (email, password) => {
    const res = await register(email, password);
    if (res.message === "Usuario registrado") router.push("/login");
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-900 text-white">
      {/* Navbar */}
      <Navbar />

      {/* Contenido de la página */}
      <div className="flex flex-grow items-center justify-center">
        <AuthForm type="register" onSubmit={handleRegister} />
      </div>
    </div>
  );
}
