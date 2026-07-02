from __future__ import annotations

from typing import Any

import requests
from flask import Blueprint, current_app, jsonify, request, session


auth_bp = Blueprint("auth", __name__)


def _extract_token(payload: dict[str, Any]) -> str | None:
    """Return a likely token field without coupling the prototype to one schema."""
    token_keys = ("token", "access_token", "jwt", "id_token", "bearer")
    for key in token_keys:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value

    # Some APIs return nested auth data.
    for container_key in ("data", "result", "auth", "authentication"):
        nested = payload.get(container_key)
        if isinstance(nested, dict):
            token = _extract_token(nested)
            if token:
                return token
    return None


def _safe_user(payload: dict[str, Any], username: str) -> dict[str, Any]:
    """Expose only user/session metadata that is safe for the browser."""
    user = payload.get("user") or payload.get("profile") or payload.get("data") or {}
    if not isinstance(user, dict):
        user = {}

    safe = {
        "username": user.get("username") or user.get("email") or username,
        "name": user.get("name") or user.get("displayName") or user.get("fullName"),
        "email": user.get("email"),
        "roles": user.get("roles") if isinstance(user.get("roles"), list) else [],
    }
    return {key: value for key, value in safe.items() if value not in (None, "")}


@auth_bp.post("/login")
def login():
    body = request.get_json(silent=True) or {}
    username = str(body.get("username", "")).strip()
    password = str(body.get("password", ""))

    if not username or not password:
        return jsonify({"ok": False, "error": "Username and password are required."}), 400

    upstream_payload = {
        "username": username,
        "password": password,
    }

    try:
        response = requests.post(
            current_app.config["UNIPARTHENOPE_LOGIN_URL"],
            json=upstream_payload,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            timeout=current_app.config["UNIPARTHENOPE_TIMEOUT_SECONDS"],
        )
    except requests.RequestException:
        current_app.logger.exception("Unable to reach UniParthenope login endpoint")
        return jsonify({"ok": False, "error": "Authentication service is not reachable."}), 502

    if response.status_code in (400, 401, 403):
        return jsonify({"ok": False, "error": "Invalid credentials or unauthorized access."}), 401

    if not response.ok:
        current_app.logger.warning("UniParthenope login failed with status %s", response.status_code)
        return jsonify({"ok": False, "error": "Authentication service returned an error."}), 502

    try:
        payload = response.json()
    except ValueError:
        return jsonify({"ok": False, "error": "Authentication service returned non-JSON data."}), 502

    token = _extract_token(payload)
    if not token:
        # Some deployments may use cookie-based auth; keep the prototype strict and explicit.
        return jsonify({"ok": False, "error": "Login succeeded but no token was found in the response."}), 502

    session.clear()
    session["authenticated"] = True
    session["api_token"] = token
    session["user"] = _safe_user(payload, username)

    return jsonify({"ok": True, "user": session["user"]})


@auth_bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"ok": True})


@auth_bp.get("/session")
def current_session():
    if not session.get("authenticated"):
        return jsonify({"ok": True, "authenticated": False})
    return jsonify({"ok": True, "authenticated": True, "user": session.get("user", {})})
