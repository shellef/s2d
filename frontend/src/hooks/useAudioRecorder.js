/**
 * Audio Recorder Hook - Captures audio and sends complete blobs.
 */

import { useState, useRef, useCallback } from 'react';

export function useAudioRecorder(onAudioChunk) {
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState(null);
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const chunksRef = useRef([]);
  const intervalRef = useRef(null);

  const startRecording = useCallback(async () => {
    try {
      setError(null);
      chunksRef.current = [];

      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000,
        }
      });

      streamRef.current = stream;

      const mimeType = 'audio/webm;codecs=opus';
      const mediaRecorder = new MediaRecorder(stream, { mimeType });

      // Collect ALL chunks
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      // When stopped, send complete blob
      mediaRecorder.onstop = () => {
        if (chunksRef.current.length > 0) {
          const completeBlob = new Blob(chunksRef.current, { type: mimeType });
          chunksRef.current = [];

          console.log('Sending complete audio:', completeBlob.size, 'bytes');

          const reader = new FileReader();
          reader.onloadend = () => {
            const base64 = reader.result.split(',')[1];
            if (onAudioChunk) {
              onAudioChunk(base64, 'webm');
            }
          };
          reader.readAsDataURL(completeBlob);
        }

        // Restart for next interval
        if (mediaRecorderRef.current && isRecording) {
          mediaRecorderRef.current.start();
        }
      };

      mediaRecorder.onerror = (error) => {
        console.error('MediaRecorder error:', error);
        setError('Recording error: ' + error.message);
      };

      mediaRecorder.start();
      mediaRecorderRef.current = mediaRecorder;
      setIsRecording(true);

      // Stop every 3 seconds to create complete files
      intervalRef.current = setInterval(() => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
          mediaRecorderRef.current.stop();
        }
      }, 3000);

      console.log('Recording started');

    } catch (err) {
      console.error('Error starting recording:', err);
      setError(err.message || 'Failed to start recording.');
      setIsRecording(false);
    }
  }, [onAudioChunk, isRecording]);

  const stopRecording = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current = null;
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }

    setIsRecording(false);
    console.log('Recording stopped');
  }, []);

  return {
    isRecording,
    error,
    audioFormat: 'webm',
    startRecording,
    stopRecording
  };
}

export default useAudioRecorder;
