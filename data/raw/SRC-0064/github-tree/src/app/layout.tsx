import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import './globals.css';
import ConditionalHeader from '@/components/common/ConditionalHeader';
import AuthGuard from '@/components/common/AuthGuard';
import OrientationBlocker from '@/components/common/OrientationBlocker';

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
});

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
});

export const metadata: Metadata = {
  title: '깜빡이',
  description: '숨겨진 집중력의 불을 켜주는 아동교육 서비스',
  manifest: '/site.webmanifest',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>

        <OrientationBlocker />

        <ConditionalHeader />
        <AuthGuard>{children}</AuthGuard>
      </body>
    </html>
  );
}
