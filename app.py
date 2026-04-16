import base64
import io
import os
import zipfile
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from PIL import Image


BASE_DIR = Path(__file__).resolve().parent
RUNTIME_ROOT = Path("/tmp/smartattendance") if os.environ.get("VERCEL") else BASE_DIR
DATA_DIR = RUNTIME_ROOT / "data"
STUDENT_DIR = DATA_DIR / "student_images"
ATTENDANCE_DIR = DATA_DIR / "attendance"
ASSETS_DIR = BASE_DIR / "assets"

STUDENT_DIR.mkdir(parents=True, exist_ok=True)
ATTENDANCE_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(
    __name__,
    static_folder=str(BASE_DIR / "public" / "static"),
    template_folder=str(BASE_DIR / "templates"),
)
app.secret_key = os.environ.get("SESSION_SECRET", "smart-attendance-development-secret")


def load_logo_base64() -> str:
    logo_path = ASSETS_DIR / "logo.svg"
    if not logo_path.exists():
        return ""
    return base64.b64encode(logo_path.read_bytes()).decode()


def get_admin_password() -> str:
    return os.environ.get("ADMIN_PASSWORD", "admin123")


def is_admin() -> bool:
    return bool(session.get("admin_authenticated"))


def attendance_file_for(date_value) -> Path:
    return ATTENDANCE_DIR / f"attendance_{date_value.strftime('%Y-%m-%d')}.csv"


def initialize_attendance_file(date_value=None) -> Path:
    if date_value is None:
        date_value = datetime.now()
    file_path = attendance_file_for(date_value)
    if not file_path.exists():
        pd.DataFrame(columns=["Name", "Time", "Date"]).to_csv(file_path, index=False)
    return file_path


def get_registered_students():
    if not STUDENT_DIR.exists():
        return []
    return sorted(
        [
            file.stem
            for file in STUDENT_DIR.iterdir()
            if file.suffix.lower() in {".jpg", ".jpeg", ".png"} and file.is_file()
        ]
    )


def get_student_image_path(student_name: str) -> Path:
    for suffix in (".jpg", ".jpeg", ".png"):
        candidate = STUDENT_DIR / f"{student_name}{suffix}"
        if candidate.exists():
            return candidate
    return STUDENT_DIR / f"{student_name}.jpg"


def get_all_attendance() -> pd.DataFrame:
    files = sorted(ATTENDANCE_DIR.glob("attendance_*.csv"))
    if not files:
        return pd.DataFrame(columns=["Name", "Time", "Date"])

    rows = []
    for file_path in files:
        try:
            rows.append(pd.read_csv(file_path))
        except Exception:
            continue

    if not rows:
        return pd.DataFrame(columns=["Name", "Time", "Date"])
    return pd.concat(rows, ignore_index=True)


def mark_attendance(student_name: str) -> bool:
    file_path = initialize_attendance_file()
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    df = pd.read_csv(file_path)
    already_marked = ((df["Name"] == student_name) & (df["Date"] == date_str)).any()
    if already_marked:
        return False

    new_row = pd.DataFrame({"Name": [student_name], "Time": [time_str], "Date": [date_str]})
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(file_path, index=False)
    return True


def remove_student(student_name: str) -> None:
    image_path = get_student_image_path(student_name)
    if image_path.exists():
        image_path.unlink()

    for file_path in ATTENDANCE_DIR.glob("attendance_*.csv"):
        try:
            df = pd.read_csv(file_path)
        except Exception:
            continue

        filtered = df[df["Name"] != student_name]
        filtered.to_csv(file_path, index=False)


def clear_attendance_range(start_date, end_date) -> int:
    removed_count = 0
    for file_path in ATTENDANCE_DIR.glob("attendance_*.csv"):
        try:
            df = pd.read_csv(file_path)
        except Exception:
            continue

        if df.empty:
            continue

        original_count = len(df)
        df["Date"] = pd.to_datetime(df["Date"]).dt.date
        filtered = df[(df["Date"] < start_date) | (df["Date"] > end_date)]
        removed_count += original_count - len(filtered)
        filtered["Date"] = filtered["Date"].astype(str)
        filtered.to_csv(file_path, index=False)
    return removed_count


