import React from "react";

const Button = ({ children, onClick, type = "button", className = "" }) => {
  return (
    <button
      type={type}
      onClick={onClick}
      className={`w-full p-2 bg-red-600 hover:bg-red-700 rounded text-white font-semibold ${className}`}
    >
      {children}
    </button>
  );
};

export default Button;
