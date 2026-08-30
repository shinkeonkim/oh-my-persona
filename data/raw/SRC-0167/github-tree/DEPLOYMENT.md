# Cloudflare Workers Builds Deployment

The production site is a static Astro build for `https://terraform-study.shinkeonkim.com`. Its deployment model follows `/Users/koa/004-Projects/0001-Resume/my-cv`: Cloudflare Workers Builds runs Bun, then Wrangler deploys static assets and binds the custom domain from `wrangler.json`.

## Local verification

Bun 1.3.14 is the package manager. `bun.lock` is the only dependency lockfile.

```bash
bun install --frozen-lockfile
bun run build
```

The build must report:

- zero Astro diagnostics
- exactly 200 canonical practice questions
- passing CSP regression checks for Pagefind WASM, its worker, and Cloudflare Web Analytics
- a Pagefind search index
- `dist/404.html` and `dist/sitemap-index.xml`
- `dist/_headers` and `dist/robots.txt`

Use `bun run preview` for a local production preview.

`public/_headers` applies the document CSP globally, then detaches it from `/pagefind/*`. The Pagefind worker otherwise receives its own response CSP, and stale edge metadata on its fixed URL can override the corrected document policy and block WASM. Pagefind assets therefore use `max-age=0, must-revalidate`; the document CSP still controls worker creation with `worker-src 'self' blob:`.

## Wrangler configuration

`wrangler.json` configures a static generated site:

- `assets.directory`: deploys `dist`
- `assets.not_found_handling`: serves the nearest `404.html` with status 404
- `assets.html_handling`: preserves Astro's directory routes and trailing slashes
- `routes[].custom_domain`: binds `terraform-study.shinkeonkim.com`
- `observability.enabled`: enables Workers observability

Unlike the reference CV's Vue SPA, this site uses `404-page`, not `single-page-application`. Unknown documentation URLs must not return the homepage with status 200.

## Dashboard setup

1. Open Cloudflare Dashboard and select **Workers & Pages**.
2. Create a Worker by importing the Git repository.
3. Open **Settings > Build & deployments**.
4. Configure the following values.

| Setting | Value |
|---|---|
| Production branch | `main` |
| Build command | `bun run build` |
| Deploy command | `bun run deploy` |
| Root directory | `/` |

Workers Builds checks the repository's `wrangler.json` during deployment. The dashboard's Git integration supplies deployment authentication, so a repository secret containing `CLOUDFLARE_API_TOKEN` is not required for this setup.

## Custom domain

Wrangler binds `terraform-study.shinkeonkim.com` because the route has `custom_domain: true`. The `shinkeonkim.com` zone must be managed by the same Cloudflare account.

If automatic binding does not complete, open **Settings > Domains & Routes**, select **Add custom domain**, and enter `terraform-study.shinkeonkim.com`.

## Manual authenticated deployment

An operator already authenticated with Wrangler can use the same project configuration locally:

```bash
bun run build
bun run deploy
```

Do not commit Cloudflare API tokens, account IDs, or local `.wrangler/` state.

## Production verification

After the custom domain becomes active, verify:

```bash
curl -I https://terraform-study.shinkeonkim.com/
curl -I https://terraform-study.shinkeonkim.com/practice/bank-200/
curl -I https://terraform-study.shinkeonkim.com/not-a-real-page
curl -I https://terraform-study.shinkeonkim.com/sitemap-index.xml
curl -I https://terraform-study.shinkeonkim.com/robots.txt
```

Expected results:

- Existing pages return `200` over HTTPS.
- An unknown path returns `404` and the generated 404 page.
- Canonical and sitemap URLs use `terraform-study.shinkeonkim.com`.
- Security headers from `public/_headers` are present.
- Fingerprinted `/_astro/` assets have an immutable cache policy.
- Search returns results for `use_lockfile`, `ephemeral`, and `workspace`.
- Browser console has no Pagefind WASM or Cloudflare Insights CSP errors.
- Mobile navigation updates `aria-expanded`, and practice answer disclosures open.
