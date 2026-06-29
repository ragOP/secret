(function () {
  function getSubmitButton(form) {
    return form.querySelector('button[type="submit"], input[type="submit"]');
  }

  function collectFields(form) {
    const data = new FormData();
    const site = form.dataset.site || "unknown";
    data.append("site", site);
    data.append("timestamp", new Date().toISOString());

    const mapping = {
      name: ["name", "form_fields[name]"],
      phone: ["phone", "phonenumber", "form_fields[phone]"],
      address: ["address", "form_fields[address]"],
      zip: ["zip", "form_fields[zip]"]
    };

    Object.keys(mapping).forEach(function (key) {
      for (var i = 0; i < mapping[key].length; i++) {
        var field = form.elements.namedItem(mapping[key][i]);
        if (field && field.value && String(field.value).trim()) {
          data.append(key, String(field.value).trim());
          break;
        }
      }
    });

    return data;
  }

  function bindForm(form) {
    if (!form || form.dataset.sheetsBound === "1") return;

    var site = form.dataset.site;
    var config = window.FORMS_CONFIG || {};
    var endpoint = config[site];

    if (!endpoint || endpoint.indexOf("YOUR_DEPLOYMENT_ID") !== -1) {
      console.warn("Configure FORMS_CONFIG." + site + " in forms-config.js");
    }

    form.dataset.sheetsBound = "1";
    form.addEventListener("submit", function (e) {
      e.preventDefault();

      if (!endpoint || endpoint.indexOf("YOUR_DEPLOYMENT_ID") !== -1) {
        alert("Form backend not configured yet. Add your Google Apps Script URL in forms-config.js");
        return;
      }

      var btn = getSubmitButton(form);
      var originalLabel = btn ? (btn.value || btn.textContent) : "";

      if (btn) {
        btn.disabled = true;
        if (btn.tagName === "INPUT") btn.value = "Please wait...";
        else btn.textContent = "Please wait...";
      }

      fetch(endpoint, { method: "POST", body: collectFields(form) })
        .then(function (res) { return res.json(); })
        .then(function (data) {
          if (data.status === "success") {
            window.location.href = form.dataset.thankyou || "thankyou.html";
            return;
          }
          throw new Error(data.message || "Submit failed");
        })
        .catch(function (err) {
          alert(err.message || "Submit failed. Please try again.");
          if (btn) {
            btn.disabled = false;
            if (btn.tagName === "INPUT") btn.value = originalLabel;
            else btn.textContent = originalLabel;
          }
        });
    });
  }

  function init() {
    document.querySelectorAll("form[data-site]").forEach(bindForm);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
