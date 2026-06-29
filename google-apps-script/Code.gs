/**
 * One Google Sheet, three tabs (one per site).
 * 1. Create a Google Sheet
 * 2. Extensions → Apps Script → paste this file
 * 3. Set SPREADSHEET_ID below
 * 4. Deploy → New deployment → Web app → Execute as: Me → Who has access: Anyone
 * 5. Copy the /exec URL into forms-config.js (all three sites)
 */

var SPREADSHEET_ID = "15Xdf8S95iikgvExAiXrPcYXnHRQp_tTFAxLumoBepiM";

var SHEET_MAP = {
  patnjali: "Patnjali Leads",
  second: "Indian Health Leads",
  third: "Ayur More Well Leads"
};

var HEADERS = ["Timestamp", "Name", "Phone", "Address", "ZIP", "Source"];

function doPost(e) {
  try {
    var params = e.parameter || {};
    var site = params.site || "unknown";
    var sheetName = SHEET_MAP[site] || site;
    var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
    var sheet = ss.getSheetByName(sheetName);

    if (!sheet) {
      sheet = ss.insertSheet(sheetName);
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
