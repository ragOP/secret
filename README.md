# secret

Offline mirrors of three landing pages.

| Folder | Site | Entry |
|--------|------|-------|
| `patnjali-clone/` | patnjali.online | `index.html` → age gate, then `home1.html` |
| `second/` | indianhealth.store/x1 | `index.html` |
| `third/` | ayurmorewell.online | `index.html` |

## Run locally

```bash
# Site 1
cd patnjali-clone && python3 finalize.py && python3 -m http.server 8080

# Site 2
cd second && python3 -m http.server 8081

# Site 3
cd third && python3 -m http.server 8082
```

## Order forms → Google Sheets

Each site has an order form. Submissions go to **separate tabs** in one Google Sheet.

1. Follow `google-apps-script/README.md` to deploy the script
2. Paste the `/exec` URL into `forms-config.js` (same URL for all three keys)
3. Redeploy on Vercel

| Site | Form fields |
|------|-------------|
| Patnjali | Name, Phone, Address, ZIP |
| Indian Health | Name, Phone, Address |
| Ayur More Well | Name, Phone, Address |

## Re-mirror a static site

```bash
python3 mirror_static.py "https://example.com/page/" output-folder
```
