// components/PianoTranscription.js
//
// Componente React para transcripción de piano con barra de progreso en tiempo real

import React, { useState, useEffect, useRef } from 'react';

const PianoTranscription = () => {
  const [file, setFile] = useState(null);
  const [taskId, setTaskId] = useState(null);
  const [status, setStatus] = useState('idle'); // idle, uploading, processing, completed, error
  const [message, setMessage] = useState('');
  const [error, setError] = useState(null);
  const [hasPdf, setHasPdf] = useState(false);
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
          
  // Referencia para el intervalo de polling
  const pollingTimeoutRef = useRef(null);
  
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://pt-api.whitewater-3f1ca299.centralus.azurecontainerapps.io/api/v1';

  // Limpiar intervalo cuando el componente se desmonte
  useEffect(() => {
    return () => {
      clearPollingTimer();
      console.log('🧹 Polling limpiado al desmontar componente');
    };
  }, []);

  const clearPollingTimer = () => {
    if (pollingTimeoutRef.current) {
      clearTimeout(pollingTimeoutRef.current);
      pollingTimeoutRef.current = null;
    }
  };

  // Validar y procesar archivo
  const processFile = (selectedFile) => {
    if (selectedFile) {
      // Validar formato - SOLO WAV
      const fileExtension = '.' + selectedFile.name.split('.').pop().toLowerCase();
      
      if (fileExtension === '.wav') {
        setFile(selectedFile);
        setError(null);
      } else {
        setError('Formato de audio no soportado. Solo se permiten archivos WAV.');
        setFile(null);
      }
    }
  };

  // Manejar selección de archivo
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    processFile(selectedFile);
  };

  // Manejar drag over
  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  // Manejar drag leave
  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  // Manejar drop
  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const droppedFile = e.dataTransfer.files[0];
    processFile(droppedFile);
  };

  // Iniciar transcripción
  const startTranscription = async () => {
    if (!file) {
      setError('Por favor selecciona un archivo de audio.');
      return;
    }

    if (!acceptTerms) {
      setError('Debes aceptar los términos para continuar.');
      return;
    }

    setStatus('uploading');
    setMessage('Subiendo archivo...');
    setError(null);

    try {
      // 1. Subir archivo e iniciar transcripción
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE_URL}/transcribe/`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al iniciar transcripción');
      }

      const data = await response.json();
      setTaskId(data.task_id);
      setStatus('processing');
      setMessage('Transcripción en proceso...');

      // 2. Iniciar polling para verificar el estado
      startPolling(data.task_id);

    } catch (err) {
      setStatus('error');
      setError(err.message);
      setMessage('Error al procesar el archivo');
    }
  };

  // Polling para verificar el estado
  const startPolling = (taskId) => {
    clearPollingTimer();

    let consecutiveErrors = 0;
    const maxErrors = 5; // Máximo de errores consecutivos antes de abortar

    const scheduleNextPoll = () => {
      pollingTimeoutRef.current = setTimeout(poll, 6000);
    };

    const poll = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/transcribe/status/${taskId}`);

        if (response.status === 404) {
          consecutiveErrors++;
          console.log(`⚠️ Tarea no encontrada (${consecutiveErrors}/${maxErrors})`);

          if (consecutiveErrors >= maxErrors) {
            setStatus('error');
            setError('La tarea no se encontró después de varios intentos');
            setMessage('No pudimos recuperar el estado de la transcripción.');
            clearPollingTimer();
            return;
          }

          setMessage('El servidor sigue preparando tu transcripción, reintentando...');
          scheduleNextPoll();
          return;
        }

        if (!response.ok) {
          throw new Error(`Error del servidor: ${response.status}`);
        }

        const data = await response.json();
        consecutiveErrors = 0;
        setMessage(data.message);
        setHasPdf(data.has_pdf);

        if (data.status === 'completed') {
          setStatus('completed');
          clearPollingTimer();
          console.log('✅ Transcripción completada - polling detenido');
          return;
        }

        if (data.status === 'failed') {
          setStatus('error');
          setError(data.error || 'La transcripción falló');
          clearPollingTimer();
          console.log('❌ Transcripción fallida - polling detenido');
          return;
        }

        console.log(`⏳ Estado: ${data.status} - ${data.message}`);
        scheduleNextPoll();
      } catch (err) {
        consecutiveErrors++;
        console.error('Error en polling:', err);

        if (consecutiveErrors >= maxErrors) {
          setStatus('error');
          setError(err.message || 'Error al verificar el estado de la transcripción');
          clearPollingTimer();
          return;
        }

        setMessage('Estamos teniendo demoras con el servidor, seguimos intentando...');
        scheduleNextPoll();
      }
    };

    // Primer intento con una pequeña espera para darle tiempo al backend
    pollingTimeoutRef.current = setTimeout(poll, 1000);
  };

  // Descargar PDF
  const downloadPdf = () => {
    if (taskId) {
      const downloadUrl = `${API_BASE_URL}/transcribe/download/pdf/${taskId}`;
      console.log('Descargando PDF desde:', downloadUrl);
      window.open(downloadUrl, '_blank');
    }
  };

  // Reiniciar
  const reset = () => {
    // Limpiar polling si existe
    clearPollingTimer();
    console.log('🧹 Polling limpiado en reset');
    
    setFile(null);
    setTaskId(null);
    setStatus('idle');
    setMessage('');
    setError(null);
    setHasPdf(false);
    setAcceptTerms(false);
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Card principal con diseño mejorado */}
      <div className="bg-slate-800/50 backdrop-blur-sm rounded-3xl shadow-2xl border border-slate-700/50 overflow-hidden">
        {/* Header del card */}
        <div className="bg-gradient-to-r from-blue-900/50 to-slate-800/50 px-6 py-4 border-b border-slate-700/50">
          <div className="flex items-center justify-center space-x-2">
            <h2 className="text-xl md:text-2xl font-bold text-white">
              Transcripción Automática de Piano
            </h2>
          </div>
        </div>

        {/* Contenido principal */}
        <div className="p-6 md:p-8">
          {/* Selector de archivo */}
          {status === 'idle' && (
            <div className="space-y-4">
              {/* Área de carga con ilustración de piano */}
              <div 
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`relative border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-300 ${
                  isDragging
                    ? 'bg-cyan-900/30 border-cyan-400 scale-[1.02]'
                    : 'bg-slate-900/50 border-cyan-500/50 hover:border-cyan-400 hover:bg-slate-900/70'
                }`}
              >
                <input
                  type="file"
                  accept=".wav"
                  onChange={handleFileChange}
                  className="hidden"
                  id="audio-upload"
                />
                <label htmlFor="audio-upload" className="cursor-pointer block">
                  {/* Ilustración de piano con ondas */}
                  <div className="mb-4 flex justify-center">
                    <div className="relative">
                      {/* Ondas de sonido animadas */}
                      <div className="absolute -left-10 top-1/2 transform -translate-y-1/2">
                        <div className="flex space-x-1">
                          <div className="w-1 h-6 bg-cyan-400 rounded-full animate-pulse"></div>
                          <div className="w-1 h-10 bg-cyan-400 rounded-full animate-pulse" style={{animationDelay: '0.1s'}}></div>
                          <div className="w-1 h-5 bg-cyan-400 rounded-full animate-pulse" style={{animationDelay: '0.2s'}}></div>
                        </div>
                      </div>
                      
                      {/* Teclas de piano */}
                      <div className="flex space-x-1.5">
                        <div className="w-10 h-24 bg-gradient-to-b from-white to-gray-50 rounded-b-xl shadow-2xl border-2 border-cyan-400"></div>
                        <div className="w-10 h-24 bg-gradient-to-b from-slate-600 to-slate-900 rounded-b-xl shadow-2xl border-2 border-cyan-400"></div>
                        <div className="w-10 h-24 bg-gradient-to-b from-white to-gray-50 rounded-b-xl shadow-2xl border-2 border-cyan-400"></div>
                        <div className="w-10 h-24 bg-gradient-to-b from-slate-600 to-slate-900 rounded-b-xl shadow-2xl border-2 border-cyan-400"></div>
                        <div className="w-10 h-24 bg-gradient-to-b from-white to-gray-50 rounded-b-xl shadow-2xl border-2 border-cyan-400"></div>
                        <div className="w-10 h-24 bg-gradient-to-b from-white to-gray-50 rounded-b-xl shadow-2xl border-2 border-cyan-400"></div>
                        <div className="w-10 h-24 bg-gradient-to-b from-slate-600 to-slate-900 rounded-b-xl shadow-2xl border-2 border-cyan-400"></div>
                      </div>

                      {/* Ondas de sonido derecha */}
                      <div className="absolute -right-10 top-1/2 transform -translate-y-1/2">
                        <div className="flex space-x-1">
                          <div className="w-1 h-5 bg-cyan-400 rounded-full animate-pulse" style={{animationDelay: '0.3s'}}></div>
                          <div className="w-1 h-10 bg-cyan-400 rounded-full animate-pulse" style={{animationDelay: '0.4s'}}></div>
                          <div className="w-1 h-6 bg-cyan-400 rounded-full animate-pulse" style={{animationDelay: '0.5s'}}></div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <p className="text-white text-base font-medium mb-1">
                    {file ? `📁 ${file.name}` : isDragging ? '¡Suelta el archivo aquí!' : 'Haz clic o arrastra un archivo'}
                  </p>
                  <p className="text-blue-300 text-sm">
                    Solo archivos WAV
                  </p>
                </label>
              </div>

              {/* Checkbox de términos y condiciones */}
              <div className="bg-blue-900/30 border border-blue-500/50 rounded-xl p-4">
                <label className="flex items-start space-x-3 cursor-pointer group">
                  <input
                    type="checkbox"
                    checked={acceptTerms}
                    onChange={(e) => setAcceptTerms(e.target.checked)}
                    className="mt-1 w-5 h-5 rounded border-2 border-cyan-400 bg-slate-800 text-cyan-500 focus:ring-2 focus:ring-cyan-400 focus:ring-offset-0 cursor-pointer"
                  />
                  <div className="flex-1">
                    <p className="text-sm text-blue-200 leading-relaxed">
                      Confirmo que mi archivo es un audio en <strong className="text-cyan-300">formato WAV</strong> que contiene <strong className="text-cyan-300">únicamente una interpretación de piano</strong> (sin otros instrumentos o voces), 
                      con <strong className="text-cyan-300">audio limpio y mínimo ruido de fondo</strong>, 
                      para garantizar la mejor calidad en la transcripción automática.
                    </p>
                  </div>
                </label>
              </div>

              {/* Botón principal estilo cyan */}
              <button
                onClick={startTranscription}
                disabled={!file || !acceptTerms}
                className={`w-full py-3 px-6 rounded-xl font-bold text-base transition-all duration-300 transform ${
                  file && acceptTerms
                    ? 'bg-cyan-500 hover:bg-cyan-400 text-slate-900 shadow-lg shadow-cyan-500/50 hover:shadow-cyan-400/50 hover:scale-[1.02]'
                    : 'bg-slate-700 text-slate-500 cursor-not-allowed'
                }`}
              >
                Transcribir Ahora
              </button>
            </div>
          )}

          {/* Estado de procesamiento */}
          {(status === 'uploading' || status === 'processing') && (
            <div className="space-y-6">
              <div className="bg-blue-900/30 border border-cyan-500/50 rounded-2xl p-8">
                <div className="flex items-center justify-center mb-6">
                  <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-cyan-500"></div>
                </div>
                
                <p className="text-center text-white font-bold text-xl mb-3">
                  {status === 'uploading' ? 'Subiendo archivo...' : 'Procesando transcripción...'}
                </p>
                
                <p className="text-base text-blue-200 text-center">{message}</p>
                
                {/* Animación de puntos saltando */}
                <div className="flex justify-center mt-4">
                  <div className="flex space-x-2">
                    <div className="w-3 h-3 bg-cyan-400 rounded-full animate-bounce"></div>
                    <div className="w-3 h-3 bg-cyan-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                    <div className="w-3 h-3 bg-cyan-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  </div>
                </div>
                
                <p className="text-sm text-blue-300/70 text-center mt-6">
                  Este proceso puede tardar varios minutos dependiendo de la duración del audio
                </p>
              </div>
            </div>
          )}

          {/* Resultado completado */}
          {status === 'completed' && (
            <div className="space-y-6">
              <div className="bg-green-900/20 border border-green-500/50 rounded-2xl p-6">
                <div className="flex items-center justify-center mb-4">
                  <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center">
                    <svg
                      className="h-8 w-8 text-green-400"
                      fill="none"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path d="M5 13l4 4L19 7"></path>
                    </svg>
                  </div>
                </div>
                
                <p className="text-green-300 font-bold text-xl text-center mb-4">
                  ¡Transcripción completada exitosamente!
                </p>
              </div>

              <button
                onClick={downloadPdf}
                disabled={!hasPdf}
                className={`w-full py-4 px-6 rounded-xl font-bold text-lg transition-all duration-300 transform ${
                  hasPdf
                    ? 'bg-cyan-500 hover:bg-cyan-400 text-slate-900 shadow-lg shadow-cyan-500/50 hover:shadow-cyan-400/50 hover:scale-[1.02]'
                    : 'bg-slate-700 text-slate-500 cursor-not-allowed'
                }`}
              >
                Descargar Partitura PDF
              </button>

              {!hasPdf && (
                <p className="text-xs text-blue-300/70 text-center">
                  * La partitura PDF puede no estar disponible si no está instalado MuseScore en el servidor
                </p>
              )}

              <button
                onClick={reset}
                className="w-full py-3 px-4 rounded-xl font-semibold text-white bg-slate-700 hover:bg-slate-600 transition-colors border border-slate-600"
              >
                Nueva Transcripción
              </button>
            </div>
          )}

          {/* Error */}
          {status === 'error' && (
            <div className="space-y-6">
              <div className="bg-red-900/20 border border-red-500/50 rounded-2xl p-6">
                <div className="flex items-center justify-center mb-4">
                  <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center">
                    <svg
                      className="h-8 w-8 text-red-400"
                      fill="none"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                  </div>
                </div>
                
                <p className="text-red-300 font-bold text-xl text-center mb-3">Error en la transcripción</p>
                <p className="text-base text-red-200 text-center bg-slate-900/50 rounded-xl p-4">{error}</p>
              </div>

              <button
                onClick={reset}
                className="w-full py-4 px-6 rounded-xl font-bold text-lg bg-cyan-500 hover:bg-cyan-400 text-slate-900 transition-all duration-300 transform hover:scale-[1.02] shadow-lg shadow-cyan-500/50"
              >
                Intentar de Nuevo
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PianoTranscription;
