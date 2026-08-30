import { useEffect, useRef } from 'react';
import type { ProcessImageResult } from '../workers/imageProcessor';

interface DiceArt2DProps {
  data: ProcessImageResult;
  invert: boolean;
}

export default function DiceArt2D({ data, invert }: DiceArt2DProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Define die pixel size for 2D rendering
    const dieSize = 10;
    const padding = 1;
    const step = dieSize + padding;

    canvas.width = data.gridWidth * step;
    canvas.height = data.gridHeight * step;

    // Background
    ctx.fillStyle = invert ? '#111827' : '#F3F4F6';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const dotRadius = invert ? dieSize * 0.12 : dieSize * 0.16;
    const center = dieSize / 2;
    const offset = dieSize * 0.25;

    // Pre-calculate dot positions relative to a die's top-left corner
    const drawDots = (val: number, xStart: number, yStart: number) => {
      ctx.fillStyle = invert ? '#fff' : '#111';
      
      const drawDot = (dx: number, dy: number) => {
        ctx.beginPath();
        ctx.arc(xStart + dx, yStart + dy, dotRadius, 0, Math.PI * 2);
        ctx.fill();
      };

      if (val === 1 || val === 3 || val === 5) drawDot(center, center);
      if (val > 1) {
        drawDot(center - offset, center - offset);
        drawDot(center + offset, center + offset);
      }
      if (val > 3) {
        drawDot(center + offset, center - offset);
        drawDot(center - offset, center + offset);
      }
      if (val === 6) {
        drawDot(center - offset, center);
        drawDot(center + offset, center);
      }
    };

    // Draw grid
    for (let y = 0; y < data.gridHeight; y++) {
      for (let x = 0; x < data.gridWidth; x++) {
        const i = y * data.gridWidth + x;
        const val = data.diceValues[i];
        
        const px = x * step;
        const py = y * step;

        // Draw Die Background
        ctx.fillStyle = invert ? '#222' : '#fff';
        ctx.fillRect(px, py, dieSize, dieSize);

        ctx.strokeStyle = invert ? '#444' : '#ddd';
        ctx.lineWidth = 1;
        ctx.strokeRect(px, py, dieSize, dieSize);

        drawDots(val, px, py);
      }
    }
  }, [data, invert]);

  return (
    <div className="w-full h-full overflow-auto flex items-center justify-center bg-gray-950 p-8">
      <div className="shadow-2xl rounded" style={{ backgroundColor: invert ? '#111' : '#f0f0f0' }}>
        <canvas ref={canvasRef} className="block" />
      </div>
    </div>
  );
}
