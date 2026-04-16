# Smart Attendance System - Vercel Deployment Guide

This project now deploys to Vercel as a Flask application.

## Vercel Deployment

### Build Behavior
- Vercel detects the Flask app from `app.py`
- Python dependencies are installed from `requirements.txt`
- The application entrypoint is the Flask `app` object in `app.py`

### Required Environment Variables
- `ADMIN_PASSWORD`: password for admin access
- `SESSION_SECRET`: secret key for Flask sessions

### Important Runtime Note
- On Vercel, this app stores runtime data under `/tmp/smartattendance`
- That means uploaded student photos and new attendance records are temporary unless you connect persistent storage

### Included Features
- Student registration with image upload
- Manual attendance marking
- Attendance history and CSV export
- Admin login and management panel
- Backup generation
- XAMPP package download page

### Local Run
```bash
python -m pip install -r requirements.txt
python app.py
```

### Production URL
After deployment, Vercel provides a project URL such as:

```text
https://smartattandance.vercel.app
```