def get_attendance_summary(attendance_df: pd.DataFrame):
    if attendance_df.empty:
        return {
            "total_records": 0,
            "active_days": 0,
            "recent_records": [],
            "history_table": [],
            "history_columns": [],
        }

    recent_records = (
        attendance_df.sort_values(["Date", "Time"], ascending=False)
        .head(10)
        .to_dict(orient="records")
    )

    pivot = attendance_df.pivot_table(
        index="Date",
        columns="Name",
        values="Time",
        aggfunc="first",
        fill_value="Absent",
    )
    for column in pivot.columns:
        pivot[column] = pivot[column].apply(lambda value: "Present" if value != "Absent" else "Absent")

    history_table = []
    for index, row in pivot.reset_index().iterrows():
        history_table.append(row.to_dict())

    return {
        "total_records": len(attendance_df),
        "active_days": int(attendance_df["Date"].nunique()),
        "recent_records": recent_records,
        "history_table": history_table,
        "history_columns": list(pivot.reset_index().columns),
    }


def build_backup() -> io.BytesIO:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for image_path in STUDENT_DIR.glob("*"):
            if image_path.is_file():
                archive.write(image_path, arcname=f"data/student_images/{image_path.name}")

        for attendance_path in ATTENDANCE_DIR.glob("attendance_*.csv"):
            archive.write(attendance_path, arcname=f"data/attendance/{attendance_path.name}")

    buffer.seek(0)
    return buffer


def xampp_downloads():
    return [
        {
            "label": "Download ZIP Version (Windows)",
            "path": BASE_DIR / "xampp_version" / "downloads" / "face_recognition_attendance_system_xampp_version.zip",
            "filename": "face_recognition_attendance_system_xampp_version.zip",
            "mime": "application/zip",
        },
        {
            "label": "Download TAR.GZ Version (Linux/Mac)",
            "path": BASE_DIR / "xampp_version" / "downloads" / "face_recognition_attendance_system_xampp_version.tar.gz",
            "filename": "face_recognition_attendance_system_xampp_version.tar.gz",
            "mime": "application/gzip",
        },
    ]


@app.context_processor
def inject_globals():
    return {
        "logo_base64": load_logo_base64(),
        "is_admin": is_admin(),
        "vercel_runtime": bool(os.environ.get("VERCEL")),
    }


@app.get("/")
def home():
    students = get_registered_students()
    stats = get_attendance_summary(get_all_attendance())
    return render_template("home.html", students=students, stats=stats)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password", "")
        if password == get_admin_password():
            session["admin_authenticated"] = True
            flash("Admin access granted.", "success")
            return redirect(url_for("admin_panel"))
        flash("Invalid admin password.", "danger")
    return render_template("login.html")


@app.post("/logout")
def logout():
    session.pop("admin_authenticated", None)
    flash("Logged out successfully.", "success")
    return redirect(url_for("home"))


@app.route("/register", methods=["GET", "POST"])
def register_student():
    existing_students = get_registered_students()

    if request.method == "POST":
        student_name = request.form.get("student_name", "").strip()
        uploaded_file = request.files.get("photo")

        if not student_name:
            flash("Student name is required.", "danger")
        elif student_name in existing_students:
            flash(f"{student_name} is already registered.", "warning")
        elif not uploaded_file or uploaded_file.filename == "":
            flash("Please upload a student photo.", "danger")
        else:
            image = Image.open(uploaded_file.stream)
            if image.mode == "RGBA":
                image = image.convert("RGB")
            image_path = STUDENT_DIR / f"{student_name}.jpg"
            image.save(image_path)
            flash(f"{student_name} registered successfully.", "success")
            return redirect(url_for("home"))

    return render_template("register.html", students=existing_students)


@app.route("/manual", methods=["GET", "POST"])
def manual_attendance():
    students = get_registered_students()
    today_file = initialize_attendance_file()
    today_records = pd.read_csv(today_file) if today_file.exists() else pd.DataFrame(columns=["Name", "Time", "Date"])

    if request.method == "POST":
        selected_student = request.form.get("student_name", "")
        if not selected_student:
            flash("Select a student first.", "danger")
        elif selected_student not in students:
            flash("Selected student does not exist.", "danger")
        else:
            if mark_attendance(selected_student):
                flash(f"Attendance marked for {selected_student}.", "success")
            else:
                flash(f"Attendance already marked for {selected_student} today.", "info")
        return redirect(url_for("manual_attendance"))

    return render_template(
        "manual.html",
        students=students,
        today_records=today_records.to_dict(orient="records"),
    )


