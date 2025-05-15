# 🧠 FlowPilot (name WIP, there's a lot of flowpilots already)

**FlowPilot** is an AI-powered, modular integration platform for building and running automation workflows. It translates natural language prompts into real, runnable, multi-step automations that connect tools like GitHub, Notion, OpenAI, Email, Weather APIs, and more.

---

## 🚀 What It Does

- Converts **natural language prompts** into structured workflows
- Supports **webhooks** and **scheduled triggers** WIP
- Uses **AI to summarize content** or generate context
- Connects to:
  - 🧊 GitHub (issues, PRs, labels, comments)
  - 📓 Notion (create pages, append content)
  - 📬 Email (send digests or alerts) WIP
  - 🌤️ Weather APIs (daily forecasts)
  - 📰 News (top stories) WIP
  - 🌐 HTTP endpoints (GET requests) WIP
- Handles all **Jinja-style templating** between steps
- Includes **parameter validation + fallback prompts**
- Modular, testable, and extensible for future APIs

---

## 🛠️ Running It Locally

### 1. Clone & install dependencies

```bash
git clone https://github.com/louritter/flowpilot
cd flowpilot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Add your secrets

Create a `.secrets.json` in the project root:

```json
{
  "OPENAI_API_KEY": "sk-...",
  "NOTION_TOKEN": "secret_...",
  "NOTION_DATABASE_ID": "...",
  "GITHUB_TOKEN": "ghp_...",
  "EMAIL_TO": "me@example.com"
}
```

### 3. Generate a workflow from a prompt

```bash
python main.py
```

_Example prompt_:
> Summarize GitHub issues and add them to a Notion page

### 4. Run the workflow

```bash
python runner.py workflows/my_workflow.json
```

---

## ✅ Currently Supported Workflow Steps

| Connector | Step Types |
|----------|-------------|
| **GitHub** | `query_issues`, `comment_pr`, `label_check`, `create_issue`, `get_pr_description`, `get_pr_diff` |
| **Notion** | `create_page`, `append_block` |
| **OpenAI** | `ai.summarize` |
| **Email** | `email.send` |
| **Weather** | `fetch_forecast` |
| **API/HTTP** | `http_get`, `fetch_hacker_news` |
| **Docs** | `save_to_file`, `generate_summary` |

---

## 📍 Project Philosophy

FlowPilot is built to be:

- **Trigger-aware**: Knows how to activate workflows via schedule, webhook, etc. WIP
- **Context-smart**: Prompts users for missing details if AI-generated workflow is incomplete
- **100% valid**: No broken workflows — ever
- **Developer-friendly**: Modular Python, schema-driven, connector-based
- **AI-native**: Prompts and workflows co-designed to use LLMs effectively

---

## 🛣️ Roadmap

### 🔧 Near-Term
- Smart webhook listener for real-time GitHub/Slack events
- Basic local persistence (per-user workflows, secrets)
- UI for managing workflows and API keys
- Better AI reasoning: suggest fixes, clarify intent, adapt prompts

### 🧠 Longer-Term
- Multi-user auth & storage (e.g. with AWS/GCP backend)
- UI builder for workflows (drag + drop steps)
- AI "copilot" mode to co-create workflows with users in real time
- Deployable SaaS / self-hostable product
- Creating connectors on its own (AKA IT'S ALIVE!!!)
---

## 🤝 Contributing

Have an idea for a new connector or step type? Want to build out a UI or storage system? PRs welcome.

---

## 🧑‍🚀 Built by @louritter

FlowPilot is an evolving personal project to showcase advanced integration engineering, AI design, and system thinking. Feedback, contributions, and ideas are welcome.