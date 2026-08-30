"use client"

import { useEffect } from "react"

export function DevTools(): null {
  useEffect(() => {
    if (process.env.NODE_ENV !== "development") return
    void Promise.all([import("react-scan"), import("react-grab")]).then(
      ([reactScan, reactGrab]) => {
        reactScan.scan({ enabled: true })
        reactGrab.init()
      },
    )
  }, [])
  return null
}
