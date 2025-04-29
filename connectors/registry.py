# connectors/registry.py

REGISTRY = {
    # === Built-in / Utility ===
    "ai.summarize": {
        "model_name": "AISummarizeStep",
        "description": "Use OpenAI to summarize text.",
        "params": {
            "text": {"required": True, "default": "Summarize this input."}
        },
        "category": "utility"
    },
    "email.send": {
        "model_name": "EmailSendStep",
        "description": "Send an email to one or more recipients.",
        "params": {
            "to": {"required": True, "default": "you@example.com"},
            "subject": {"required": True, "default": "No subject"},
            "body": {"required": True, "default": "Empty body"}
        },
        "category": "communication"
    },

    # === Triggers ===
    "scheduler.cron": {
        "model_name": "CronTrigger",
        "description": "Run the workflow on a recurring cron schedule.",
        "params": {
            "expression": {"required": True, "default": "0 9 * * *"}
        },
        "category": "trigger"
    },
    "webhook.receive": {
        "model_name": "WebhookTrigger",
        "description": "Trigger a workflow via incoming webhook.",
        "params": {},
        "category": "trigger"
    },
    "github.issue_created": {
        "model_name": "GitHubIssueCreatedTrigger",
        "description": "Trigger when a GitHub issue is created.",
        "params": {
            "repo": {"required": True, "default": "my-org/my-repo"}
        },
        "category": "trigger"
    },

    # === API Fetching ===
    "api.fetch_hacker_news": {
        "model_name": "HackerNewsFetchStep",
        "description": "Fetch top stories from Hacker News.",
        "params": {
            "limit": {"required": False, "default": 3}
        },
        "category": "api"
    },
    "api.http_get": {
        "model_name": "GenericHttpGetStep",
        "description": "Make a simple HTTP GET request.",
        "params": {
            "url": {"required": True, "default": "https://example.com"},
            "headers": {"required": False, "default": {}}
        },
        "category": "api"
    },

    # === Weather ===
    "weather.fetch_forecast": {
        "model_name": "WeatherFetchForecastStep",
        "description": "Get current or upcoming weather for a location.",
        "params": {
            "location": {"required": True, "default": "New York"},
            "unit": {"required": False, "default": "imperial"}
        },
        "category": "api"
    },

    # === Notion ===
    "notion.create_task": {
        "model_name": "NotionCreateTaskStep",
        "description": "Create a task or page in Notion.",
        "params": {
            "title": {"required": True, "default": "New Task"},
            "content": {"required": True, "default": "Task description"}
        },
        "category": "productivity"
    },
    "notion.create_page": {
        "model_name": "NotionCreatePageStep",
        "description": "Create a flexible page in Notion under a database or page.",
        "required_params": ["parent_id"],
        "category": "productivity"
    },
    "notion.append_block": {
        "model_name": "NotionAppendBlockStep",
        "description": "Append content to an existing Notion page.",
        "params": {
            "page_id": {"required": True, "default": "[MISSING_PAGE_ID]"},
            "text": {"required": True, "default": "Additional content"}
        },
        "category": "productivity"
    },

    # === GitHub Actions ===
    "github.comment_pr": {
        "model_name": "GitHubCommentPRStep",
        "description": "Add a comment to a GitHub pull request.",
        "params": {
            "pr_number": {"required": True, "default": 1},
            "message": {"required": True, "default": "Thanks for your contribution!"}
        },
        "category": "devtools"
    },
    "github.label_check": {
        "model_name": "GitHubLabelCheckStep",
        "description": "Check if a PR has a specific label.",
        "params": {
            "pr_number": {"required": True, "default": 1},
            "label": {"required": True, "default": "ready-for-review"}
        },
        "category": "devtools"
    },
    "github.create_issue": {
        "model_name": "GitHubCreateIssueStep",
        "description": "Create a new issue in a GitHub repository.",
        "params": {
            "repo": {"required": True, "default": "my-org/my-repo"},
            "title": {"required": True, "default": "Bug report"},
            "body": {"required": True, "default": "Describe the issue here."}
        },
        "category": "devtools"
    },

    # === Slack / Discord ===
    "slack.send_message": {
        "model_name": "SlackSendMessageStep",
        "description": "Send a message to a Slack channel.",
        "params": {
            "channel": {"required": True, "default": "#general"},
            "message": {"required": True, "default": "Hello from FlowPilot!"}
        },
        "category": "communication"
    },
    "discord.send_message": {
        "model_name": "DiscordSendMessageStep",
        "description": "Send a message using a Discord webhook.",
        "params": {
            "webhook_url": {"required": True, "default": "[DISCORD_WEBHOOK_URL]"},
            "content": {"required": True, "default": "Hello from FlowPilot!"}
        },
        "category": "communication"
    },

    # === Docs / Output ===
    "doc.generate_summary": {
        "model_name": "DocGenerateSummaryStep",
        "description": "Generate a report from content (markdown or HTML).",
        "params": {
            "text": {"required": True, "default": "Here's what happened today..."},
            "format": {"required": False, "default": "markdown"}
        },
        "category": "docs"
    },
    "doc.save_to_file": {
        "model_name": "DocSaveToFileStep",
        "description": "Save given content to a local file.",
        "params": {
            "filename": {"required": True, "default": "output.md"},
            "content": {"required": True, "default": "# Report\n\nNo content."}
        },
        "category": "docs"
    }
}
