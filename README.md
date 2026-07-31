# secret

Offline mirrors of four landing pages.

| Folder | Site | Entry |
|--------|------|-------|
| `patnjali-clone/` | patnjali.online | `index.html` → age gate, then `home1.html` |
| `second/` | indianhealth.store/x1 | `index.html` |
| `third/` | ayurmorewell.online | `index.html` |
| `four/` | ayurmorewell.online (clone) | `index.html` — **own Google Spreadsheet** |

## Run locallys

```bash
# Site 1
cd patnjali-clone && python3 finalize.py && python3 -m http.server 8080

# Site 2
cd second && python3 -m http.server 8081

# Site 3
cd third && python3 -m http.server 8082

# Site 4
cd four && python3 -m http.server 8083
```

## Order forms → Google Sheets

Each site has an order form. Sites 1–3 share one spreadsheet (separate tabs). **Four uses its own Google Spreadsheet.**

1. Follow `google-apps-script/README.md` to deploy the script
2. Create a blank sheet for four and paste its ID into `FOUR_SPREADSHEET_ID` in `Code.gs`
3. Paste the `/exec` URL into `forms-config.js` (same URL for all four keys)
4. Redeploy on Vercel

| Site | Form fields | Sheet |
|------|-------------|-------|
| Patnjali | Name, Phone, Address, ZIP | Shared tab |
| Indian Health | Name, Phone, Address | Shared tab |
| Ayur More Well | Name, Phone, Address | Shared tab |
| Four | Name, Phone, Address | **New spreadsheet** |

## Re-mirror a static site

```bash
python3 mirror_static.py "https://example.com/page/" output-folder
```
