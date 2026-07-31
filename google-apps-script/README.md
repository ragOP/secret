# Google Sheets setup

| Site folder | Destination |
|-------------|-------------|
| `patnjali-clone/` | Shared spreadsheet → tab **Patnjali Leads** |
| `second/` | Shared spreadsheet → tab **Indian Health Leads** |
| `third/` | Shared spreadsheet → tab **Ayur More Well Leads** |
| `four/` | **Separate spreadsheet** → tab **Leads** |

## Shared sheet (sites 1–3)

1. Spreadsheet ID is already set as `SPREADSHEET_ID` in `Code.gs`
2. Tabs are created automatically on first submit if missing

## Four — new spreadsheet (not a tab)

1. Open [Google Sheets](https://sheets.google.com) → **Blank spreadsheet**
2. Rename it something like **Four Leads**
3. Copy the spreadsheet ID from the URL:  
   `https://docs.google.com/spreadsheets/d/THIS_PART/edit`
4. Paste that ID into `FOUR_SPREADSHEET_ID` in `Code.gs`
5. In the **existing** Apps Script project (Extensions → Apps Script on the shared sheet, or the script you already deploy):
   - Replace code with the updated `Code.gs`
   - **Deploy → Manage deployments → Edit → New version** (or New deployment)
6. Keep the same `/exec` URL in `forms-config.js` for all four keys (including `four`)

On first submit from `/four/`, the script creates a **Leads** tab inside that new spreadsheet.

## First-time deploy (if starting fresh)

1. Open **Extensions → Apps Script** on the shared sheet
2. Paste `Code.gs` and set both spreadsheet IDs
3. **Deploy → New deployment → Web app**
   - Execute as: **Me**
   - Who has access: **Anyone**
4. Copy the **Web app URL** (ends with `/exec`) into `/forms-config.js`
5. Commit and redeploy on Vercel

## Test

Submit a test order on `/four/`. Rows should appear in the **new** spreadsheet, not as a tab on the shared one.
