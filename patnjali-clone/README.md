# patnjali.online static clone

Offline mirror of https://patnjali.online in `secret/patnjali-clone/`.

## Pages

| File | Original URL | Purpose |
|------|--------------|---------|
| `index.html` | `/` | Age verification gate |
| `home1.html` | `/home1` | Main ESI WELLNESS landing page |

## View locally

```bash
cd secret/patnjali-clone
python3 finalize.py   # fix lazy images + local links
python3 -m http.server 8080
```

Open http://localhost:8080/ — click **Yes, I'm 21+** to reach `home1.html`.

## Scripts

- `mirror.py` — download pages and assets from the live site (requires network access to patnjali.online)
- `fix_paths.py` — rewrite remote URLs to local paths
- `finalize.py` — swap lazy-load placeholders for real `src` values for offline viewing

## Notes

- Assets live under `wp-content/`.
- The live site may block direct curl/python downloads; the main landing page was captured during an earlier mirror run.
- Age gate `index.html` was rebuilt from page structure + local CSS (`post-15.css`).
