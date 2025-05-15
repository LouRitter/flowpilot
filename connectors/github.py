import requests
from core.secrets import SecretsManager

def run(params: dict, context: dict = None):
    secrets = SecretsManager()
    token = secrets.get("GITHUB_TOKEN")

    if "_step_type" not in params:
        print("⚠️ Missing _step_type in GitHub step")
        return None

    step_type = params["_step_type"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    if step_type == "github.query_issues":
        repo = params["repo"]
        url = f"https://api.github.com/repos/{repo}/issues"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Failed to fetch issues: {response.status_code} {response.text}")
            return None
        issues = response.json()
        summary = "\n".join([f"- #{i['number']}: {i['title']}" for i in issues if 'pull_request' not in i])
        return summary or "No issues found."

    elif step_type == "github.comment_pr":
        repo = params["repo"]
        pr_number = params["pr_number"]
        message = params["message"]
        url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
        res = requests.post(url, headers=headers, json={"body": message})
        if res.status_code != 201:
            print(f"❌ Failed to post comment: {res.status_code} {res.text}")
            return None
        print("✅ Comment posted successfully.")
        return res.json().get("html_url")

    elif step_type == "github.label_check":
        repo = params["repo"]
        pr_number = params["pr_number"]
        label_to_check = params.get("label")
        url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/labels"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Failed to check labels: {response.status_code} {response.text}")
            return None
        labels = [label["name"] for label in response.json()]
        return label_to_check in labels

    elif step_type == "github.create_issue":
        repo = params["repo"]
        title = params["title"]
        body = params["body"]
        url = f"https://api.github.com/repos/{repo}/issues"
        res = requests.post(url, headers=headers, json={"title": title, "body": body})
        if res.status_code != 201:
            print(f"❌ Failed to create issue: {res.status_code} {res.text}")
            return None
        print("✅ Issue created successfully.")
        return res.json().get("html_url")
    elif step_type == "github.get_pr_description":
        repo = params["repo"]
        pr_number = params["pr_number"]
        url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print(f"❌ Failed to fetch PR: {res.status_code} {res.text}")
            return None
        return res.json().get("body") or "[No description provided]"
    elif step_type == "github.get_pr_diff":
        repo = params["repo"]
        pr_number = params["pr_number"]
        url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
        headers["Accept"] = "application/vnd.github.v3.diff"  # Get diff format
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print(f"❌ Failed to fetch PR diff: {res.status_code} {res.text}")
            return None
        return res.text[:8000]  # Truncate to avoid context overload
    else:
        print(f"⚠️ Unknown GitHub step: {step_type}")
        return None
