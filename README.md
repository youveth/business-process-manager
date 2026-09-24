# Business Process Manager

A Flask web application for tracking and organizing business processes and their workflows.

This project is designed as a portfolio project around **business processes, digitalization, and IT management**.

## Live Demo

The application is deployed online with Render.

## Features

- Dashboard with process statistics
- Business process management
- Create, edit, and delete processes
- Process owner and status management
- Workflow steps
- Workflow step status updates
- Automatic process status updates
- Workflow completion percentage
- Authentication and user roles
- Admin/User permissions
- REST API
- SQLite database
- Automated tests with pytest
- GitHub Actions CI
- Production deployment with Gunicorn

## Example Workflows

### Purchase Request

Employee submits request → Manager approval → Finance review → Payment → Completed

### Employee Onboarding

Collect employee documents → Create accounts and access → Team introduction → Complete onboarding

## REST API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /api/processes | List processes |
| GET | /api/processes/<id> | Get one process |
| POST | /api/processes | Create a process |
| PUT | /api/processes/<id> | Update a process |
| DELETE | /api/processes/<id> | Delete a process |
| PATCH | /api/processes/<id>/steps/<step_id>/status | Update step status |

API access follows the application's authentication and role permissions.

## Testing

Automated tests are located in:

`tests/test_app.py`

Run them with:

```bash
pytest -q
```

GitHub Actions automatically runs the test suite for pushes and pull requests to `main`.

## Tech Stack

- Python
- Flask
- SQLite
- HTML
- CSS
- pytest
- Gunicorn
- GitHub Actions
- Render

## Run Locally

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\\Scripts\\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python app.py
```

Then open:

`http://127.0.0.1:5000`

The SQLite database is created automatically in:

`instance/business_process_manager.db`

## Project Structure

```text
business-process-manager/
├── app.py
├── requirements.txt
├── README.md
├── tests/
│   └── test_app.py
├── templates/
├── static/
├── instance/
└── .github/
    └── workflows/
        └── tests.yml
```

## Roadmap

- [x] Process and workflow management
- [x] Workflow status updates
- [x] SQLite persistence
- [x] Edit/delete actions
- [x] Authentication and user roles
- [x] REST API
- [x] Automated tests
- [x] GitHub Actions CI
- [x] Deployment
- [ ] Production security improvements
- [ ] PostgreSQL database
- [ ] Improved API documentation
- [ ] Dashboard analytics

## Portfolio Goal

This project demonstrates practical skills in:

- Business process management
- Digitalization
- CRUD application development
- Authentication and authorization
- REST API design
- Database management
- Automated testing
- CI/CD basics
- Cloud deployment

It is part of a portfolio focused on **Business IT, Digitalization, Information Systems, and IT Management**.
