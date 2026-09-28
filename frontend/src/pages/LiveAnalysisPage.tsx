import React, { useRef, useEffect, useState } from 'react';
import { Radio, Zap, Eye, Gauge, Play, Square } from 'lucide-react';
import { useLiveAnalysis } from '../hooks/useLiveAnalysis';

export const LiveAnalysisPage: React.FC = () => {
  const { connected, mode, setMode, frameSkip, setFrameSkip, latestFrame, sendFrame } = useLiveAnalysis();
  const [streaming, setStreaming] = useState(false);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const intervalRef = useRef<any>(null);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
        setStreaming(true);
      }
    } catch (err) {
      console.error('Camera access error:', err);
      alert('Unable to access webcam. Please check browser camera permissions.');
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach((track) => track.stop());
      videoRef.current.srcObject = null;
    }
    setStreaming(false);
    if (intervalRef.current) clearInterval(intervalRef.current);
  };

  useEffect(() => {
    if (streaming) {
      intervalRef.current = setInterval(() => {
        if (videoRef.current && canvasRef.current) {
          const video = videoRef.current;
          const canvas = canvasRef.current;
          const ctx = canvas.getContext('2d');

          if (ctx && video.videoWidth > 0) {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            const base64 = canvas.toDataURL('image/jpeg', 0.7);
            sendFrame(base64);
          }
        }
      }, 100); // Send frame every 100ms (~10 FPS capture rate)
    } else {
      if (intervalRef.current) clearInterval(intervalRef.current);
    }

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [streaming, sendFrame]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-bold text-slate-900">Real-Time Live Analysis</h1>
            <span
              className={`px-2.5 py-0.5 rounded-full text-xs font-mono font-bold flex items-center space-x-1.5 border ${
                streaming
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                  : 'bg-slate-100 text-slate-600 border-slate-200'
              }`}
            >
              <span className={`w-2 h-2 rounded-full ${streaming ? 'bg-emerald-600 animate-ping' : 'bg-slate-400'}`}></span>
              <span>{streaming ? 'LIVE STREAM ACTIVE' : 'STREAM STANDBY'}</span>
            </span>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Real-time optical frame processing over WebSockets with latency metrics & frame skipping
          </p>
        </div>

        {/* Telemetry Metrics */}
        <div className="flex items-center space-x-3 font-mono text-xs">
          <div className="px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-700 shadow-2xs">
            FPS: <strong className="text-emerald-700">{latestFrame?.fps || '0.0'}</strong>
          </div>
          <div className="px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-700 shadow-2xs">
            Latency: <strong className="text-emerald-700">{latestFrame?.latency_ms ? `${latestFrame.latency_ms} ms` : '0 ms'}</strong>
          </div>
          <div className="px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-700 shadow-2xs">
            WS: <strong className={connected ? 'text-emerald-700 font-bold' : 'text-rose-600 font-bold'}>{connected ? 'Online' : 'Offline'}</strong>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Live Canvas / Video Container */}
        <div className="lg:col-span-2 glass-panel p-4 flex flex-col justify-between min-h-[460px] relative overflow-hidden bg-white border-slate-200">
          <video ref={videoRef} className="hidden" playsInline muted />
          <canvas ref={canvasRef} className="hidden" />

          {streaming ? (
            <div className="relative rounded-xl overflow-hidden bg-slate-900 border border-slate-200">
              <video
                ref={(el) => {
                  if (el && videoRef.current?.srcObject) {
                    el.srcObject = videoRef.current.srcObject;
                    el.play();
                  }
                }}
                className="w-full h-auto max-h-[440px] object-contain block mx-auto"
                autoPlay
                playsInline
                muted
              />

              {/* Real-time bounding box overlay */}
              {latestFrame && latestFrame.detections && (
                <div className="absolute inset-0 pointer-events-none">
                  <svg className="w-full h-full" viewBox="0 0 640 480" preserveAspectRatio="none">
                    {latestFrame.detections.map((det) => {
                      const x = det.bbox.x1;
                      const y = det.bbox.y1;
                      const w = Math.max(1, det.bbox.x2 - det.bbox.x1);
                      const h = Math.max(1, det.bbox.y2 - det.bbox.y1);
                      return (
                        <g key={det.region_id}>
                          <rect
                            x={x}
                            y={y}
                            width={w}
                            height={h}
                            fill="rgba(5, 150, 105, 0.28)"
                            stroke="#059669"
                            strokeWidth="3"
                            rx="4"
                          />
                          <rect
                            x={x}
                            y={Math.max(0, y - 20)}
                            width={Math.max(100, w)}
                            height="20"
                            fill="rgba(15, 23, 42, 0.85)"
                            rx="3"
                          />
                          <text
                            x={x + 4}
                            y={Math.max(14, y - 5)}
                            fill="#ffffff"
                            fontSize="12"
                            fontWeight="bold"
                            className="font-mono"
                          >
                            {det.class_name} ({Math.round(det.confidence * 100)}%)
                          </text>
                        </g>
                      );
                    })}
                  </svg>
                </div>
              )}
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center border border-dashed border-slate-300 rounded-xl py-16 bg-slate-50/50">
              <Radio className="w-12 h-12 text-emerald-600 opacity-60 mb-3 animate-pulse" />
              <h3 className="font-bold text-slate-900 text-sm">Live Camera / Stream Inactive</h3>
              <p className="text-xs text-slate-500 max-w-sm text-center mt-1 mb-4">
                Click Start Stream below to connect your webcam feed to the real-time WebSocket analysis pipeline.
              </p>
              <button
                onClick={startCamera}
                className="btn-primary"
              >
                <Play className="w-4 h-4 fill-current" />
                <span>Start Live Webcam Feed</span>
              </button>
            </div>
          )}

          {/* Control Bar */}
          {streaming && (
            <div className="mt-4 flex items-center justify-between border-t border-slate-200 pt-3">
              <button
                onClick={stopCamera}
                className="px-4 py-2 rounded-xl bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 font-semibold text-xs transition flex items-center space-x-2"
              >
                <Square className="w-3.5 h-3.5 fill-current" />
                <span>Stop Stream</span>
              </button>

              <span className="text-xs font-mono text-slate-600">
                Frame #{latestFrame?.frame_number || 0} • Quality: <strong className="text-emerald-700">{latestFrame?.quality?.overall_quality || 'GOOD'}</strong>
              </span>
            </div>
          )}
        </div>

        {/* Stream Settings Panel */}
        <div className="glass-panel p-5 space-y-6 bg-white border-slate-200">
          <h3 className="font-bold text-sm text-slate-900 border-b border-slate-200 pb-3 flex items-center space-x-2">
            <Gauge className="w-4 h-4 text-emerald-600" />
            <span>Stream Mode & Performance</span>
          </h3>

          <div className="space-y-3">
            <label className="text-xs text-slate-600 font-medium block">Processing Mode:</label>
            <div className="grid grid-cols-2 gap-2 font-mono text-xs font-semibold">
              <button
                type="button"
                onClick={() => setMode('FAST')}
                className={`p-3 rounded-xl border flex items-center justify-center space-x-2 transition ${
                  mode === 'FAST'
                    ? 'bg-emerald-50 border-emerald-500 text-emerald-800 shadow-xs'
                    : 'bg-white border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                <Zap className="w-4 h-4 text-emerald-600" />
                <span>FAST MODE</span>
              </button>

              <button
                type="button"
                onClick={() => setMode('EXPLAINABLE')}
                className={`p-3 rounded-xl border flex items-center justify-center space-x-2 transition ${
                  mode === 'EXPLAINABLE'
                    ? 'bg-emerald-50 border-emerald-500 text-emerald-800 shadow-xs'
                    : 'bg-white border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                <Eye className="w-4 h-4 text-emerald-600" />
                <span>EXPLAINABLE</span>
              </button>
            </div>
          </div>

          <div className="space-y-2 text-xs font-mono">
            <div className="flex justify-between text-slate-700 font-medium">
              <span>Frame Skip Ratio:</span>
              <span className="text-emerald-700 font-bold">Every {frameSkip} frame(s)</span>
            </div>
            <input
              type="range"
              min="1"
              max="5"
              step="1"
              value={frameSkip}
              onChange={(e) => setFrameSkip(parseInt(e.target.value))}
              className="w-full accent-emerald-600"
            />
          </div>

          {latestFrame?.quality && (
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-2 text-xs font-mono">
              <div className="flex justify-between text-slate-700">
                <span>Blur Score:</span>
                <span className="text-emerald-700 font-bold">{latestFrame.quality.blur_score.toFixed(1)}</span>
              </div>
              <div className="flex justify-between text-slate-700">
                <span>Brightness:</span>
                <span className="text-amber-700 font-bold">{latestFrame.quality.brightness_score.toFixed(1)}</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
