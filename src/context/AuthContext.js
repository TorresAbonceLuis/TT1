import { createContext, useState, useEffect } from "react";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Verificar si hay un usuario guardado en localStorage al cargar la app
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  const login = async (email, password) => {
    const res = await fetch("/api/auth", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, action: "login" }),
    });

    const data = await res.json();
    if (res.ok) {
      setUser(data.user);
      localStorage.setItem("user", JSON.stringify(data.user)); // Guardar usuario en localStorage
    }
    return data;
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("user"); // Eliminar usuario al cerrar sesión
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
