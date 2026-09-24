from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

ALLOWED_STEP_STATUSES = ["Pending", "In Progress", "Completed"]


processes = [
    {
        "id": 1,
        "name": "Employee Onboarding",
        "description": "Standard process for onboarding a new employee.",
        "owner": "HR",
        "status": "In Progress",
        "steps": [
            {"name": "Collect employee documents", "status": "Completed"},
            {"name": "Create accounts and access", "status": "In Progress"},
            {"name": "Team introduction", "status": "Pending"},
            {"name": "Complete onboarding", "status": "Pending"},
        ],
    },
    {
        "id": 2,
        "name": "Purchase Request",
        "description": "Process for requesting and approving a company purchase.",
        "owner": "Finance",
        "status": "In Progress",
        "steps": [
            {"name": "Employee submits request", "status": "Completed"},
            {"name": "Manager approval", "status": "In Progress"},
            {"name": "Finance review", "status": "Pending"},
            {"name": "Payment", "status": "Pending"},
            {"name": "Completed", "status": "Pending"},
        ],
    },
]


def update_process_status(process):
    steps = process["steps"]

    if not steps:
        process["status"] = "Pending"
        return

    statuses = [step["status"] for step in steps]

    if all(status == "Completed" for status in statuses):
        process["status"] = "Completed"
    elif any(status in ["In Progress", "Completed"] for status in statuses):
        process["status"] = "In Progress"
    else:
        process["status"] = "Pending"


def get_completion_percentage(process):
    total_steps = len(process["steps"])

    if total_steps == 0:
        return 0

    completed_steps = sum(
        step["status"] == "Completed"
        for step in process["steps"]
    )

    return round((completed_steps / total_steps) * 100)


@app.route("/")
def index():
    for process in processes:
        update_process_status(process)

    return render_template("index.html", processes=processes)


@app.route("/processes/<int:process_id>")
def process_detail(process_id):
    process = next((item for item in processes if item["id"] == process_id), None)

    if process is None:
        return "Process not found", 404

    update_process_status(process)
    progress = get_completion_percentage(process)

    return render_template(
        "process_detail.html",
        process=process,
        progress=progress,
        allowed_statuses=ALLOWED_STEP_STATUSES,
    )


@app.route(
    "/processes/<int:process_id>/steps/<int:step_index>/status",
    methods=["POST"],
)
def update_step_status(process_id, step_index):
    process = next((item for item in processes if item["id"] == process_id), None)

    if process is None:
        return "Process not found", 404

    if step_index < 0 or step_index >= len(process["steps"]):
        return "Step not found", 404

    new_status = request.form.get("status")

    if new_status not in ALLOWED_STEP_STATUSES:
        return "Invalid status", 400

    process["steps"][step_index]["status"] = new_status
    update_process_status(process)

    return redirect(url_for("process_detail", process_id=process_id))


@app.route("/processes/new", methods=["GET", "POST"])
def create_process():
    if request.method == "POST":
        step_names = [
            step.strip()
            for step in request.form.get("steps", "").splitlines()
            if step.strip()
        ]

        new_process = {
            "id": max((process["id"] for process in processes), default=0) + 1,
            "name": request.form["name"].strip(),
            "description": request.form["description"].strip(),
            "owner": request.form["owner"].strip(),
            "status": "Pending",
            "steps": [
                {"name": step, "status": "Pending"}
                for step in step_names
            ],
        }

        processes.append(new_process)
        return redirect(url_for("index"))

    return render_template("create_process.html")


if __name__ == "__main__":
    app.run(debug=True)
