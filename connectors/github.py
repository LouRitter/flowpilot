# connectors/github.py

import requests
from core.secrets import SecretsManager

def github_api_request(method: str, endpoint: str, token: str, json=None):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    url = f"https://api.github.com{endpoint}"
    response = requests.request(method, url, headers=headers, json=json)
    return response

def run(params: dict, context: dict = None):
    secrets = SecretsManager()
    token = secrets.get("GITHUB_TOKEN")
    step_type = params.get("_step_type")  # Injected by runner or dispatcher

    if step_type == "github.create_issue":
        return create_issue(params, token)
    elif step_type == "github.comment_issue":
        return comment_issue(params, token)
    elif step_type == "github.add_label":
        return add_label(params, token)
    elif step_type == "github.close_issue":
        return close_issue(params, token)
    elif step_type == "github.create_repo":
        return create_repo(params, token)
    elif "github.query_issues":
        return query_issues(params, token)
    else:
        raise ValueError(f"Unsupported GitHub step type: {step_type}")

def create_issue(params, token):
    repo = params["repo"]
    title = params["title"]
    body = params.get("body", "")
    labels = params.get("labels", [])
    assignees = params.get("assignees", [])

    payload = {
        "title": title,
        "body": body,
        "labels": labels,
        "assignees": assignees
    }
    res = github_api_request("POST", f"/repos/{repo}/issues", token, json=payload)
    if res.status_code != 201:
        raise Exception(f"Failed to create issue: {res.text}")
    print("✅ GitHub issue created")
    return res.json().get("html_url")

def comment_issue(params, token):
    repo = params["repo"]
    issue_number = params["issue_number"]
    comment = params["comment"]

    payload = {"body": comment}
    res = github_api_request("POST", f"/repos/{repo}/issues/{issue_number}/comments", token, json=payload)
    if res.status_code != 201:
        raise Exception(f"Failed to comment on issue: {res.text}")
    print("✅ Comment added to issue")
    return res.json().get("html_url")

def add_label(params, token):
    repo = params["repo"]
    issue_number = params["issue_number"]
    labels = params["labels"]  # List

    payload = {"labels": labels}
    res = github_api_request("POST", f"/repos/{repo}/issues/{issue_number}/labels", token, json=payload)
    if res.status_code != 200:
        raise Exception(f"Failed to add labels: {res.text}")
    print("✅ Labels added")
    return labels

def close_issue(params, token):
    repo = params["repo"]
    issue_number = params["issue_number"]

    payload = {"state": "closed"}
    res = github_api_request("PATCH", f"/repos/{repo}/issues/{issue_number}", token, json=payload)
    if res.status_code != 200:
        raise Exception(f"Failed to close issue: {res.text}")
    print("✅ Issue closed")
    return res.json().get("html_url")

def create_repo(params, token):
    name = params["name"]
    private = params.get("private", True)
    description = params.get("description", "")

    payload = {
        "name": name,
        "private": private,
        "description": description
    }
    res = github_api_request("POST", "/user/repos", token, json=payload)
    if res.status_code != 201:
        raise Exception(f"Failed to create repo: {res.text}")
    print("✅ Repository created")
    return res.json().get("html_url")

def query_issues(params, token):
    repo = params["repo"]
    state = params.get("state", "open")
    per_page = params.get("per_page", 5)

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    url = f"https://api.github.com/repos/{repo}/issues"
    response = requests.get(url, headers=headers, params={
        "state": state,
        "per_page": per_page
    })

    response.raise_for_status()
    issues = response.json()

    if not issues:
        return "No issues found."

    summary_lines = [f"- #{i['number']}: {i['title']}" for i in issues if "pull_request" not in i]
    return "\\n".join(summary_lines)