@app.route("/attendance")
def view_attendance():
    selected_date = request.args.get("date")
    if selected_date:
        try:
            current_date = datetime.strptime(selected_date, "%Y-%m-%d")
        except ValueError:
            current_date = datetime.now()
    else:
        current_date = datetime.now()

    attendance_file = attendance_file_for(current_date)
    selected_records = (
        pd.read_csv(attendance_file).to_dict(orient="records")
        if attendance_file.exists()
        else []
    )

    attendance_history = get_all_attendance()
    stats = get_attendance_summary(attendance_history)

    return render_template(
        "attendance.html",
        selected_date=current_date.strftime("%Y-%m-%d"),
        selected_records=selected_records,
        stats=stats,
    )


@app.get("/attendance/download")
def download_attendance():
    attendance_history = get_all_attendance()
    csv_bytes = attendance_history.to_csv(index=False).encode()
    return send_file(
        io.BytesIO(csv_bytes),
        mimetype="text/csv",
        as_attachment=True,
        download_name="attendance_history.csv",
    )


@app.route("/xampp")
def xampp_version():
    downloads = [item for item in xampp_downloads() if item["path"].exists()]
    return render_template("xampp.html", downloads=downloads)


@app.get("/xampp/download/<filename>")
def download_xampp_asset(filename):
    for item in xampp_downloads():
        if item["filename"] == filename and item["path"].exists():
            return send_file(item["path"], mimetype=item["mime"], as_attachment=True, download_name=item["filename"])
    flash("Requested download is not available.", "warning")
    return redirect(url_for("xampp_version"))


@app.route("/admin")
def admin_panel():
    if not is_admin():
        flash("Please log in as admin to access the admin panel.", "warning")
        return redirect(url_for("login"))

    students = get_registered_students()
    attendance_df = get_all_attendance()
    stats = get_attendance_summary(attendance_df)
    student_records = defaultdict(int)
    if not attendance_df.empty:
        for name, count in attendance_df["Name"].value_counts().items():
            student_records[name] = int(count)

    return render_template(
        "admin.html",
        students=students,
        attendance_df=attendance_df.to_dict(orient="records"),
        stats=stats,
        student_records=student_records,
        default_start=(datetime.now().date() - timedelta(days=30)).isoformat(),
        default_end=datetime.now().date().isoformat(),
    )


@app.post("/admin/remove-student")
def admin_remove_student():
    if not is_admin():
        flash("Admin access required.", "danger")
        return redirect(url_for("login"))

    student_name = request.form.get("student_name", "").strip()
    if student_name:
        remove_student(student_name)
        flash(f"{student_name} removed successfully.", "success")
    return redirect(url_for("admin_panel"))


@app.post("/admin/clear-range")
def admin_clear_range():
    if not is_admin():
        flash("Admin access required.", "danger")
        return redirect(url_for("login"))

    start_value = request.form.get("start_date", "")
    end_value = request.form.get("end_date", "")
    confirmed = request.form.get("confirmed") == "on"

    if not confirmed:
        flash("Please confirm the clear action before submitting.", "warning")
        return redirect(url_for("admin_panel"))

    try:
        start_date = datetime.strptime(start_value, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_value, "%Y-%m-%d").date()
    except ValueError:
        flash("Invalid date range.", "danger")
        return redirect(url_for("admin_panel"))

    removed_count = clear_attendance_range(start_date, end_date)
    flash(f"Removed {removed_count} attendance records.", "success")
    return redirect(url_for("admin_panel"))


@app.get("/admin/backup")
def admin_backup():
    if not is_admin():
        flash("Admin access required.", "danger")
        return redirect(url_for("login"))

    backup = build_backup()
    filename = f"system_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    return send_file(
        backup,
        mimetype="application/zip",
        as_attachment=True,
        download_name=filename,
    )


@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=True)
