import type { NextConfig } from "next"

const nextConfig = {
  output: "standalone",
  outputFileTracingRoot: new URL("../../", import.meta.url).pathname,
  poweredByHeader: false,
  experimental: {
    optimizePackageImports: ["@phosphor-icons/react"],
  },
  async rewrites() {
    const apiInternalUrl = process.env["API_INTERNAL_URL"] ?? "http://localhost:3001/api/"
    const normalizedApiUrl = apiInternalUrl.endsWith("/") ? apiInternalUrl : `${apiInternalUrl}/`
    const apiOrigin = new URL(normalizedApiUrl).origin
    return [
      {
        source: "/api/:path*",
        destination: `${normalizedApiUrl}:path*`,
      },
      {
        source: "/healthz",
        destination: `${apiOrigin}/healthz`,
      },
      {
        source: "/readyz",
        destination: `${apiOrigin}/readyz`,
      },
    ]
  },
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
        ],
      },
    ]
  },
} satisfies NextConfig

export default nextConfig
