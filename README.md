# UniParthenope PWA Auth Prototype

MIT-licensed Progressive Web Application prototype for authenticating a web app through the University of Naples "Parthenope" API endpoint:

```text
https://api.uniparthenope.it/UniparthenopeApp/v2/login
```

The project uses:

- Python 3 and Flask for serving the web app and backend authentication APIs
- HTML5, CSS3, JavaScript, Bootstrap, and jQuery for the frontend
- A Web App Manifest and Service Worker for PWA support
- Server-side Flask sessions so the upstream API token is not exposed to browser JavaScript

## Architecture

```text
Browser -> Flask /api/auth/login -> UniParthenope App login endpoint
Browser <- Flask secure session cookie <- Flask stores upstream token server-side
```

The frontend never calls the UniParthenope login endpoint directly. It posts credentials to the local Flask backend, which forwards them to the upstream API and stores the returned token in the server-side session.

## Project layout

```text
.
├── app/
│   ├── __init__.py
│   ├── auth.py
│   ├── config.py
│   ├── routes.py
│   ├── static/
│   │   ├── css/app.css
│   │   ├── icons/icon.svg
│   │   ├── js/app.js
│   │   ├── manifest.webmanifest
│   │   └── service-worker.js
│   └── templates/index.html
├── tests/test_auth.py
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
└── wsgi.py
```

## Quick start

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask --app wsgi run --debug
```

Open:

```text
http://127.0.0.1:5000
```

## Configuration

Copy `.env.example` to `.env` and edit it as needed:

```bash
SECRET_KEY=change-me-in-production
UNIPARTHENOPE_LOGIN_URL=https://api.uniparthenope.it/UniparthenopeApp/v2/login
UNIPARTHENOPE_TIMEOUT_SECONDS=10
SESSION_COOKIE_SECURE=false
```

For production HTTPS deployments, use:

```bash
SESSION_COOKIE_SECURE=true
```

## Local API endpoints

### `POST /api/auth/login`

Request body:

```json
{
  "username": "student-or-user-id",
  "password": "password"
}
```

Successful response:

```json
{
  "ok": true,
  "user": {
    "username": "student-or-user-id"
  }
}
```

### `GET /api/auth/session`

Returns the current local Flask session status.

### `POST /api/auth/logout`

Clears the local Flask session.

## Token handling

The prototype searches the upstream login JSON response for common token fields:

- `token`
- `access_token`
- `jwt`
- `id_token`
- `bearer`

It also checks nested containers such as `data`, `result`, `auth`, and `authentication`.

If the real API response uses a different field, update `_extract_token()` in `app/auth.py`.

## Security notes

This is a prototype, not a production security audit. Before production use:

- Replace the development `SECRET_KEY`
- Serve only over HTTPS
- Set `SESSION_COOKIE_SECURE=true`
- Add CSRF protection for form posts
- Add rate limiting and audit logging
- Avoid logging credentials or tokens
- Review the official API schema and response fields

## Tests

```bash
pytest -q
```

## License

Released under the MIT License. See [LICENSE](LICENSE).
