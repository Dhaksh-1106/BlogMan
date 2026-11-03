# BlogMan

BlogMan is a Flask-powered blogging website for publishing and reading posts, with user accounts, reader comments, and a contact form. Blog content is stored with SQLAlchemy, and posts can be composed using a rich-text editor.

## Features

- Browse published posts and open individual post pages.
- Register and sign in with an email address and password.
- Create, edit, and delete posts using the admin account.
- Write formatted posts and comments with CKEditor.
- Comment on posts while signed in.
- View About and Contact pages; contact submissions are sent by email.
- Use SQLite locally or configure another SQLAlchemy database URL, such as PostgreSQL.

## Technology

- **Backend:** Python, Flask, Flask-Login, Flask-SQLAlchemy, SQLAlchemy
- **Forms and validation:** Flask-WTF, WTForms, Email Validator
- **Presentation:** HTML, CSS, Bootstrap-Flask
- **Rich text:** Flask-CKEditor
- **Production server:** Gunicorn
- **Database:** SQLite by default; PostgreSQL is supported through `DB_URI`

## Getting started

### Prerequisites

- Python 3.10 or later (use a Python version compatible with the pinned dependencies)
- `pip` and `venv`
- For contact-form email delivery, a Gmail account and an app password

### 1. Get the code

```bash
git clone https://github.com/Dhaksh-1106/BlogMan.git
cd BlogMan
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Activate it with your platform's command:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Set a strong, private `SECRET_KEY` before starting the application. The app uses `sqlite:///blog.db` if `DB_URI` is not set.

| Variable | Required? | Purpose |
| --- | --- | --- |
| `SECRET_KEY` | Yes | Flask session and form-protection secret. |
| `DB_URI` | No | SQLAlchemy database URL. Defaults to `sqlite:///blog.db`. |
| `MY_EMAIL` | Only for contact email | Gmail address used as the SMTP account and recipient. |
| `PASSWORD` | Only for contact email | Gmail app password used for SMTP authentication. |

Example for macOS/Linux:

```bash
export SECRET_KEY="replace-with-a-long-random-secret"
# Optional, if using PostgreSQL:
# export DB_URI="postgresql+psycopg://user:password@localhost:5432/blogman"
# Optional, for the contact form:
# export MY_EMAIL="you@example.com"
# export PASSWORD="your-gmail-app-password"
```

Example for Windows PowerShell:

```powershell
$env:SECRET_KEY = "replace-with-a-long-random-secret"
# Optional:
# $env:DB_URI = "postgresql+psycopg://user:password@localhost:5432/blogman"
# $env:MY_EMAIL = "you@example.com"
# $env:PASSWORD = "your-gmail-app-password"
```

Do not commit real secrets, credentials, or production database URLs to the repository. For Gmail, use an app password where available rather than your regular account password.

### 5. Run locally

```bash
python main.py
```

Open the local address printed by Flask (typically <http://127.0.0.1:5000>). The database tables are created automatically when the app initializes. The default local database file is `blog.db`.

## Usage

1. Register an account from the site.
2. Sign in to comment on posts.
3. The application currently grants post-management access to the account whose database user ID is `1` (normally the first account created in a fresh database). That account can create posts and edit or delete posts.
4. Configure the email environment variables if you want the Contact form to send messages.

> **Admin access note:** Admin authorization is currently tied to the numeric user ID `1`, not to a configurable role. Protect initial account creation and review this authorization design before exposing a deployment to the public.

## Application pages

| Path | Description | Access |
| --- | --- | --- |
| `/` | List blog posts | Public |
| `/post/<post_id>` | Read a post and view or submit comments | Reading is public; commenting requires sign-in |
| `/register` | Create an account | Public |
| `/login` | Sign in | Public |
| `/logout` | Sign out | Signed-in user |
| `/new-post` | Create a post | Admin account (user ID `1`) |
| `/edit-post/<post_id>` | Edit a post | Admin account (user ID `1`) |
| `/delete/<post_id>` | Delete a post | Admin account (user ID `1`) |
| `/about` | About page | Public |
| `/contact` | Contact page and form | Public; email settings are needed to send messages |

## Project structure

```text
BlogMan/
├── main.py             # Flask app, database models, routes, and mail handling
├── forms.py            # WTForms for posts, accounts, and comments
├── requirements.txt    # Python dependencies
├── Procfile            # Gunicorn web process declaration
├── templates/          # Jinja templates for pages and shared layout
└── static/             # CSS, JavaScript, and image assets
```

## Deployment

The repository includes a `Procfile` that starts the application with Gunicorn:

```text
web: Gunicorn main:app
```

On a hosting provider that supports Procfiles, configure the environment variables described above and provide a persistent database URL for production (for example, PostgreSQL). Use a strong `SECRET_KEY`, keep credentials in the host's secret/environment-variable settings, and ensure the database is backed up. The SQLite fallback is intended for simple local use; many hosted environments do not guarantee persistence for local files.

## Data model

- **User**: name, unique email, and hashed password.
- **BlogPost**: unique title, subtitle, publication date, rich-text body, image URL, and author.
- **BlogComment**: rich-text body, author, and associated post.

Passwords are stored as hashes using Werkzeug's password-hashing helpers rather than as plaintext.

## Development notes

- Dependencies are pinned in `requirements.txt`.
- The database schema is created with `db.create_all()` at application startup. There is currently no migration workflow documented in the repository.
- The contact form uses Gmail SMTP with TLS and the `MY_EMAIL` / `PASSWORD` environment variables.
- No automated test command is currently documented.

## Contributing

Issues and pull requests are welcome. For changes, please describe the behavior being updated and include steps to verify it manually. Avoid including secrets or personal data in commits and issue reports.

## License

No license file is currently provided. Unless a license is added, the project should be treated as having no explicit open-source reuse license.
