import { AuthForm } from "@/components/auth-form"

type PageProps = { readonly searchParams: Promise<{ readonly next?: string }> }

export default async function LoginPage({ searchParams }: PageProps) {
  const requested = (await searchParams).next
  const nextPath =
    requested?.startsWith("/") === true && !requested.startsWith("//") ? requested : "/dashboard"
  return (
    <div className="form-shell">
      <AuthForm mode="login" nextPath={nextPath} />
    </div>
  )
}
