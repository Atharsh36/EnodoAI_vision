import { useState, useEffect, useRef, useCallback } from 'react';
import { QualityMetrics, Detection } from '../types';

export interface LiveAnalysisFrame {
  frame_number: number;
  mode: 'FAST' | 'EXPLAINABLE';
  fps: number;
  latency_ms: number;
  detection_latency_ms: number;
  quality: QualityMetrics;
  detections: Detection[];
  skipped?: boolean;
}

export const useLiveAnalysis = () => {
  const [connected, setConnected] = useState(false);
  const [mode, setMode] = useState<'FAST' | 'EXPLAINABLE'>('FAST');
  const [frameSkip, setFrameSkip] = useState<number>(1);
  const [latestFrame, setLatestFrame] = useState<LiveAnalysisFrame | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/live-analysis`;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      ws.send(JSON.stringify({ mode, frame_skip: frameSkip }));
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.frame_number) {
          setLatestFrame(data);
        }
      } catch (err) {
        console.error('WS parse error:', err);
      }
    };

    ws.onclose = () => {
      setConnected(false);
    };

    return () => {
      ws.close();
    };
  }, []);

  const sendFrame = useCallback((base64Frame: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        mode,
        frame_skip: frameSkip,
        frame: base64Frame
      }));
    }
  }, [mode, frameSkip]);

  const updateMode = useCallback((newMode: 'FAST' | 'EXPLAINABLE') => {
    setMode(newMode);
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ mode: newMode, frame_skip: frameSkip }));
    }
  }, [frameSkip]);

  return {
    connected,
    mode,
    setMode: updateMode,
    frameSkip,
    setFrameSkip,
    latestFrame,
    sendFrame
  };
};
