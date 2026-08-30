// Web Worker for processing images
// Translates pixels into dice values (1-6)

export interface ProcessImageOptions {
  imageData: ImageData;
  width: number;
  height: number;
  targetResolution: number; // Target width in dice count
  invert: boolean;
}

export interface ProcessImageResult {
  diceValues: number[]; // 1D array of dice values (1-6)
  gridWidth: number;
  gridHeight: number;
}

self.onmessage = async (e: MessageEvent<ProcessImageOptions>) => {
  const { imageData, width, height, targetResolution, invert } = e.data;

  // 1. Calculate target dimensions to maintain aspect ratio
  const aspectRatio = height / width;
  const gridWidth = targetResolution;
  const gridHeight = Math.round(gridWidth * aspectRatio);

  // 2. Resize image using OffscreenCanvas
  const canvas = new OffscreenCanvas(gridWidth, gridHeight);
  const ctx = canvas.getContext('2d', { willReadFrequently: true });
  
  if (!ctx) {
    self.postMessage({ error: 'Failed to get 2d context for OffscreenCanvas' });
    return;
  }

  const bitmap = await createImageBitmap(imageData);
  ctx.drawImage(bitmap, 0, 0, width, height, 0, 0, gridWidth, gridHeight);
  bitmap.close();

  const scaledImageData = ctx.getImageData(0, 0, gridWidth, gridHeight);
  const data = scaledImageData.data;

  const pixels = new Float32Array(gridWidth * gridHeight);
  
  // 3. Convert to Grayscale and find Min/Max for Auto Contrast
  let minLuma = 255;
  let maxLuma = 0;

  for (let i = 0; i < gridWidth * gridHeight; i++) {
    const idx = i * 4;
    const r = data[idx];
    const g = data[idx + 1];
    const b = data[idx + 2];
    
    // Improved perceptual luma
    const luma = 0.299 * r + 0.587 * g + 0.114 * b;
    pixels[i] = luma;

    if (luma < minLuma) minLuma = luma;
    if (luma > maxLuma) maxLuma = luma;
  }

  // 4. Auto Contrast Auto-Stretch (Normalization)
  // To avoid stretching extreme outliers too much, we could use percentiles, but min/max is usually fine for this art.
  // We can also apply a slight gamma curve to boost midtones for the white background.
  const range = maxLuma - minLuma === 0 ? 1 : maxLuma - minLuma;
  
  for (let i = 0; i < pixels.length; i++) {
    // Normalize to 0-255
    let stretched = ((pixels[i] - minLuma) / range) * 255;
    
    // Non-linear gamma curve to increase contrast depending on mode
    // For white background (invert=false), darks need to be darker.
    // For black background (invert=true), brights need to be brighter.
    const normalized = stretched / 255;
    let gamma = invert ? 0.8 : 1.25; 
    
    pixels[i] = Math.max(0, Math.min(255, Math.pow(normalized, gamma) * 255));
  }

  // Quantization steps
  const levels = 6;
  const step = 255 / (levels - 1); // 51

  // Floyd-Steinberg Dithering
  for (let y = 0; y < gridHeight; y++) {
    for (let x = 0; x < gridWidth; x++) {
      const idx = y * gridWidth + x;
      const oldPixel = pixels[idx];
      
      const quantIndex = Math.round(oldPixel / step);
      const newPixel = quantIndex * step;
      pixels[idx] = newPixel;
      
      const quantError = oldPixel - newPixel;
      
      // Distribute error
      if (x + 1 < gridWidth) pixels[y * gridWidth + (x + 1)] += (quantError * 7) / 16;
      if (x - 1 >= 0 && y + 1 < gridHeight) pixels[(y + 1) * gridWidth + (x - 1)] += (quantError * 3) / 16;
      if (y + 1 < gridHeight) pixels[(y + 1) * gridWidth + x] += (quantError * 5) / 16;
      if (x + 1 < gridWidth && y + 1 < gridHeight) pixels[(y + 1) * gridWidth + (x + 1)] += (quantError * 1) / 16;
    }
  }

  // 5. Map to Dice Values (1 to 6)
  const diceValues = new Array(gridWidth * gridHeight);
  for (let i = 0; i < pixels.length; i++) {
    let val = Math.round(pixels[i] / step);
    val = Math.max(0, Math.min(5, val));
    
    if (invert) {
      diceValues[i] = val + 1; // Bright -> 6 dots
    } else {
      diceValues[i] = 6 - val; // Bright -> 1 dot
    }
  }

  const result: ProcessImageResult = {
    diceValues,
    gridWidth,
    gridHeight
  };

  self.postMessage(result);
};

export {}
