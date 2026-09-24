from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

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
        "status": "Pending",
        "steps": [
            {"name": "Employee submits request", "status": "Completed"},
            {"name": "Manager approval", "status": "In Progress"},
            {"name": "Finance review", "status": "Pending"},
            {"name": "Payment", "status": "Pending"},
            {"name": "Completed", "status": "Pending"},
        ],
    },
]


@app.route("/")
def index():
    return render_template("index.html", processes=processes)


@app.route("/processes/<int:process_id>")
def process_detail(process_id):
    process = next((item for item in processes if item["id"] == process_id), None)

    if process is None:
        return "Process not found", 404

    return render_template("process_detail.html", process=process)


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
