# Face Recognition Attendance System - Deployment Guide

This guide explains how to deploy the Face Recognition Attendance System to Render.com.

## Render Deployment

### Quick Deploy
1. Connect your repository to Render
2. Use the following settings:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r render-requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

### Environment Variables
Set the following environment variable in your Render dashboard:

- `ADMIN_PASSWORD`: Set a secure password for admin access (required)

### Files for Deployment
- `render-requirements.txt` - Python dependencies
- `render.yaml` - Render configuration (optional)
- `Procfile` - Alternative start command configuration
- `.streamlit/config.toml` - Streamlit configuration

## Admin Panel
- The admin panel is only visible to authenticated users
- Default admin password is "admin123" (change using ADMIN_PASSWORD environment variable)
- Admin features:
  - View system statistics
  - Manage students and attendance records
  - Create system backups
  - Delete records (admin only)

## Security Features
- Password-protected admin panel
- Environment variable configuration for secrets
- Regular users cannot delete data
- Admin authentication required for system management

## Data Persistence
- Student images stored in `data/student_images/`
- Attendance records stored in `data/attendance/`
- All data persists across deployments
- Admin can create full system backups

## Troubleshooting
- Ensure ADMIN_PASSWORD environment variable is set
- Check that all required files are included in deployment
- Verify Python version compatibility (3.8+)
- Monitor deployment logs for any errors