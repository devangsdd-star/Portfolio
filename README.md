# Devang — Personal Portfolio

A responsive, dark-themed personal portfolio built with HTML, CSS, JavaScript, Python Flask and SQLite.

## Features

- Responsive layout for desktop, tablet and mobile
- Smooth navigation and scroll reveal animations
- Expandable project cards with keyboard support
- Contact form connected to a Flask API
- Server-side validation and SQLite message storage
- Basic anti-spam honeypot and submission cooldown
- Visitor counter stored in SQLite
- Health endpoint at `/api/health`

## Run locally

1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Create and activate a virtual environment:

   **Windows PowerShell**
   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

4. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

5. Start the application:
   ```powershell
   python app.py
   ```

6. Open `http://127.0.0.1:5000` in your browser.

The SQLite database (`portfolio.db`) is created automatically when the app runs. Contact submissions are saved in its `messages` table.

## Useful API routes

- `GET /api/health` — confirms the Flask service is running.
- `POST /api/contact` — validates and stores a contact message.

Example JSON body:
```json
{
  "name": "Alex",
  "email": "alex@example.com",
  "subject": "Project collaboration",
  "message": "I would like to discuss a project with you.",
  "company": ""
}
```

## Before submitting / publishing

Update the placeholder education details in `templates/index.html`. Review the skills and project descriptions so they accurately reflect your contribution. Add your real email and social profile links if you want them displayed.

## Deploying

Push this folder to a GitHub repository and connect the repository to Render. Render can detect `render.yaml`, or you can create a Web Service manually with:

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`

**Important database note:** the default SQLite database is suitable for local development and a simple assignment demonstration. Many free web-hosting instances use temporary filesystems, so SQLite data may disappear after a restart or redeploy. For persistent production contact storage, attach a persistent disk and set `DATABASE_PATH` to a file on that disk, or replace SQLite with a managed database such as Supabase.

## Assignment explanation

The Python backend is implemented using Flask. When a visitor submits the contact form, JavaScript sends the form data to `/api/contact`. Flask validates the name, email and message on the server, applies a basic anti-spam cooldown, and inserts valid messages into an SQLite database using parameterized SQL. The API returns a JSON response that the front end displays to the visitor.
