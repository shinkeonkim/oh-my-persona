import { MagnifyingGlass } from "@phosphor-icons/react/dist/ssr"
import Link from "next/link"

export default function NotFoundPage() {
  return (
    <div className="form-shell text-center">
      <div className="form-card">
        <MagnifyingGlass
          className="mx-auto text-[var(--accent)]"
          size={42}
          weight="duotone"
          aria-hidden="true"
        />
        <span className="eyebrow mt-5 block">404</span>
        <h1 className="mt-2 text-3xl font-bold">학습 자료를 찾지 못했습니다</h1>
        <p className="muted mt-3">주소를 확인하거나 자격증 홈에서 다시 탐색하세요.</p>
        <Link className="button button-primary mt-6" href="/">
          홈으로 돌아가기
        </Link>
      </div>
    </div>
  )
}
