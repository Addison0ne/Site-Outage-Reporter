from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, abort, g, jsonify, render_template, request

from config import settings
from db import SessionLocal, get_outages_for_sites, init_db
from poller import poll_once

app = Flask(__name__)

scheduler = BackgroundScheduler(daemon=True)


def resolve_authenticated_user() -> str | None:
    """
    Resolve IIS-authenticated user identity.

    IIS + FastCGI commonly forwards identities in REMOTE_USER and can optionally
    inject x-iis-windowsauthuser / x-forwarded-user headers when ARR or reverse
    proxy layers are involved.
    """
    user = request.environ.get("REMOTE_USER")
    if user:
        return user

    trusted_headers = ["X-IIS-WindowsAuthUser", "X-Forwarded-User"]
    for header in trusted_headers:
        value = request.headers.get(header)
        if value:
            return value

    return None


@app.before_request
def bootstrap() -> None:
    if settings.enable_scheduler and not scheduler.running:
        init_db()
        scheduler.add_job(
            poll_once,
            "interval",
            minutes=settings.poll_interval_minutes,
            id="provider-poll",
            replace_existing=True,
        )
        scheduler.start()

    g.authenticated_user = resolve_authenticated_user()
    if settings.require_auth and g.authenticated_user is None:
        abort(401)


@app.errorhandler(401)
def unauthorized(_):
    return (
        jsonify({"error": "Authentication required (IIS Windows Authentication)."})
        if request.path.startswith("/api/")
        else ("Authentication required (IIS Windows Authentication).", 401)
    )


@app.get("/")
def home():
    site_codes_param = request.args.get("sites", "")
    site_codes = [s.strip().upper() for s in site_codes_param.split(",") if s.strip()]
    db = SessionLocal()
    try:
        outages = get_outages_for_sites(db, site_codes)
        return render_template(
            "index.html",
            outages=outages,
            site_codes=site_codes_param,
            authenticated_user=g.authenticated_user,
        )
    finally:
        db.close()


@app.post("/api/poll")
def manual_poll():
    result = poll_once()
    return jsonify(result)


@app.get("/api/whoami")
def whoami():
    return jsonify({"user": g.authenticated_user})


# IIS hosts this application through wfastcgi + wsgi.py.
# Intentionally no Flask development server entrypoint.
