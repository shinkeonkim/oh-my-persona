import { useRef, useState, useCallback } from "react";
import { WebSpeechSTTProvider } from "@/shared/lib/stt/WebSpeechSTTProvider";
import type { STTSegment } from "@/shared/lib/stt/types";

/**
 * Manages camera/mic stream, audio level metering, and STT provider.
 * Returns state values and refs separately to satisfy react-hooks/refs lint rule.
 */
export function useMediaSetup() {
  // ── Refs (not used in render / dependency arrays) ──
  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const audioRafRef = useRef<number | null>(null);
  const sttRef = useRef<WebSpeechSTTProvider | null>(null);

  /**
   * STT 결과를 실제로 기록할지 여부를 동기적으로 판단하는 ref.
   * startStt() 호출 시 true, stopStt() 호출 시 즉시 false 로 전환된다.
   * onResult 콜백 내부에서 이 값을 확인하여 speaking phase 외부의 결과를 무시한다.
   */
  const isListeningRef = useRef(false);

  // ── State (safe for render / dependency arrays) ──
  const [isListening, setIsListening] = useState(false);
  const [finalText, setFinalText] = useState("");
  const [interimText, setInterimText] = useState("");
  const [audioLevel, setAudioLevel] = useState(0);
  const [mediaReady, setMediaReady] = useState(false);
  const [sttSegments, setSttSegments] = useState<STTSegment[]>([]);
  const lastFinalTimestampRef = useRef(0);

  const setupMedia = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      mediaStreamRef.current = stream;
      if (videoRef.current) videoRef.current.srcObject = stream;
      try {
        audioCtxRef.current = new AudioContext();
        const source = audioCtxRef.current.createMediaStreamSource(stream);
        const analyser = audioCtxRef.current.createAnalyser();
        analyser.fftSize = 256;
        source.connect(analyser);
        analyserRef.current = analyser;
        const dataArray = new Uint8Array(analyser.frequencyBinCount);
        let lastLevel = -1;
        const drawMeter = () => {
          if (!analyserRef.current) return;
          analyserRef.current.getByteFrequencyData(dataArray);
          const avg = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
          const next = Math.round(Math.min(100, (avg / 128) * 100));
          // 값이 실제로 변경된 경우에만 setState 를 호출하여 불필요한 리렌더를 방지한다.
          if (next !== lastLevel) {
            lastLevel = next;
            setAudioLevel(next);
          }
          audioRafRef.current = requestAnimationFrame(drawMeter);
        };
        drawMeter();
      } catch { /* AudioContext unavailable */ }
    } catch { console.warn("미디어 장치 접근 실패"); }

    sttRef.current = new WebSpeechSTTProvider();

    // guard: speaking phase 에서만 자동 재시작을 허용한다.
    sttRef.current.setShouldRestartGuard(() => isListeningRef.current);

    sttRef.current.onResult((result) => {
      // isListeningRef 가 false 이면 speaking phase 가 아니므로 결과를 무시한다.
      // TTS 재생 중 브라우저가 STT 결과를 뒤늦게 전달하는 경우를 방어한다.
      if (!isListeningRef.current) return;

      if (result.isFinal) {
        const startMs = lastFinalTimestampRef.current;
        const endMs = result.timestampMs;
        lastFinalTimestampRef.current = endMs;
        setSttSegments((prev) => [...prev, { text: result.text, startMs, endMs }]);
        setFinalText((prev) => prev + (prev ? " " : "") + result.text);
        setInterimText("");
      } else {
        setInterimText(result.text);
      }
    });
    sttRef.current.onError((e) => console.warn("STT 오류:", e));
    setMediaReady(true);
  }, []);

  const cleanupMedia = useCallback(() => {
    isListeningRef.current = false;
    sttRef.current?.stop();
    mediaStreamRef.current?.getTracks().forEach((t) => t.stop());
    mediaStreamRef.current = null;
    if (audioRafRef.current) cancelAnimationFrame(audioRafRef.current);
    audioRafRef.current = null;
    audioCtxRef.current?.close().catch(() => {});
    audioCtxRef.current = null;
    analyserRef.current = null;
  }, []);

  const startStt = useCallback((lang = "ko-KR") => {
    // ref 를 먼저 true 로 설정하여 onResult guard 가 즉시 활성화되도록 한다.
    isListeningRef.current = true;
    sttRef.current?.start(lang);
    setIsListening(true);
  }, []);

  const stopStt = useCallback(() => {
    // ref 를 먼저 false 로 설정하여 이후 도착하는 onResult 결과를 즉시 차단한다.
    // WebSpeechSTTProvider.stop() 내부의 onend null 처리와 함께 이중 방어를 구성한다.
    isListeningRef.current = false;
    sttRef.current?.stop();
    setIsListening(false);
  }, []);

  const resetText = useCallback(() => {
    setFinalText("");
    setInterimText("");
    setSttSegments([]);
    lastFinalTimestampRef.current = 0;
  }, []);

  return {
    // Refs — only pass to ref= props or use inside callbacks/effects
    videoRef,
    sttRef,
    // State — safe for render and dependency arrays
    isListening,
    finalText,
    interimText,
    audioLevel,
    mediaReady,
    sttSegments,
    // Setters
    setIsListening,
    setFinalText,
    setInterimText,
    // Actions
    setupMedia,
    cleanupMedia,
    startStt,
    stopStt,
    resetText,
  };
}
