'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';

const publicPaths = ['/', '/signin', '/signup', '/report'];

interface AuthGuardProps {
  children: React.ReactNode;
}

const AuthGuard = ({ children }: AuthGuardProps) => {
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    // 공개 경로 확인
    const isPublicPath =
      pathname &&
      publicPaths.some((path) => {
        // 루트 경로('/')는 정확히 일치하는 경우만 공개 경로로 처리
        if (path === '/') {
          return pathname === '/';
        }
        // 다른 경로는 startsWith로 체크
        return pathname.startsWith(path);
      });

    if (isPublicPath) {
      return;
    }

    // 인증 토큰 확인
    const accessToken = window.sessionStorage.getItem('accessToken');

    if (!accessToken) {
      // 토큰이 없으면 로그인 페이지로 리다이렉트
      router.replace('/signin');
    }
  }, [pathname, router]);

  return <>{children}</>;
};

export default AuthGuard;
