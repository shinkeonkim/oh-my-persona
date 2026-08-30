# slack-data-collector

Collect every piece of metadata from one or more Slack channels - messages, thread replies, reactions, attached files, and users - into a single, queryable **SQLite** archive.

- Multiple channels, public and private
- Incremental sync: only new messages on each run, no duplicates
- Thread replies kept fresh via configurable lookback window
- All metadata preserved (every API response stored as `raw_json` next to indexed columns)
- Attached files downloaded with the right `Authorization` header
- One file, queryable in `sqlite3` / DBeaver / pandas
- Safe to push to GitHub: secrets in `.env` (gitignored), collected data in `data/` (gitignored)

---

## Quick start

```bash
git clone https://github.com/<your>/slack-data-collector
cd slack-data-collector
python -m venv .venv
source .venv/bin/activate
pip install -e .

cp .env.example .env                  # then paste your xoxb- token
cp config.example.yaml config.yaml    # then edit `channels:` list

slack-collector init                  # prints scope checklist + creates data/slack.db
slack-collector channels list         # shows channels the bot can see
slack-collector sync                  # first run = full backfill
slack-collector sync                  # later runs = incremental
slack-collector status                # see per-channel state
```

## Slack app setup

The fastest path is the included **app manifest**:

1. Go to <https://api.slack.com/apps> → **Create New App** → **From a manifest**.
2. Pick your workspace, paste the contents of [`manifest.example.yaml`](manifest.example.yaml), click **Next** → **Create**.
3. **Install to Workspace** and copy the **Bot User OAuth Token** (starts with `xoxb-`) into `.env`.
4. Invite the bot to each channel you want to collect: `/invite @slack-collector` (or whatever you named it).

### Required Bot Token scopes

| Scope | Purpose |
|---|---|
| `channels:history` | Read messages in public channels |
| `groups:history` | Read messages in private channels (only ones the bot is invited to) |
| `channels:read` | List public channels |
| `groups:read` | List private channels the bot is in |
| `users:read` | Resolve user IDs to display names |
| `users.profile:read` | Real names, display names, email |
| `files:read` | Download attached files |
| `reactions:read` | Emoji reactions |
| `team:read` | Workspace name/id |

If you also want DMs collected, add `im:history`, `im:read`, `mpim:history`, `mpim:read`. They are intentionally excluded from the default manifest.

## Rate limit warning - read this before a large run

`conversations.history` has two rate-limit regimes since 2025-05-29:

| App type | Tier | Effective speed |
|---|---|---|
| Internal customer-built app, or Marketplace app | Tier 3 | ~50+ req/min, `limit` up to 999 (200 recommended) |
| New non-Marketplace distributed app | Hard cap | **1 req/min, `limit=15`** |

For an internal app (the default and recommended case), a 10k-message channel syncs in minutes. For a distributed non-Marketplace app, it can take 11+ hours. The tool works in either case; it just respects the limit. Set `rate_limit_sleep_sec` in `config.yaml` accordingly.

The SDK also retries on HTTP 429 automatically (`RateLimitErrorRetryHandler`, configurable via `max_retry_count`).

## Configuration

`config.yaml`:

```yaml
data_dir: ./data
download_files: true
lookback_days: 30
rate_limit_sleep_sec: 1.0
max_retry_count: 10
channels:
  - general
  - C0123456789
refresh_workspace: true
refresh_users: true
fetch_all_workspace_users: false
```

`refresh_users` looks up only the users that actually wrote, reacted to, or edited a message in the channels you collect (one `users.info` call per new user). `fetch_all_workspace_users` is off by default - turn it on only if you also want every workspace member who has never posted in the collected channels.

`.env`:

```
SLACK_BOT_TOKEN=xoxb-...
```

Both files in your real project are **gitignored**. The committed templates are `.env.example` and `config.example.yaml`.

## How incremental sync works

1. On the first run for a channel, `sync_state.last_ts` is NULL → full backfill via `conversations.history(oldest=0)`, paginated.
2. On every subsequent run we use `oldest = last_ts` and `inclusive=False` → Slack excludes the boundary message, we never double-store it.
3. After Phase 1 (parent messages), we re-fetch replies for any thread whose `latest_reply` is within `lookback_days`. This catches replies posted to old threads. New replies on threads outside the lookback are missed - widen the window or `--full` if you need them.
4. Phase 3 downloads attached files we have not pulled yet, with `Authorization: Bearer <token>`.
5. Phase 4 resolves users referenced in collected messages/reactions/edits that are not yet in the `users` table. **Only channel-active users are fetched** - the workspace's full user list is not pulled by default. Use `slack-collector users-sync --all` (or set `fetch_all_workspace_users: true`) if you also want every workspace member.

