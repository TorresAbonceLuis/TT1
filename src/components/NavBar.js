import React, { useContext, useEffect, useState } from "react";
import Link from "next/link";
import AuthContext from "../context/AuthContext";
import { useRouter } from "next/router";

const Navbar = () => {
  const { user, logout } = useContext(AuthContext);
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Revisar si hay usuario en localStorage para mostrar el botón de Logout correctamente
    const storedUser = localStorage.getItem("user");
    setIsAuthenticated(!!storedUser);
  }, [user]);

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <nav className="bg-gray-900 p-4 text-white flex justify-between">
      <h1 className="text-xl font-bold">🎵 AudioTranscriber</h1>
      
      <div className="navbar-buttons">
        {isAuthenticated ? (
          <button onClick={handleLogout} className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded">
            Logout
          </button>
        ) : (
          <>
            <Link href="/login" className="mr-4 hover:underline">Login</Link>
            <Link href="/register" className="hover:underline">Register</Link>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
