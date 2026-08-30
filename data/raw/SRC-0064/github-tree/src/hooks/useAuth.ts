import { useEffect } from 'react';
import { useRouter, usePathname, useSearchParams } from 'next/navigation';

const publicPaths = ['/signin', '/signup', '/on-boarding', '/report'];

export const useAuth = () => {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    if (typeof window === 'undefined') return;

    if (pathname && publicPaths.some((path) => pathname.startsWith(path))) {
      return;
    }

    const accessToken = window.sessionStorage.getItem('accessToken');

    if (!accessToken) {
      router.push('/signin');
    }
  }, [pathname, router, searchParams]);
};
