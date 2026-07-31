/**
 * Sites 1–3 share one spreadsheet (different tabs).
 * Site four uses its OWN separate Google Spreadsheet (not a tab).
 *
 * Setup:
 * 1. Keep SPREADSHEET_ID for patnjali / second / third
 * 2. Create a blank Google Sheet for four → paste its ID into FOUR_SPREADSHEET_ID
 * 3. Deploy → New deployment → Web app → Execute as: Me → Anyone
 * 4. Paste the /exec URL into forms-config.js
 */

var SPREADSHEET_ID = "15Xdf8S95iikgvExAiXrPcYXnHRQp_tTFAxLumoBepiM";

// Separate spreadsheet for /four/ — NOT a tab on the sheet above.
// Create at https://sheets.google.com → Blank → copy ID from URL:
// https://docs.google.com/spreadsheets/d/THIS_PART/edit
var FOUR_SPREADSHEET_ID = "1zQCXThLsgCX7Hwhi8FfjOBpyfgv3N68N4T3gKekQwAQ";

var SITE_CONFIG = {
  patnjali: { spreadsheetId: SPREADSHEET_ID, sheetName: "Patnjali Leads" },
  second: { spreadsheetId: SPREADSHEET_ID, sheetName: "Indian Health Leads" },
  third: { spreadsheetId: SPREADSHEET_ID, sheetName: "Ayur More Well Leads" },
  four: { spreadsheetId: FOUR_SPREADSHEET_ID, sheetName: "Leads" }
};

var HEADERS = ["Timestamp", "Name", "Phone", "Address", "ZIP", "Source"];

function doPost(e) {
  try {
    var params = e.parameter || {};
    var site = params.site || "unknown";
    var config = SITE_CONFIG[site];

    if (!config) {
      return json_({ status: "error", message: "Unknown site: " + site });
    }

    if (!config.spreadsheetId || config.spreadsheetId.indexOf("PASTE_") === 0) {
      return json_({
        status: "error",
        message: "Spreadsheet not configured for site: " + site
      });
    }

    var ss = SpreadsheetApp.openById(config.spreadsheetId);
    var sheet = ss.getSheetByName(config.sheetName);

    if (!sheet) {
      sheet = ss.insertSheet(config.sheetName);
      sheet.appendRow(HEADERS);
    } else if (sheet.getLastRow() === 0) {
      sheet.appendRow(HEADERS);
    }

    sheet.appendRow([
      params.timestamp || new Date().toISOString(),
      params.name || "",
      params.phone || params.phonenumber || "",
      params.address || "",
      params.zip || "",
      site
    ]);

    return json_({ status: "success" });
  } catch (err) {
    return json_({ status: "error", message: String(err) });
  }
}

function doGet() {
  return json_({ status: "ok" });
}

function json_(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
