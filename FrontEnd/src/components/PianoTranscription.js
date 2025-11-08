// components/PianoTranscription.js
//
// Componente React para transcripción de piano con barra de progreso en tiempo real

import React, { useState, useEffect, useRef } from 'react';

const PianoTranscription = () => {
  const [file, setFile] = useState(null);
  const [taskId, setTaskId] = useState(null);
  const [status, setStatus] = useState('idle'); // idle, uploading, processing, completed, error
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('');
  const [error, setError] = useState(null);
  const [transcriptionInfo, setTranscriptionInfo] = useState(null);
  const [hasPdf, setHasPdf] = useState(false);
  
  const eventSourceRef = useRef(null);
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://pt-api.whitewater-3f1ca299.centralus.azurecontainerapps.io/api/v1';

  // Limpiar EventSource al desmontar
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  // Manejar selección de archivo
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
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

  // Iniciar transcripción
  const startTranscription = async () => {
    if (!file) {
      setError('Por favor selecciona un archivo de audio.');
      return;
    }

    setStatus('uploading');
    setProgress(0);
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
      setMessage('Transcripción iniciada...');

      // 2. Conectar a SSE para recibir progreso en tiempo real
      connectToProgressStream(data.task_id);

    } catch (err) {
      setStatus('error');
      setError(err.message);
      setMessage('Error al procesar el archivo');
    }
  };

  // Conectar a Server-Sent Events para progreso en tiempo real
  const connectToProgressStream = (taskId) => {
    const eventSource = new EventSource(`${API_BASE_URL}/transcribe/stream/${taskId}`);
    eventSourceRef.current = eventSource;

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      setProgress(data.progress);
      setMessage(data.message);

      if (data.status === 'completed') {
        setStatus('completed');
        eventSource.close();
        
        // Consultar info final
        fetchFinalStatus(taskId);
      } else if (data.status === 'failed') {
        setStatus('error');
        setError(data.message);
        eventSource.close();
      }
    };

    eventSource.onerror = () => {
      console.error('Error en SSE, cambiando a polling...');
      eventSource.close();
      
      // Fallback a polling si SSE falla
      startPolling(taskId);
    };
  };

  // Polling como fallback
  const startPolling = (taskId) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/transcribe/status/${taskId}`);
        const data = await response.json();

        setProgress(data.progress);
        setMessage(data.message);
        setHasPdf(data.has_pdf);

        if (data.status === 'completed') {
          setStatus('completed');
          setTranscriptionInfo(data.transcription_info);
          clearInterval(interval);
        } else if (data.status === 'failed') {
          setStatus('error');
          setError(data.error);
          clearInterval(interval);
        }
      } catch (err) {
        console.error('Error en polling:', err);
      }
    }, 1000); // Polling cada 1 segundo
  };

  // Obtener información final
  const fetchFinalStatus = async (taskId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/transcribe/status/${taskId}`);
      const data = await response.json();
      
      setTranscriptionInfo(data.transcription_info);
      setHasPdf(data.has_pdf);
    } catch (err) {
      console.error('Error al obtener estado final:', err);
    }
  };

  // Descargar PDF
  const downloadPdf = () => {
    if (taskId) {
      window.open(`${API_BASE_URL}/transcribe/download/pdf/${taskId}`, '_blank');
    }
  };

  // Reiniciar
  const reset = () => {
    setFile(null);
    setTaskId(null);
    setStatus('idle');
    setProgress(0);
    setMessage('');
    setError(null);
    setTranscriptionInfo(null);
    setHasPdf(false);
    
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-8 bg-gray-800 rounded-xl shadow-2xl border border-gray-700">
      <h2 className="text-3xl font-bold text-center mb-6 text-white">
        🎹 Transcripción Automática de Piano
      </h2>

      {/* Selector de archivo */}
      {status === 'idle' && (
        <div className="space-y-4">
          <div className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center hover:border-yellow-500 transition-colors bg-gray-700/30">
            <input
              type="file"
              accept=".wav"
              onChange={handleFileChange}
              className="hidden"
              id="audio-upload"
            />
            <label
              htmlFor="audio-upload"
              className="cursor-pointer block"
            >
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                stroke="currentColor"
                fill="none"
                viewBox="0 0 48 48"
              >
                <path
                  d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                  strokeWidth={2}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              <span className="mt-2 block text-sm font-medium text-white">
                {file ? file.name : 'Selecciona un archivo de audio WAV'}
              </span>
              <span className="mt-1 block text-xs text-gray-400">
                Solo archivos WAV
              </span>
            </label>
          </div>

          <button
            onClick={startTranscription}
            disabled={!file}
            className={`w-full py-3 px-4 rounded-lg font-semibold transition-colors ${
              file
                ? 'bg-yellow-500 hover:bg-yellow-400 text-gray-900'
                : 'bg-gray-600 text-gray-400 cursor-not-allowed'
            }`}
          >
            Iniciar Transcripción
          </button>
        </div>
      )}

      {/* Barra de progreso */}
      {(status === 'uploading' || status === 'processing') && (
        <div className="space-y-4">
          <div className="relative pt-1">
            <div className="flex mb-2 items-center justify-between">
              <div>
                <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-yellow-900 bg-yellow-500">
                  {status === 'uploading' ? 'Subiendo' : 'Procesando'}
                </span>
              </div>
              <div className="text-right">
                <span className="text-xs font-semibold inline-block text-yellow-400">
                  {progress}%
                </span>
              </div>
            </div>
            <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-gray-700">
              <div
                style={{ width: `${progress}%` }}
                className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-yellow-500 transition-all duration-300"
              />
            </div>
          </div>

          <p className="text-sm text-gray-300 text-center">{message}</p>

          {/* Animación de carga */}
          <div className="flex justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-yellow-500"></div>
          </div>
        </div>
      )}

      {/* Resultado completado */}
      {status === 'completed' && (
        <div className="space-y-4">
          <div className="bg-green-900/30 border border-green-500 rounded-lg p-4">
            <div className="flex items-center">
              <svg
                className="h-6 w-6 text-green-400 mr-3"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M5 13l4 4L19 7"></path>
              </svg>
              <p className="text-green-300 font-semibold">
                ¡Transcripción completada exitosamente!
              </p>
            </div>

            {transcriptionInfo && (
              <div className="mt-3 text-sm text-green-400 space-y-1">
                <p>⏱️ Duración: {transcriptionInfo.duration_seconds.toFixed(2)} segundos</p>
                <p>🎵 Notas detectadas: {transcriptionInfo.total_notes}</p>
                <p>📊 Frames procesados: {transcriptionInfo.total_frames}</p>
              </div>
            )}
          </div>

          <button
            onClick={downloadPdf}
            disabled={!hasPdf}
            className={`w-full py-4 px-6 rounded-lg font-bold text-lg transition-colors ${
              hasPdf
                ? 'bg-red-600 hover:bg-red-500 text-white shadow-lg'
                : 'bg-gray-600 text-gray-400 cursor-not-allowed'
            }`}
          >
            📄 Descargar Partitura
          </button>

          {!hasPdf && (
            <p className="text-xs text-gray-400 text-center">
              * La partitura PDF puede no estar disponible si no está instalado MuseScore en el servidor
            </p>
          )}

          <button
            onClick={reset}
            className="w-full py-2 px-4 rounded-lg font-semibold text-gray-900 bg-gray-300 hover:bg-gray-200 transition-colors"
          >
            Nueva Transcripción
          </button>
        </div>
      )}

      {/* Error */}
      {status === 'error' && (
        <div className="space-y-4">
          <div className="bg-red-900/30 border border-red-500 rounded-lg p-4">
            <div className="flex items-center">
              <svg
                className="h-6 w-6 text-red-400 mr-3"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M6 18L18 6M6 6l12 12"></path>
              </svg>
              <p className="text-red-300 font-semibold">Error en la transcripción</p>
            </div>
            <p className="mt-2 text-sm text-red-400">{error}</p>
          </div>

          <button
            onClick={reset}
            className="w-full py-2 px-4 rounded-lg font-semibold text-gray-900 bg-yellow-500 hover:bg-yellow-400 transition-colors"
          >
            Intentar de nuevo
          </button>
        </div>
      )}
    </div>
  );
};

export default PianoTranscription;