Edits are detected: if a stored message comes back with a newer `edited.ts`, we update `text`, `raw_json`, `edited_ts`, `edited_user` and bump the `messages_updated` counter. We never overwrite the original `ts`.

Hard-deleted messages disappear from `conversations.history` and stay in our archive as the last snapshot we saw.

## Schema cheat sheet

```sql
channels        (id PK, name, is_private, is_archived, topic, purpose, raw_json, ...)
users           (id PK, name, real_name, display_name, email, is_bot, deleted, raw_json, ...)
messages        (channel_id, ts) PK, thread_ts, user_id, text, reply_count, latest_reply,
                is_thread_parent, is_reply, edited_ts, raw_json, ...
reactions       (channel_id, message_ts, name, user_id) PK
files           (id PK, channel_id, message_ts, name, mimetype, size, url_private,
                local_path, downloaded, download_error, raw_json, ...)
sync_state      (channel_id PK, last_ts, last_full_sync_at, last_incremental_at)
collection_runs (id PK, channel_id, mode, started_at, finished_at, status,
                messages_added, messages_updated, threads_processed, ...)
workspace       (team_id PK, name, domain, raw_json)
```

Every entity has `raw_json` with the full API response - if you later realize you need a field we didn't index, it's already there.

### Sample queries

Top 10 emoji used in a channel:

```sql
SELECT name, COUNT(*) AS uses
FROM reactions
WHERE channel_id = 'C0123456789'
GROUP BY name
ORDER BY uses DESC
LIMIT 10;
```

Most active users in the last 30 days:

```sql
SELECT u.display_name, u.name, COUNT(*) AS messages
FROM messages m
JOIN users u ON u.id = m.user_id
WHERE CAST(m.ts AS REAL) >= strftime('%s','now') - 30*86400
GROUP BY u.id
ORDER BY messages DESC
LIMIT 20;
```

Threads with the most replies:

```sql
SELECT m.channel_id, m.ts, m.text, m.reply_count
FROM messages m
WHERE m.is_thread_parent = 1
ORDER BY m.reply_count DESC
LIMIT 20;
```

All attachments larger than 10 MB:

```sql
SELECT id, name, size, channel_id, message_ts, local_path
FROM files
WHERE size > 10*1024*1024
ORDER BY size DESC;
```

Run any read-only query straight from the CLI:

```bash
slack-collector query "SELECT name, COUNT(*) FROM reactions GROUP BY name ORDER BY 2 DESC LIMIT 5"
```

## Commands

```
slack-collector init                         scaffold data dir, print scope checklist
slack-collector channels list                channels the bot can see
slack-collector channels tracked             tracked channels + last sync time
slack-collector sync                         sync all channels in config.yaml
slack-collector sync --channel general       sync one channel
slack-collector sync --full --channel C123   force full re-fetch
slack-collector users-sync                   resolve channel-active users (default)
slack-collector users-sync --all             fetch the entire workspace user directory
slack-collector files retry                  reset previous download errors and retry
slack-collector status                       per-channel state + recent runs
slack-collector query "<read-only SQL>"      run a SELECT and print as table or JSON
```

`-c PATH` overrides the config file location for any command.

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `not_in_channel` | Bot is not a member of the channel | `/invite @<botname>` in the channel |
| `missing_scope` | Token lacks a required permission | Add the scope in OAuth & Permissions, **reinstall** the app, replace token |
| `ratelimited` (HTTP 429) | Slack rate limit | The SDK retries automatically; if it gives up, raise `max_retry_count` or `rate_limit_sleep_sec` |
| `SLACK_BOT_TOKEN is not set` | Missing `.env` | Copy `.env.example` to `.env`, paste your `xoxb-` token |
| File download fails with HTML body | `files:read` missing or token revoked | Add scope, reinstall, replace token |
| `database is locked` | Another process holds a write lock | We use WAL mode; check no other `sync` is running |

## GitHub safety checklist

Before your first `git push`:

```bash
git status                            # should NOT list .env or data/
git ls-files | grep -E '\.env$'       # must be empty
git ls-files | grep -E '^data/'       # must be empty
```

The shipped `.gitignore` covers `.env`, `data/`, the venv, and tool caches. If you copy the layout into another repo, copy the `.gitignore` too.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest                                # unit tests with mocked WebClient
ruff check src tests                  # lint
```

The implementation is intentionally small (~10 files in `src/slack_collector/`). The `raw_json` column on every entity makes the schema future-proof: you can add new indexed columns later and backfill them from `raw_json` without re-fetching anything.

## License

MIT. Use at your own discretion; Slack content is sensitive - treat the resulting database as confidential.
