# Face Recognition Attendance System

## Project Overview
A comprehensive Face Recognition Attendance System built with Python, leveraging Streamlit for the web interface. The system provides both a web-based version and a downloadable XAMPP version for local deployment.

## Recent Changes
- ✅ Created complete PHP/MySQL version for XAMPP deployment
- ✅ Added secure admin panel with password authentication (environment variable based)
- ✅ Implemented Render deployment configuration with proper files
- ✅ Added data persistence and admin-only access controls
- ✅ Created system backup functionality for admin users
- ✅ Protected data deletion features (admin-only access)
- ✅ Added deployment files: render-requirements.txt, render.yaml, Procfile, config.toml

## User Preferences
- Deploy to Render platform
- Admin panel should be secure and only visible to authorized users
- Data should not be deletable except by admin users
- Admin panel should be separate from regular user interface

## Project Architecture
- **Frontend**: Streamlit web application
- **Backend**: File-based storage (CSV) with optional MySQL for XAMPP version
- **Authentication**: Admin panel with password protection
- **Deployment**: Render platform with environment variables for secrets
- **File Structure**: 
  - `app.py` - Main Streamlit application
  - `admin_panel.py` - Secure admin interface
  - `requirements.txt` - Python dependencies
  - `render.yaml` - Render deployment configuration

## Features
- Student registration with photo upload
- Manual attendance marking
- Attendance viewing and export
- Admin panel for system management
- XAMPP version for local deployment
- Data migration tools

## Security
- Admin panel protected with environment variable authentication
- Regular users cannot delete data
- Admin-only data management capabilities