import React from "react";

const Input = ({ type, placeholder, value, onChange }) => {
  return (
    <input
      type={type}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      className="w-full p-2 rounded bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-red-500"
    />
  );
};

export default Input;
