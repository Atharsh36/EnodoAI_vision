import React, { useState } from 'react';
import { Detection } from '../../types';

interface Props {
  imageUrl: string;
  detections: Detection[];
  selectedRegionIndex: number | null;
  onSelectRegion: (index: number) => void;
}

export const DetectionOverlay: React.FC<Props> = ({
  imageUrl,
  detections,
  selectedRegionIndex,
  onSelectRegion,
}) => {
  const [dimensions, setDimensions] = useState<{ width: number; height: number } | null>(null);

  return (
    <div className="relative inline-block w-full rounded-xl overflow-hidden bg-slate-900 border border-slate-200 shadow-md">
      <img
        src={imageUrl}
        alt="Endoscopic Frame"
        onLoad={(e) => {
          const img = e.currentTarget;
          if (img.naturalWidth && img.naturalHeight) {
            setDimensions({ width: img.naturalWidth, height: img.naturalHeight });
          }
        }}
        className="w-full h-auto object-contain block max-h-[500px] mx-auto"
      />

      {/* SVG Bounding Boxes Overlay with exact viewBox scaling */}
      <svg
        className="absolute inset-0 w-full h-full pointer-events-none"
        viewBox={dimensions ? `0 0 ${dimensions.width} ${dimensions.height}` : undefined}
        preserveAspectRatio="none"
      >
        {detections.map((det) => {
          const isSelected = selectedRegionIndex === det.region_index;
          const x = det.bbox.x1;
          const y = det.bbox.y1;
          const w = Math.max(1, det.bbox.x2 - det.bbox.x1);
          const h = Math.max(1, det.bbox.y2 - det.bbox.y1);

          // Calculate dynamic font and stroke sizing proportional to natural image dimensions
          const imgWidth = dimensions?.width || 1000;
          const strokeWidth = dimensions ? Math.max(3, Math.round(imgWidth * 0.004)) : 3;
          const fontSize = dimensions ? Math.max(14, Math.round(imgWidth * 0.022)) : 14;
          const labelPadding = Math.round(fontSize * 0.4);
          const labelHeight = fontSize + labelPadding * 2;
          const labelY = Math.max(labelHeight, y - 4);

          return (
            <g
              key={det.region_id || det.region_index}
              className="cursor-pointer pointer-events-auto transition-opacity hover:opacity-90"
              onClick={() => onSelectRegion(det.region_index)}
            >
              {/* ROI Box */}
              <rect
                x={x}
                y={y}
                width={w}
                height={h}
                fill={isSelected ? 'rgba(5, 150, 105, 0.28)' : 'rgba(16, 185, 129, 0.16)'}
                stroke={isSelected ? '#059669' : '#10b981'}
                strokeWidth={strokeWidth}
                strokeDasharray={isSelected ? 'none' : '8 4'}
                rx="6"
              />
              {/* Label Background Badge */}
              <rect
                x={x}
                y={labelY - labelHeight}
                width={Math.max(120, w)}
                height={labelHeight}
                fill="rgba(15, 23, 42, 0.85)"
                rx="4"
              />
              {/* Label Text */}
              {(() => {
                const conf = det.confidence ?? (det as any).detection_confidence ?? det.prediction?.class_confidence ?? 0.85;
                const confPercent = Math.round(conf * 100);
                return (
                  <text
                    x={x + labelPadding}
                    y={labelY - labelPadding - 2}
                    fill="#ffffff"
                    fontSize={fontSize}
                    fontWeight="bold"
                    className="font-mono"
                  >
                    R{det.region_index}: {det.class_name} ({confPercent}%)
                  </text>
                );
              })()}
            </g>
          );
        })}
      </svg>
    </div>
  );
};

