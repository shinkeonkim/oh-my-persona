import { useState, useEffect, useRef } from 'react';
import { Upload, Image as ImageIcon, Loader2, Download, Box } from 'lucide-react';
import { processImageFile } from './utils/processImage';
import type { ProcessImageResult } from './workers/imageProcessor';
import DiceArt3D from './components/DiceArt3D';
import type { DiceArt3DRef } from './components/DiceArt3D';
import DiceArt2D from './components/DiceArt2D';

function App() {
  const [sourceImage, setSourceImage] = useState<HTMLImageElement | null>(null);
  const [diceData, setDiceData] = useState<ProcessImageResult | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  
  const dice3DRef = useRef<DiceArt3DRef>(null);

  // Settings
  const [resolution, setResolution] = useState(80);
  const [invertBackground, setInvertBackground] = useState(false);
  const [is3DMode, setIs3DMode] = useState(true);

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const img = new Image();
    const objectUrl = URL.createObjectURL(file);
    
    img.onload = () => {
      setSourceImage(img);
      processCurrent(img, resolution, invertBackground);
      URL.revokeObjectURL(objectUrl);
    };
    img.src = objectUrl;
  };

  const processCurrent = async (img: HTMLImageElement, res: number, invert: boolean) => {
    setIsProcessing(true);
    try {
      const result = await processImageFile(img, res, invert);
      setDiceData(result);
    } catch (error) {
      console.error("Failed to process image:", error);
    } finally {
      setIsProcessing(false);
    }
  };

  // Re-process when settings change
  useEffect(() => {
    if (sourceImage) {
      const timer = setTimeout(() => {
        processCurrent(sourceImage, resolution, invertBackground);
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [resolution, invertBackground, sourceImage]);

  const handleDownload = () => {
    const canvas = document.querySelector('canvas');
    if (canvas) {
      const url = canvas.toDataURL('image/png');
      const a = document.createElement('a');
      a.href = url;
      a.download = `dice-art-${resolution}x.png`;
      a.click();
    }
  };

  const handleDownloadGLB = () => {
    dice3DRef.current?.exportGLTF();
  };

  return (
    <div className="flex h-screen w-full bg-white text-gray-900 overflow-hidden font-sans">
      {/* Sidebar Controls */}
      <aside className="w-80 border-r-2 border-gray-200 bg-white flex flex-col z-10 overflow-y-auto">
        <div className="p-6 border-b-2 border-gray-200 flex items-center justify-between shrink-0">
          <h1 className="text-2xl font-extrabold tracking-tight text-gray-900 flex items-center gap-3">
            <div className="flex items-center justify-center w-10 h-10 bg-blue-500 text-white rounded-md text-2xl shadow-sm">
              🎲
            </div>
            Dice Art
          </h1>
        </div>

        <div className="p-6 border-b-2 border-gray-200 shrink-0">
          <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-gray-300 hover:border-blue-500 hover:bg-blue-50 bg-gray-100 rounded-lg cursor-pointer transition-all duration-200 hover:scale-[1.02] group">
            <div className="flex flex-col items-center justify-center pt-5 pb-6">
              {isProcessing ? (
                <Loader2 className="w-8 h-8 mb-2 text-blue-500 animate-spin" />
              ) : (
                <Upload className="w-8 h-8 mb-2 text-gray-400 group-hover:text-blue-500 transition-colors" />
              )}
              <p className="text-sm font-bold text-gray-900">Click to upload image</p>
              <p className="text-xs font-medium text-gray-500 mt-1">PNG, JPG, WEBP</p>
            </div>
            <input type="file" className="hidden" accept="image/*" onChange={handleImageUpload} />
          </label>
        </div>

        <div className="p-6 flex flex-col gap-6 overflow-y-auto">
          <div className="space-y-6">
            <div className="space-y-3 pb-6 border-b-2 border-gray-200">
              <div className="flex justify-between items-center">
                <label className="text-sm font-bold text-gray-900">Resolution</label>
                <span className="text-xs font-bold text-blue-600 bg-blue-50 border-2 border-blue-100 px-2 py-1 rounded-md">{resolution}</span>
              </div>
              <input 
                type="range" 
                min="20" max="200" step="10" 
                value={resolution} 
                onChange={(e) => setResolution(Number(e.target.value))} 
                className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-500 outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2" 
              />
              <div className="flex justify-between text-xs font-medium text-gray-500 px-1">
                <span>Low</span>
                <span>High</span>
              </div>
            </div>

            <div className="space-y-3 pb-6 border-b-2 border-gray-200">
              <label className="flex items-center justify-between cursor-pointer group">
                <span className="text-sm font-bold text-gray-900">Invert Background</span>
                <div className="relative">
                  <input type="checkbox" className="sr-only peer" checked={invertBackground} onChange={() => setInvertBackground(!invertBackground)} />
                  <div className="w-12 h-7 bg-gray-200 ring-2 ring-transparent peer-focus:ring-blue-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-blue-500"></div>
                </div>
              </label>
            </div>

            <div className="space-y-3">
              <label className="flex items-center justify-between cursor-pointer group">
                <span className="text-sm font-bold text-gray-900">3D Output</span>
                <div className="relative">
                  <input type="checkbox" className="sr-only peer" checked={is3DMode} onChange={() => setIs3DMode(!is3DMode)} />
                  <div className="w-12 h-7 bg-gray-200 ring-2 ring-transparent peer-focus:ring-blue-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-blue-500"></div>
                </div>
              </label>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Canvas Area */}
      <main className="flex-1 relative bg-gray-100 flex flex-col overflow-hidden">
        {!diceData && (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-400 z-10 pointer-events-none">
            <div className="w-24 h-24 mb-6 rounded-full bg-white border-2 border-gray-200 flex items-center justify-center">
              <ImageIcon className="w-10 h-10 text-gray-400" />
            </div>
            <p className="text-2xl font-extrabold text-gray-900 tracking-tight">Generate Dice Art</p>
            <p className="text-gray-500 font-medium mt-2">Upload an image from the sidebar to begin.</p>
          </div>
        )}
        
        {diceData && (
          <>
            {is3DMode ? (
              <DiceArt3D data={diceData} invert={invertBackground} ref={dice3DRef} />
            ) : (
              <DiceArt2D data={diceData} invert={invertBackground} />
            )}
            
            <div className="absolute top-6 right-6 flex flex-col items-end gap-4 z-20 pointer-events-none">
              <div className="bg-white border-2 border-gray-200 p-6 rounded-lg pointer-events-auto">
                <div className="font-extrabold text-sm uppercase tracking-wider text-gray-500 mb-3">Grid Stats</div>
                <div className="grid grid-cols-2 gap-x-8 gap-y-2 text-base font-medium">
                  <span className="text-gray-600">Total Dice:</span>
                  <span className="text-gray-900 text-right">{(diceData.gridWidth * diceData.gridHeight).toLocaleString()}</span>
                  <span className="text-gray-600">Dimensions:</span>
                  <span className="text-gray-900 text-right">{diceData.gridWidth}x{diceData.gridHeight}</span>
                </div>
              </div>
              <button 
                onClick={handleDownload} 
                className="pointer-events-auto flex items-center justify-center gap-2 bg-blue-500 text-white px-6 py-4 rounded-md font-bold transition-all duration-200 hover:scale-105 hover:bg-blue-600 w-full"
              >
                <Download className="w-5 h-5" /> DOWNLOAD IMAGE
              </button>
              
              {is3DMode && (
                <button 
                  onClick={handleDownloadGLB} 
                  className="pointer-events-auto flex items-center justify-center gap-2 bg-emerald-500 text-white px-6 py-4 rounded-md font-bold transition-all duration-200 hover:scale-105 hover:bg-emerald-600 w-full mt-2"
                >
                  <Box className="w-5 h-5" /> DOWNLOAD 3D MODEL
                </button>
              )}
            </div>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
