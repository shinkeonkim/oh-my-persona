import type { Metadata } from "next"
import type { JSX, ReactNode } from "react"

import { DevTools } from "@/components/dev-tools"
import { SiteHeader } from "@/components/site-header"
import { getCurrentUser } from "@/lib/server-api"

import "./globals.css"

export const metadata: Metadata = {
  metadataBase: new URL("https://aws-study.shinkeonkim.com"),
  title: { default: "AWS Study", template: "%s | AWS Study" },
  description: "AIF, CLF, SAA 자격증과 AWS 서비스를 구조적으로 학습하는 개인 학습 공간",
  openGraph: { title: "AWS Study", description: "AWS 자격증 통합 학습 공간", type: "website" },
  robots: { index: true, follow: true },
}

const themeScript = `try{const saved=localStorage.getItem("aws-study-theme");const preferred=matchMedia("(prefers-color-scheme:light)").matches?"light":"dark";document.documentElement.dataset.theme=saved??preferred}catch{}`

export default async function RootLayout({
  children,
}: {
  readonly children: ReactNode
}): Promise<JSX.Element> {
  const user = await getCurrentUser()
  return (
    <html lang="ko" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: `(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);}})(window,document,'script','dataLayer','GTM-54NK6F38');` }} />
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body>
        <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-54NK6F38" height="0" width="0" style={{ display: "none", visibility: "hidden" }} title="Google Tag Manager" /></noscript>
        <a className="skip-link" href="#main-content">
          본문으로 건너뛰기
        </a>
        <SiteHeader user={user} />
        <main id="main-content" className="site-main">
          {children}
        </main>
        <footer className="site-footer">
          <div className="shell footer-inner">
            <span>AWS Study</span>
            <span>개인 학습용 · AWS와 제휴되지 않음</span>
          </div>
        </footer>
        <DevTools />
      </body>
    </html>
  )
}
