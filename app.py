import os
import sqlite3
from functools import wraps
from pathlib import Path

from flask import Flask, g, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "instance" / "business_process_manager.db"
ALLOWED_STEP_STATUSES = ["Pending", "In Progress", "Completed"]


def get_db():
    if "db" not in g:
        DATABASE.parent.mkdir(exist_ok=True)
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        );
        CREATE TABLE IF NOT EXISTS processes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            owner TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending'
        );
        CREATE TABLE IF NOT EXISTS workflow_steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            process_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            step_order INTEGER NOT NULL,
            FOREIGN KEY (process_id) REFERENCES processes (id) ON DELETE CASCADE
        );
    """)

    if db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        db.executemany(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            [
                ("admin", generate_password_hash("admin123"), "admin"),
                ("user", generate_password_hash("user123"), "user"),
            ],
        )

    if db.execute("SELECT COUNT(*) FROM processes").fetchone()[0] == 0:
        employee = db.execute(
            "INSERT INTO processes (name, description, owner, status) VALUES (?, ?, ?, ?)",
            ("Employee Onboarding", "Standard process for onboarding a new employee.", "HR", "In Progress"),
        )
        db.executemany(
            "INSERT INTO workflow_steps (process_id, name, status, step_order) VALUES (?, ?, ?, ?)",
            [
                (employee.lastrowid, "Collect employee documents", "Completed", 1),
                (employee.lastrowid, "Create accounts and access", "In Progress", 2),
                (employee.lastrowid, "Team introduction", "Pending", 3),
                (employee.lastrowid, "Complete onboarding", "Pending", 4),
            ],
        )
        purchase = db.execute(
            "INSERT INTO processes (name, description, owner, status) VALUES (?, ?, ?, ?)",
            ("Purchase Request", "Process for requesting and approving a company purchase.", "Finance", "In Progress"),
        )
        db.executemany(
            "INSERT INTO workflow_steps (process_id, name, status, step_order) VALUES (?, ?, ?, ?)",
            [
                (purchase.lastrowid, "Employee submits request", "Completed", 1),
                (purchase.lastrowid, "Manager approval", "In Progress", 2),
                (purchase.lastrowid, "Finance review", "Pending", 3),
                (purchase.lastrowid, "Payment", "Pending", 4),
                (purchase.lastrowid, "Completed", "Pending", 5),
            ],
        )
    db.commit()


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped_view


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped_view(*args, **kwargs):
        if g.user["role"] != "admin":
            return "Forbidden: admin access required", 403
        return view(*args, **kwargs)
    return wrapped_view


@app.before_request
def load_logged_in_user():
    user_id = session.get("user_id")
    g.user = None if user_id is None else get_db().execute(
        "SELECT id, username, role FROM users WHERE id = ?", (user_id,)
    ).fetchone()


def get_processes():
    rows = get_db().execute("""
        SELECT p.id, p.name, p.description, p.owner, p.status, COUNT(s.id) AS step_count
        FROM processes p
        LEFT JOIN workflow_steps s ON s.process_id = p.id
        GROUP BY p.id
        ORDER BY p.id
    """).fetchall()
    return [dict(row) for row in rows]


def get_process(process_id):
    db = get_db()
    process_row = db.execute("SELECT * FROM processes WHERE id = ?", (process_id,)).fetchone()
    if process_row is None:
        return None
    step_rows = db.execute("""
        SELECT id, name, status, step_order FROM workflow_steps
        WHERE process_id = ? ORDER BY step_order
    """, (process_id,)).fetchall()
    process = dict(process_row)
    process["steps"] = [dict(row) for row in step_rows]
    return process


def update_process_status(process_id):
    db = get_db()
    statuses = [row["status"] for row in db.execute(
        "SELECT status FROM workflow_steps WHERE process_id = ?", (process_id,)
    ).fetchall()]
    if not statuses:
        new_status = "Pending"
    elif all(status == "Completed" for status in statuses):
        new_status = "Completed"
    elif any(status in ["In Progress", "Completed"] for status in statuses):
        new_status = "In Progress"
    else:
        new_status = "Pending"
    db.execute("UPDATE processes SET status = ? WHERE id = ?", (new_status, process_id))
    db.commit()


def get_completion_percentage(process):
    total = len(process["steps"])
    if total == 0:
        return 0
    return round((sum(step["status"] == "Completed" for step in process["steps"]) / total) * 100)


with app.app_context():
    init_db()


@app.route("/login", methods=["GET", "POST"])
def login():
    if g.user is not None:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        user = get_db().execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid username or password.")
        else:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(request.args.get("next") or url_for("index"))
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    return render_template("index.html", processes=get_processes())


@app.route("/processes/<int:process_id>")
@login_required
def process_detail(process_id):
    process = get_process(process_id)
    if process is None:
        return "Process not found", 404
    update_process_status(process_id)
    process = get_process(process_id)
    return render_template("process_detail.html", process=process,
                           progress=get_completion_percentage(process),
                           allowed_statuses=ALLOWED_STEP_STATUSES)


@app.route("/processes/<int:process_id>/steps/<int:step_id>/status", methods=["POST"])
@login_required
def update_step_status(process_id, step_id):
    db = get_db()
    step = db.execute(
        "SELECT id FROM workflow_steps WHERE id = ? AND process_id = ?",
        (step_id, process_id)
    ).fetchone()
    if step is None:
        return "Step not found", 404
    new_status = request.form.get("status")
    if new_status not in ALLOWED_STEP_STATUSES:
        return "Invalid status", 400
    db.execute("UPDATE workflow_steps SET status = ? WHERE id = ?", (new_status, step_id))
    db.commit()
    update_process_status(process_id)
    return redirect(url_for("process_detail", process_id=process_id))


@app.route("/processes/new", methods=["GET", "POST"])
@admin_required
def create_process():
    if request.method == "POST":
        name = request.form["name"].strip()
        description = request.form["description"].strip()
        owner = request.form["owner"].strip()
        step_names = [s.strip() for s in request.form.get("steps", "").splitlines() if s.strip()]
        db = get_db()
        process = db.execute(
            "INSERT INTO processes (name, description, owner, status) VALUES (?, ?, ?, ?)",
            (name, description, owner, "Pending")
        )
        process_id = process.lastrowid
        db.executemany(
            "INSERT INTO workflow_steps (process_id, name, status, step_order) VALUES (?, ?, ?, ?)",
            [(process_id, name, "Pending", order) for order, name in enumerate(step_names, start=1)]
        )
        db.commit()
        return redirect(url_for("index"))
    return render_template("create_process.html")


@app.route("/processes/<int:process_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_process(process_id):
    process = get_process(process_id)
    if process is None:
        return "Process not found", 404
    if request.method == "POST":
        name = request.form["name"].strip()
        description = request.form["description"].strip()
        owner = request.form["owner"].strip()
        step_names = [s.strip() for s in request.form.get("steps", "").splitlines() if s.strip()]
        db = get_db()
        db.execute(
            "UPDATE processes SET name = ?, description = ?, owner = ? WHERE id = ?",
            (name, description, owner, process_id)
        )
        existing = db.execute(
            "SELECT id FROM workflow_steps WHERE process_id = ? ORDER BY step_order",
            (process_id,)
        ).fetchall()
        for index, step_name in enumerate(step_names):
            if index < len(existing):
                db.execute(
                    "UPDATE workflow_steps SET name = ?, step_order = ? WHERE id = ?",
                    (step_name, index + 1, existing[index]["id"])
                )
            else:
                db.execute(
                    "INSERT INTO workflow_steps (process_id, name, status, step_order) VALUES (?, ?, ?, ?)",
                    (process_id, step_name, "Pending", index + 1)
                )
        for row in existing[len(step_names):]:
            db.execute("DELETE FROM workflow_steps WHERE id = ?", (row["id"],))
        db.commit()
        update_process_status(process_id)
        return redirect(url_for("process_detail", process_id=process_id))
    return render_template("edit_process.html", process=process)


@app.route("/processes/<int:process_id>/delete", methods=["POST"])
@admin_required
def delete_process(process_id):
    db = get_db()
    if db.execute("SELECT id FROM processes WHERE id = ?", (process_id,)).fetchone() is None:
        return "Process not found", 404
    db.execute("DELETE FROM processes WHERE id = ?", (process_id,))
    db.commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
