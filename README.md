# Business Process Manager

A beginner-friendly Flask web application for tracking and organizing business processes and their workflows.

## Current features

- Dashboard with process statistics
- List of business processes
- Create a new process
- Process owner and status
- Workflow steps for each process
- Process detail page with a visual step-by-step workflow
- Add workflow steps when creating a process
- Responsive web interface

## Example workflows

### Purchase Request

Employee submits request → Manager approval → Finance review → Payment → Completed

### Employee Onboarding

Collect employee documents → Create accounts and access → Team introduction → Complete onboarding

## Tech stack

- Python
- Flask
- HTML
- CSS

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

On Windows:

```bash
.venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000`.

## Roadmap

1. ~~Add process steps and workflow management~~
2. Add workflow step status updates
3. Add edit/delete actions
4. Add SQLite database
5. Add authentication and user roles
6. Add REST API
7. Add tests
8. Deploy the application

## Project goal

This project is part of a portfolio focused on business processes, digitalization, and IT management.
