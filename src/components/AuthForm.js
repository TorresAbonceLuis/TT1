import React, { useState } from "react";
import Button from "./Button";
import Input from "./Input";

const AuthForm = ({ type, onSubmit }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(email, password);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 bg-gray-800 p-6 rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold text-center text-white">{type === "login" ? "Iniciar Sesión" : "Registrarse"}</h2>
      <Input type="email" placeholder="Correo" value={email} onChange={(e) => setEmail(e.target.value)} />
      <Input type="password" placeholder="Contraseña" value={password} onChange={(e) => setPassword(e.target.value)} />
      <Button type="submit">{type === "login" ? "Ingresar" : "Registrarse"}</Button>
    </form>
  );
};

export default AuthForm;
