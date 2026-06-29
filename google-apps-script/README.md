# Google Sheets setup (one spreadsheet, three tabs)

Each site writes to its own sheet tab:

| Site folder | Tab name |
|-------------|----------|
| `patnjali-clone/` | Patnjali Leads |
| `second/` | Indian Health Leads |
| `third/` | Ayur More Well Leads |

## Steps

1. Go to [Google Sheets](https://sheets.google.com) → **Blank spreadsheet**
2. Copy the spreadsheet ID from the URL:  
   `https://docs.google.com/spreadsheets/d/THIS_PART/edit`
3. Open **Extensions → Apps Script**
4. Replace the default code with `Code.gs` from this folder
5. Set `SPREADSHEET_ID` in `Code.gs`
6. **Deploy → New deployment → Web app**
   - Execute as: **Me**
   - Who has access: **Anyone**
7. Copy the **Web app URL** (ends with `/exec`)
8. Paste it into `/forms-config.js` for all three keys (`patnjali`, `second`, `third`)
9. Commit and redeploy on Vercel

## Test

Submit a test order on each site. You should see a new row in the matching tab.
