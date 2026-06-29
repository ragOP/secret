(function () {
  function getSubmitButton(form) {
    return form.querySelector('button[type="submit"], input[type="submit"]');
  }

  function collectFields(form) {
    var data = new FormData();
    var site = form.dataset.site || "unknown";
    data.append("site", site);
    data.append("timestamp", new Date().toISOString());

    var mapping = {
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

  function handleSubmit(e) {
    var form = e.target;
    if (!form || form.tagName !== "FORM" || !form.dataset.site) return;

    e.preventDefault();
    e.stopPropagation();

    if (form.dataset.submitting === "1") return;
    form.dataset.submitting = "1";

    var site = form.dataset.site;
    var config = window.FORMS_CONFIG || {};
    var endpoint = config[site];

    if (!endpoint || endpoint.indexOf("YOUR_DEPLOYMENT_ID") !== -1) {
      form.dataset.submitting = "0";
      alert("Form backend not configured. Check forms-config.js");
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
        form.dataset.submitting = "0";
        alert(err.message || "Submit failed. Please try again.");
        if (btn) {
          btn.disabled = false;
          if (btn.tagName === "INPUT") btn.value = originalLabel;
          else btn.textContent = originalLabel;
        }
      });
  }

  document.addEventListener("submit", handleSubmit, true);
})();
