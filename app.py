from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

processes = [
    {
        "id": 1,
        "name": "Employee Onboarding",
        "description": "Standard process for onboarding a new employee.",
        "owner": "HR",
        "status": "In Progress",
    },
    {
        "id": 2,
        "name": "Purchase Request",
        "description": "Process for requesting and approving a company purchase.",
        "owner": "Finance",
        "status": "Pending",
    },
]


@app.route("/")
def index():
    return render_template("index.html", processes=processes)


@app.route("/processes/new", methods=["GET", "POST"])
def create_process():
    if request.method == "POST":
        new_process = {
            "id": len(processes) + 1,
            "name": request.form["name"].strip(),
            "description": request.form["description"].strip(),
            "owner": request.form["owner"].strip(),
            "status": "Pending",
        }
        processes.append(new_process)
        return redirect(url_for("index"))

    return render_template("create_process.html")


if __name__ == "__main__":
    app.run(debug=True)
