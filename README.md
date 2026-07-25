# SEAUX9.ART

Official artist site for **SEAUX9** — Artist. Producer. Sonic Shaman.
Static site, zero build dependencies at runtime, hosted the same way as prmlrecords.com (Render static site + custom domain `seaux9.art`).

> Interim home while `seaux9.com` is squatted — re-purchase window opens **~Feb 2027**.

## Brand lock

| Token | Value |
|---|---|
| Ink (bg) | `#011627` |
| Paper | `#FDFFFC` |
| Red | `#F71735` |
| Aqua | `#41EAD4` |
| Sun | `#FF9F1C` |
| Display font | WDXL Lubrifont TC (`assets/fonts/WDXL-Latin.woff2`, Latin subset, OFL) |
| Hand/body font | Kalam Light/Regular/Bold (woff2, OFL) |
| Logo | `assets/seaux9-logo.svg` — traced from `Seaux S Logo Final.png`, fills with `currentColor` so CSS can paint it any brand color |

## Folder map

```
index.html              the site (logo SVG embedded as <symbol> by build.py)
assets/css/style.css    all styling
assets/js/main.js       renders releases/events/posts/socials from content data
content/site.json       ★ THE source of truth — edit this
content/site.data.js    auto-generated from site.json (makes file:// viewing work)
scripts/build.py        rebuild step (logo injection + data embed)
scripts/post.py         posting CLI (see below)
```

## Money (all LIVE Stripe, created 2026-07-25)

- **Store**: 11 payment links (CDs $17.99–$22.22, vinyl $100, digital $9–$22.22, shirt $36 w/ size dropdown, posters $15) — physical items collect US shipping + phone
- **Donations**: custom-amount link `https://donate.stripe.com/3cIdRa3eBaRMdXEdf41ZS1k`
- **9SQUAD Inner Circle**: $9.99/mo subscription `https://buy.stripe.com/dRm6oIeXj3pkbPwdf41ZS1l`
- **Mailing list**: Tally `https://tally.so/r/D4EQbl` (segment fans with `?source=` params)

## Publishing content (the automation)

Everything on the site (music, store, events, tiers, press, gallery, journal, socials) renders from `content/site.json`.

```bash
# add a journal post
python scripts/post.py post "Title" "Body text" --tags news,9squad

# add an event
python scripts/post.py event "Show Name" 2026-10-01 --time "8 PM" --venue "Venue" --city "Atlanta, GA" --info "One-liner" --cta RSVP

# hand-edit site.json instead? then just:
python scripts/build.py
```

Flags: `--push` (git add/commit/push → host redeploys) · `--crosspost` (send the same post to every social platform via Postiz, see below).

**PRML booking → site**: confirmed SEAUX9 bookings drop a JSON into `16_CLAUDE_OPS/seaux9-bookings/`, then `python scripts/booking-sync.py --scan` publishes the event (LIVESTREAM badge + stream-ticket link supported). Wired into /prml-booking Step 7.

**Skills**: `/seaux9-site` (site ops) · `/seaux9-reels` (video recycler → 5 posts/day via Postiz).

## Cross-platform posting (TikTok / FB / YouTube / IG / X / …)

**[Postiz](https://github.com/gitroomhq/postiz-app)** — open-source (AGPL-3.0), self-hostable, ~30k GitHub stars, supports 33 platforms incl. TikTok, Facebook, Instagram, YouTube, X, Threads, Bluesky, Reddit, Pinterest, Discord. Has a public API; `scripts/post.py --crosspost` already talks to it (`POSTIZ_URL` + `POSTIZ_API_KEY` env vars).

**Fanbase** (fanbase.app/seaux9): no public developer API as of Jul 2026 — post manually for now. Fanbase is Atlanta-built (Isaac Hayes III); a PRML→Fanbase partnership/API-access ask is the real play. Postiz's provider architecture means Fanbase can be added as a custom provider the day an API exists.

## Deploy (same as prmlrecords.com)

1. `git init` this folder, push to GitHub.
2. Render → New Static Site → point at repo, publish directory `/`.
3. Add custom domain `seaux9.art` (Namecheap DNS → Render).
4. Later: PRML streaming API on prmlrecords.com feeds the "PRML STREAM" player.

## Licenses

Fonts are SIL OFL 1.1 — full texts in `assets/fonts/OFL-WDXL.txt` and `assets/fonts/OFL-Kalam.txt`.
