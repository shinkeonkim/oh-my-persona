import type { ProcessImageOptions, ProcessImageResult } from '../workers/imageProcessor';

// Creates a worker and wraps the postMessage flow in a Promise
export function processImageFile(
  img: HTMLImageElement, 
  targetResolution: number, 
  invert: boolean
): Promise<ProcessImageResult> {
  return new Promise((resolve, reject) => {
    // Draw image to canvas to get ImageData
    const canvas = document.createElement('canvas');
    canvas.width = img.width;
    canvas.height = img.height;
    const ctx = canvas.getContext('2d');
    if (!ctx) {
      reject(new Error("Failed to get 2d context for image loader"));
      return;
    }
    
    ctx.drawImage(img, 0, 0);
    const imageData = ctx.getImageData(0, 0, img.width, img.height);

    // Create worker
    const worker = new Worker(new URL('../workers/imageProcessor.ts', import.meta.url), {
      type: 'module'
    });

    worker.onmessage = (e) => {
      if (e.data.error) {
        reject(new Error(e.data.error));
      } else {
        resolve(e.data as ProcessImageResult);
      }
      worker.terminate();
    };

    worker.onerror = (err) => {
      reject(err);
      worker.terminate();
    };

    const options: ProcessImageOptions = {
      imageData,
      width: img.width,
      height: img.height,
      targetResolution,
      invert
    };

    worker.postMessage(options);
  });
}
