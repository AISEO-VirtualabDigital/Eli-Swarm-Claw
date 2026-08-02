# Subdomain Deployment Notes

## Placeholder DNS
- Create a CNAME or A record placeholder for the future subdomain, for example:
  - app.<your-domain>
  - eli.<your-domain>

## Reverse proxy placeholder
- Configure a reverse proxy to route the subdomain to this pilot control app.
- Keep the proxy layer simple and dry-run only for the initial rollout.

## Environment variables
- PILOT_MODE=dry-run-only
- PILOT_CONTROL_BASE_URL=https://<placeholder-subdomain>
- PILOT_API_BASE_URL=https://<placeholder-api-subdomain>

## Safety warning
- This pilot control experience is intentionally dry-run only.
- Do not connect it to live execution backends yet.
- Do not publish production secrets or real credentials.
