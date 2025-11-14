// components/FloatingNotes.js
// Notas musicales flotantes que rebotan en los bordes

import React, { useEffect, useState } from 'react';

const FloatingNotes = () => {
  const [notes, setNotes] = useState([]);

  useEffect(() => {
    // Símbolos de notas musicales
    const noteSymbols = ['♪', '♫', '♬', '♩', '♭', '♮', '♯', '𝄞'];
    
    // Crear 15 notas con posiciones y velocidades aleatorias
    const initialNotes = Array.from({ length: 15 }, (_, i) => ({
      id: i,
      symbol: noteSymbols[Math.floor(Math.random() * noteSymbols.length)],
      x: Math.random() * (typeof window !== 'undefined' ? window.innerWidth : 1000),
      y: Math.random() * (typeof window !== 'undefined' ? window.innerHeight : 800),
      vx: (Math.random() - 0.5) * 2, // velocidad horizontal (-1 a 1)
      vy: (Math.random() - 0.5) * 2, // velocidad vertical (-1 a 1)
      size: 50 + Math.random() * 60, // tamaño 50-110px (mucho más grandes)
      opacity: 0.3 + Math.random() * 0.3, // opacidad 0.3-0.6 (más visibles)
      rotation: Math.random() * 360,
      rotationSpeed: (Math.random() - 0.5) * 2,
    }));

    setNotes(initialNotes);

    // Animación
    const animationFrame = setInterval(() => {
      setNotes(prevNotes =>
        prevNotes.map(note => {
          let newX = note.x + note.vx;
          let newY = note.y + note.vy;
          let newVx = note.vx;
          let newVy = note.vy;

          // Rebotar en los bordes
          if (newX <= 0 || newX >= window.innerWidth - note.size) {
            newVx = -note.vx;
            newX = newX <= 0 ? 0 : window.innerWidth - note.size;
          }
          if (newY <= 0 || newY >= window.innerHeight - note.size) {
            newVy = -note.vy;
            newY = newY <= 0 ? 0 : window.innerHeight - note.size;
          }

          return {
            ...note,
            x: newX,
            y: newY,
            vx: newVx,
            vy: newVy,
            rotation: (note.rotation + note.rotationSpeed) % 360,
          };
        })
      );
    }, 16); // ~60 FPS

    return () => clearInterval(animationFrame);
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
      {notes.map(note => (
        <div
          key={note.id}
          className="absolute text-cyan-300 font-bold transition-opacity"
          style={{
            left: `${note.x}px`,
            top: `${note.y}px`,
            fontSize: `${note.size}px`,
            opacity: note.opacity,
            transform: `rotate(${note.rotation}deg)`,
            textShadow: '0 0 30px rgba(34, 211, 238, 0.8), 0 0 60px rgba(34, 211, 238, 0.4)',
            filter: 'drop-shadow(0 0 8px rgba(34, 211, 238, 0.6))',
          }}
        >
          {note.symbol}
        </div>
      ))}
    </div>
  );
};

export default FloatingNotes;
