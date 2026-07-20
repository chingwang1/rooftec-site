/**
 * Posts contact forms to the Cloudflare Worker (Resend email).
 *
 * After you deploy the worker, set your URL below (or before this script):
 *   window.CONTACT_API_URL = "https://roofing-brisbane-contact.xxx.workers.dev";
 *
 * Until that URL is set, forms fall back to FormSubmit so the site still works.
 */
(function () {
  var FALLBACK =
    "https://formsubmit.co/ajax/kylehunt2017@gmail.com";

  function apiUrl() {
    return window.CONTACT_API_URL || "";
  }

  function getFields(form) {
    var fd = new FormData(form);
    return {
      name: (fd.get("name") || "").toString().trim(),
      phone: (fd.get("phone") || "").toString().trim(),
      email: (fd.get("email") || "").toString().trim(),
      suburb: (fd.get("suburb") || "").toString().trim(),
      service: (fd.get("service") || "").toString().trim(),
      message: (fd.get("message") || "").toString().trim(),
      _honey: (fd.get("_honey") || "").toString(),
    };
  }

  function showStatus(form, ok, text) {
    var el = form.querySelector(".form-status");
    if (!el) {
      el = document.createElement("p");
      el.className = "form-status guarantee";
      el.style.marginTop = "12px";
      form.appendChild(el);
    }
    el.style.display = "block";
    el.style.borderColor = ok ? "#86efac" : "#fca5a5";
    el.style.background = ok ? "#f0fdf4" : "#fef2f2";
    el.style.color = ok ? "#166534" : "#991b1b";
    el.innerHTML = text;
  }

  async function submitForm(form) {
    var data = getFields(form);
    if (!data.name && form.querySelector("[name=name]")) {
      showStatus(form, false, "Please enter your name.");
      return;
    }
    // Homepage only has email + message — synthesize name
    if (!data.name) data.name = data.email || "Website visitor";
    if (!data.phone) data.phone = "Not provided";
    if (!data.message) {
      showStatus(form, false, "Please enter a message.");
      return;
    }

    var btn = form.querySelector('[type="submit"]');
    var prev = btn ? btn.textContent : "";
    if (btn) {
      btn.disabled = true;
      btn.textContent = "Sending…";
    }

    var url = apiUrl();
    try {
      var res;
      if (url) {
        res = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json", Accept: "application/json" },
          body: JSON.stringify(data),
        });
      } else {
        // Fallback: FormSubmit AJAX until Worker URL is configured
        res = await fetch(FALLBACK, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
          },
          body: JSON.stringify({
            name: data.name,
            phone: data.phone,
            email: data.email,
            suburb: data.suburb,
            service: data.service,
            message: data.message,
            _subject: "Roofing Brisbane — website enquiry",
          }),
        });
      }

      var body = await res.json().catch(function () {
        return {};
      });

      if (!res.ok || body.ok === false || body.success === "false") {
        throw new Error(body.error || body.message || "Send failed");
      }

      showStatus(
        form,
        true,
        "<strong>Thanks — your message was sent.</strong> We’ll get back to you soon."
      );
      form.reset();
    } catch (err) {
      showStatus(
        form,
        false,
        "<strong>Could not send.</strong> Please call <a href='tel:+61481255051'>0481 255 051</a> or email <a href='mailto:kylehunt2017@gmail.com'>kylehunt2017@gmail.com</a>."
      );
      console.error(err);
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.textContent = prev;
      }
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("form.js-contact-api").forEach(function (form) {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        submitForm(form);
      });
    });
  });
})();
