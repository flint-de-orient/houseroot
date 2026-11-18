# HouseRoot — website + admin panel

Static, framework-free site with a small dependency-free Node server that adds an admin panel for projects, blog posts and site details.

```
index.html        Home (featured projects render from data)
projects.html     Buy / Rent listing (filters, sort and cards render from data)
project.html      Project detail (?id=<slug>, fills from data)
blog.html         Blog list            post.html   Single post (?slug=<slug>)
about.html · developers.html · contact.html
admin/            Admin panel (served at /admin/ by server.js)
server.js         Content server + admin API (Node 18+, no npm install needed)
data/content.json All projects, posts and settings (the single source of truth)
data/admin.json   Admin password hash (created on first run)   data/secret.key  Session signing key
assets/css/style.css   all styles (tokens at the top)
assets/js/main.js      nav, drawer, reveal, counters, segs, forms, tabs, FAQ, transitions
assets/js/site-data.js renders projects, posts and settings from data/content.json
assets/uploads/        photos uploaded from the admin panel
_build/build.py        regenerates the 8 pages from shared header/footer partials (python3 _build/build.py)
```

## Run it

```
node server.js            # or: npm start
```

- Site: http://127.0.0.1:8080/
- Admin: http://127.0.0.1:8080/admin/ — first-run password is `houseroot1`. Change it under Site settings → Change password.
- Env vars: `PORT` (default 8080), `HOST` (default 127.0.0.1; set `0.0.0.0` on a VPS behind nginx), `ADMIN_PASSWORD` (overrides the stored password).

## Admin panel

- **Projects**: name, developer, locality, tag, status, listing type (buy/rent/plots/commercial), price (shown) + price in lakh (for filters/sort), configurations, carpet, possession, RERA no., card chips, about, units table, amenities, nearby distances, Google Maps embed, HouseRoot verdict, photos (upload or URL), featured and published flags.
- **Blog posts**: title, slug, date, author, excerpt, Markdown body with live preview, cover image, published flag.
- **Site settings**: WhatsApp number, phone, email, RERA number and office address. These fill the `[placeholders]` across every page.
- Drafts (published off) are hidden from the public site; the server only exposes published items to visitors.

## Security

- **Login lockout**: 5 wrong passwords in 15 minutes locks that IP for 15 minutes; each further lockout doubles the wait, up to 24 hours. Lockouts are stored in `data/lockouts.json`, so restarting the server does not clear them. Every failed attempt is also slowed by 0.8 s.
- **Sessions** last 12 hours (`ADMIN_SESSION_HOURS` to change) and all sessions are ended when the password changes.
- **Password rules**: 8 to 64 characters with at least one letter and one number. Stored as a salted scrypt hash in `data/admin.json`.
- **Audit log**: sign-ins, failures, lockouts, uploads and every content change are appended to `data/audit.log` with time and IP.
- **Uploads** are checked by file signature, not just extension; only real JPG, PNG, WebP, GIF or PDF content is accepted (max 6 MB).
- **Headers**: the admin panel is served with a Content Security Policy, cannot be embedded in frames, and sends no referrer.
- **Optional**: `ADMIN_ALLOW_IPS=1.2.3.4,5.6.7.8` restricts the admin API to those addresses; `SECURE_COOKIES=1` marks the session cookie HTTPS-only; set `TRUST_PROXY=1` when running behind nginx so the real client IP is used.

## Deploying

**Option A — VPS (admin + site together).** Copy the folder to the server, run `node server.js` under pm2 or a systemd unit, put nginx in front for HTTPS. Keep the `data/` folder backed up; it holds everything the admin writes.

**Option B — static host (Netlify, Vercel, GitHub Pages).** Run the admin locally, then upload the whole folder. The public pages only need `data/content.json` and `assets/uploads/`, both plain files. Note that on a static host the JSON file is served as-is, so unpublished drafts are visible to anyone who opens it directly; delete drafts before uploading if that matters.

## Editing the HTML

- Header/footer live once in `_build/build.py`; run it after changes. Or edit the HTML directly and delete `_build/`.
- Colours/radii/fonts: `:root` tokens at the top of `style.css`.
- Stylesheet and script links carry a `?v=` stamp. Bump it after editing CSS/JS so browsers fetch the new file.

## Lead forms

Forms carry `data-lead`. `main.js` validates the phone, shows a success state, and has a `TODO` where to POST:
```js
fetch('/api/lead', { method: 'POST', body: new FormData(f) })   // → FlintBox / n8n webhook
```

## Animations (all respect `prefers-reduced-motion`)
Word-by-word headline · scroll reveal (`data-reveal`, `data-stagger`) · count-up stats (`data-count`) · sliding segmented control · sticky header shrink · mobile drawer · card hover lift · save-heart pop · FAQ height animation · scroll-spy tabs on project page · page fade transitions.
