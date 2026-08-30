import ky from "ky"

export const clientApi = ky.create({
  prefix: process.env["NEXT_PUBLIC_API_URL"] ?? "http://localhost:3001/api",
  credentials: "include",
  timeout: 10_000,
  retry: { limit: 1, methods: ["get"] },
})
