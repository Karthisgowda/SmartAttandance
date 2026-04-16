# SmartAttandance

SmartAttandance is a Flask-based attendance management app for registering students, marking attendance, viewing attendance history, downloading CSV exports, and managing records through an admin panel.

## Live App

- Production URL: https://smartattandance.vercel.app

## Features

- Register students with photo upload
- Mark attendance manually
- View attendance by date
- Download attendance history as CSV
- Admin login and management panel
- Backup generation
- XAMPP package download page

## Tech Stack

- Python
- Flask
- Pandas
- Pillow
- Bootstrap 5
- Vercel

## Local Development

### Requirements

- Python 3.11 or newer

### Install

```bash
python -m pip install -r requirements.txt
```

### Run

```bash
python app.py
```

The app will start locally on:

```text
http://127.0.0.1:5000
```

## Environment Variables

Set these values for production:

- `SESSION_SECRET`: Flask session secret
- `ADMIN_PASSWORD`: admin login password

Current production admin password:

```text
123456
```

## Vercel Deployment

This project is deployed on Vercel as a Flask app.

### Important Note About Storage

On Vercel, runtime data is stored in `/tmp/smartattendance`, so uploaded student images and new attendance records are temporary unless persistent storage is added later.

## Project Structure

```text
app.py
requirements.txt
pyproject.toml
templates/
public/static/
assets/
data/
xampp_version/
```

## Admin Panel

The admin panel lets you:

- view system stats
- remove students
- clear attendance records by date range
- download a backup zip

## Repository

- GitHub: https://github.com/Karthisgowda/SmartAttandance

