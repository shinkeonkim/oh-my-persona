import { useEffect, useRef } from "react";

declare global {
  interface Window {
    turnstile?: { render: (element: HTMLElement, options: Record<string, unknown>) => string };
  }
}

interface Props { siteKey: string; onVerify: (token: string) => void; }

export function TurnstileChallenge({ siteKey, onVerify }: Props) {
  const container = useRef<HTMLDivElement>(null);
  useEffect(() => {
    let cancelled = false;
    function render() {
      if (!cancelled && container.current && window.turnstile) {
        container.current.replaceChildren();
        window.turnstile.render(container.current, {
          sitekey: siteKey, callback: onVerify, "expired-callback": () => onVerify(""),
          theme: "light", language: "ko",
        });
      }
    }
    const existing = document.querySelector<HTMLScriptElement>('script[data-persona-turnstile]');
    if (existing) {
      if (window.turnstile) render();
      else existing.addEventListener("load", render, { once: true });
    } else {
      const script = document.createElement("script");
      script.src = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";
      script.async = true; script.defer = true; script.dataset.personaTurnstile = "true";
      script.addEventListener("load", render, { once: true }); document.head.append(script);
    }
    return () => { cancelled = true; };
  }, [siteKey, onVerify]);
  return <div className="turnstile-wrap" ref={container} aria-label="자동화 요청 방지 확인" />;
}
