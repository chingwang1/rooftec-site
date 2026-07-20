/**
 * Cloudflare Worker — contact form → email via Resend
 *
 * POST JSON or form-urlencoded:
 *   { name, phone, email, suburb, service, message }
 *
 * Secrets (wrangler secret put):
 *   RESEND_API_KEY  — required (https://resend.com/api-keys)
 *   FORM_SECRET     — optional; if set, require header X-Form-Secret
 */

const DEFAULT_TO = "kylehunt2017@gmail.com";
const DEFAULT_FROM = "Roofing Brisbane <onboarding@resend.dev>";

function corsHeaders(origin, allowed) {
  const list = (allowed || "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
  // file:// pages send Origin: null
  const ok =
    !origin ||
    list.includes(origin) ||
    list.includes("null") ||
    list.some((o) => origin === o || (o.endsWith(".github.io") && origin.endsWith(".github.io")));

  const allowOrigin = ok && origin && origin !== "null" ? origin : list[0] || "*";

  return {
    "Access-Control-Allow-Origin": allowOrigin === "null" ? "*" : allowOrigin,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, X-Form-Secret",
    "Access-Control-Max-Age": "86400",
  };
}

function json(data, status, cors) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      ...cors,
    },
  });
}

function clean(s, max = 2000) {
  return String(s || "")
    .replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, "")
    .trim()
    .slice(0, max);
}

async function parseBody(request) {
  const type = request.headers.get("content-type") || "";
  if (type.includes("application/json")) {
    return await request.json();
  }
  if (type.includes("application/x-www-form-urlencoded") || type.includes("multipart/form-data")) {
    const fd = await request.formData();
    const obj = {};
    for (const [k, v] of fd.entries()) {
      if (typeof v === "string") obj[k] = v;
    }
    return obj;
  }
  // try json fallback
  try {
    return await request.json();
  } catch {
    return {};
  }
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    const cors = corsHeaders(origin, env.ALLOWED_ORIGINS);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }

    if (request.method !== "POST") {
      return json(
        {
          ok: true,
          service: "roofing-brisbane-contact",
          usage: "POST name, phone, email, suburb, service, message",
        },
        200,
        cors
      );
    }

    // Optional shared secret (set FORM_SECRET with wrangler)
    if (env.FORM_SECRET) {
      const got = request.headers.get("X-Form-Secret") || "";
      if (got !== env.FORM_SECRET) {
        return json({ ok: false, error: "Unauthorized" }, 401, cors);
      }
    }

    if (!env.RESEND_API_KEY) {
      return json(
        {
          ok: false,
          error: "RESEND_API_KEY not configured on Worker",
        },
        500,
        cors
      );
    }

    let body;
    try {
      body = await parseBody(request);
    } catch {
      return json({ ok: false, error: "Invalid body" }, 400, cors);
    }

    // Honeypot (bots fill hidden field)
    if (body._honey || body.website || body.company_url) {
      return json({ ok: true }, 200, cors);
    }

    const name = clean(body.name, 120);
    const phone = clean(body.phone, 40);
    const email = clean(body.email, 120);
    const suburb = clean(body.suburb, 120);
    const service = clean(body.service, 120);
    const message = clean(body.message, 4000);

    if (!name || !phone || !message) {
      return json(
        { ok: false, error: "name, phone and message are required" },
        400,
        cors
      );
    }

    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return json({ ok: false, error: "Invalid email" }, 400, cors);
    }

    const to = env.TO_EMAIL || DEFAULT_TO;
    const from = env.FROM_EMAIL || DEFAULT_FROM;

    const text = [
      "New enquiry from the Roofing Brisbane website",
      "",
      `Name:    ${name}`,
      `Phone:   ${phone}`,
      `Email:   ${email || "(not provided)"}`,
      `Suburb:  ${suburb || "(not provided)"}`,
      `Service: ${service || "(not provided)"}`,
      "",
      "Message:",
      message,
      "",
      `Received: ${new Date().toISOString()}`,
    ].join("\n");

    const html = `
      <h2>New website enquiry</h2>
      <table style="border-collapse:collapse;font-family:sans-serif;font-size:14px">
        <tr><td style="padding:4px 12px 4px 0;color:#666">Name</td><td><strong>${escapeHtml(name)}</strong></td></tr>
        <tr><td style="padding:4px 12px 4px 0;color:#666">Phone</td><td><a href="tel:${escapeHtml(phone)}">${escapeHtml(phone)}</a></td></tr>
        <tr><td style="padding:4px 12px 4px 0;color:#666">Email</td><td>${email ? `<a href="mailto:${escapeHtml(email)}">${escapeHtml(email)}</a>` : "—"}</td></tr>
        <tr><td style="padding:4px 12px 4px 0;color:#666">Suburb</td><td>${escapeHtml(suburb || "—")}</td></tr>
        <tr><td style="padding:4px 12px 4px 0;color:#666">Service</td><td>${escapeHtml(service || "—")}</td></tr>
      </table>
      <h3 style="margin-top:20px">Message</h3>
      <p style="white-space:pre-wrap;font-family:sans-serif">${escapeHtml(message)}</p>
    `;

    const res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${env.RESEND_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from,
        to: [to],
        reply_to: email || undefined,
        subject: `Roofing Brisbane enquiry${suburb ? ` — ${suburb}` : ""}${name ? ` (${name})` : ""}`,
        text,
        html,
      }),
    });

    const result = await res.json().catch(() => ({}));

    if (!res.ok) {
      console.error("Resend error", res.status, result);
      return json(
        {
          ok: false,
          error: "Email provider rejected the message",
          detail: result?.message || result?.name || String(res.status),
        },
        502,
        cors
      );
    }

    return json({ ok: true, id: result.id || null }, 200, cors);
  },
};

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
