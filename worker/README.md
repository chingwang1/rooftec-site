# Contact form Worker (Cloudflare + Resend)

Sends enquiries from the static GitHub Pages site to **kylehunt2017@gmail.com**.

GitHub Pages stays static. This Worker is the tiny backend that actually emails.

## One-time setup

### 1. Cloudflare account
- Sign up at [dash.cloudflare.com](https://dash.cloudflare.com) (free)
- Install Wrangler (or use the `npm` scripts here)

### 2. Resend account (free: 3,000 emails/month)
- [resend.com/signup](https://resend.com/signup)
- Create an API key: **API Keys → Create**
- For testing, you can send **from** `onboarding@resend.dev` **to** your own Gmail only  
- For production (send as your domain): add a domain in Resend and verify DNS, then set `FROM_EMAIL` to e.g. `Roofing Brisbane <hello@yourdomain.com.au>`

### 3. Install & log in

```powershell
cd $env:USERPROFILE\Desktop\rooftec-site\worker
npm install
npx wrangler login
```

### 4. Put the API key in a secret (not in git)

```powershell
npx wrangler secret put RESEND_API_KEY
# paste your re_... key when prompted
```

Optional:

```powershell
npx wrangler secret put TO_EMAIL
# kylehunt2017@gmail.com
```

### 5. Deploy

```powershell
npm run deploy
```

Wrangler prints a URL like:

```
https://roofing-brisbane-contact.<your-subdomain>.workers.dev
```

### 6. Point the website at the Worker

Set this in the site (or tell the agent to wire it) as `window.CONTACT_API_URL`:

```js
window.CONTACT_API_URL = "https://roofing-brisbane-contact.YOUR_SUBDOMAIN.workers.dev";
```

Or edit `js/contact-api.js` after deploy.

## Test

```powershell
curl -X POST https://roofing-brisbane-contact.YOUR_SUBDOMAIN.workers.dev ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Test\",\"phone\":\"0411510699\",\"email\":\"you@test.com\",\"suburb\":\"Brisbane\",\"service\":\"Repairs\",\"message\":\"Hello from curl\"}"
```

You should get `{ "ok": true }` and an email in Gmail.

## Local dev

```powershell
npx wrangler dev
# then POST to http://127.0.0.1:8787
```

## Security notes

- Never commit `RESEND_API_KEY`
- CORS only allows listed origins (`ALLOWED_ORIGINS` in `wrangler.toml`)
- Honeypot field `_honey` drops bots
- Optional `FORM_SECRET` header for extra lock-down
