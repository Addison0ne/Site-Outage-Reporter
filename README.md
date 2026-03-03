# Site Outage Reporter (Australia)

An IIS-hosted Python web app that polls Australian 4G providers (Telstra, Optus, Vodafone) and NBN outage feeds, stores outage events in SQL Server, and shows outages for specified sites.

## Features

- SQL Server integration through SQLAlchemy + pyodbc.
- Scheduled polling via APScheduler (optional via `ENABLE_SCHEDULER`).
- Manual polling endpoint (`POST /api/poll`).
- Website UI with site-code filtering (`?sites=MEL-001,SYD-002`).
- IIS hosting through `wfastcgi` with Windows Authentication passthrough.

## IIS-only deployment (Windows Authentication)

1. Install IIS features:
   - CGI
   - Windows Authentication
2. Install Python dependencies, including `wfastcgi`:

```bash
pip install -r requirements.txt
```

3. Copy environment variables and set SQL Server credentials:

```bash
copy .env.example .env
```

4. Update `web.config` values for your server:
   - `scriptProcessor` (Python executable + `wfastcgi.py`)
   - `PYTHONPATH` (site folder)
   - `WSGI_LOG` (log destination)
5. Place this project under your IIS site root.
6. In IIS, disable **Anonymous Authentication** and enable **Windows Authentication**.
7. Recycle the IIS application pool.

The app resolves the authenticated user from:
- `REMOTE_USER` (preferred with IIS FastCGI)
- `X-IIS-WindowsAuthUser` / `X-Forwarded-User` (for proxied deployments)

Use `GET /api/whoami` to verify the passed-through identity.

## Authentication behavior

- `REQUIRE_AUTH=true` (default): requests without IIS user identity receive HTTP 401.
- `REQUIRE_AUTH=false`: permits anonymous requests (only for troubleshooting).

## Scheduler behavior under IIS

If your IIS deployment uses multiple worker processes/instances, in-process schedulers can duplicate jobs.
For production, consider setting `ENABLE_SCHEDULER=false` and run polling from a single external scheduler (Windows Task Scheduler, SQL Agent, or a separate worker process).

## Provider integration notes

The provider URLs in `providers.py` are placeholders and should be replaced with real API endpoints or scrapers used by your organization.

Each provider response is expected in this shape:

```json
{
  "outages": [
    {
      "site_code": "MEL-001",
      "status": "OUTAGE",
      "description": "Tower power loss",
      "started_at": "2026-03-02T01:23:00Z",
      "updated_at": "2026-03-02T03:45:00Z"
    }
  ]
}
```
