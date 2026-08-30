"use client";

import { useEffect, useState } from "react";

export default function OrientationBlocker() {
  const [shouldBlock, setShouldBlock] = useState(false);

  useEffect(() => {
    const checkScreen = () => {
      const width = window.innerWidth;

      // 1024px 미만이면 화면을 막기
      setShouldBlock(width < 1024);
    };

    checkScreen();
    window.addEventListener("resize", checkScreen);

    return () => window.removeEventListener("resize", checkScreen);
  }, []);

  if (!shouldBlock) return null;

  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-white text-center p-5">
      <p className="text-xl font-semibold">더 나은 이용을 위해</p>
      <p className="text-xl font-semibold text-blue-500">화면을 가로로 돌려주세요</p>
    </div>
  );
}
