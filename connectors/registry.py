# connectors/registry.py

REGISTRY = {
    # === Utility ===
    "ai.summarize": {
        "model_name": "AISummarizeStep",
        "description": "Use OpenAI to summarize text.",
        "required_params": ["text"],
        "category": "utility"
    },

    # === Communication ===
    "email.send": {
        "model_name": "EmailSendStep",
        "description": "Send an email with subject and body.",
        "required_params": ["to", "subject", "body"],
        "category": "communication"
    },
    "slack.send_message": {
        "model_name": "SlackSendMessageStep",
        "description": "Send a message to a Slack channel.",
        "required_params": ["channel", "message"],
        "category": "communication"
    },
    "discord.send_message": {
        "model_name": "DiscordSendMessageStep",
        "description": "Send a message via a Discord webhook.",
        "required_params": ["webhook_url", "content"],
        "category": "communication"
    },

    # === Notion ===
    "notion.create_page": {
        "model_name": "NotionCreatePageStep",
        "description": "Create a flexible page in Notion under a database or page.",
        "required_params": ["parent_id", "title"],
        "category": "productivity"
    },
    "notion.append_block": {
        "model_name": "NotionAppendBlockStep",
        "description": "Append content blocks to a Notion page.",
        "required_params": ["page_id", "text"],
        "category": "productivity"
    },
    "notion.update_page": {
        "model_name": "NotionUpdatePageStep",
        "description": "Update properties of an existing Notion page.",
        "required_params": ["page_id", "properties"],
        "category": "productivity"
    },
    "notion.query_database": {
        "model_name": "NotionQueryDatabaseStep",
        "description": "Query a Notion database with filters.",
        "required_params": ["database_id"],
        "category": "productivity"
    },

    # === GitHub ===
    "github.create_issue": {
        "model_name": "GitHubCreateIssueStep",
        "description": "Create a new issue in a GitHub repository.",
        "required_params": ["repo", "title"],
        "category": "devtools"
    },
    "github.comment_issue": {
        "model_name": "GitHubCommentIssueStep",
        "description": "Add a comment to a GitHub issue.",
        "required_params": ["repo", "issue_number", "comment"],
        "category": "devtools"
    },
    "github.add_label": {
        "model_name": "GitHubAddLabelStep",
        "description": "Add a label to an existing GitHub issue.",
        "required_params": ["repo", "issue_number", "labels"],
        "category": "devtools"
    },
    "github.close_issue": {
        "model_name": "GitHubCloseIssueStep",
        "description": "Close a GitHub issue.",
        "required_params": ["repo", "issue_number"],
        "category": "devtools"
    },
    "github.create_repo": {
        "model_name": "GitHubCreateRepoStep",
        "description": "Create a new GitHub repository.",
        "required_params": ["name"],
        "category": "devtools"
    },
    "github.query_issues": {
        "model_name": "GitHubQueryIssuesStep",
        "description": "Query open issues from a GitHub repository.",
        "required_params": ["repo"],
        "category": "devtools"
    },

    # === Weather ===
    "weather.fetch_forecast": {
        "model_name": "WeatherFetchForecastStep",
        "description": "Get the current weather forecast for a location.",
        "required_params": ["location"],
        "category": "api"
    },

    # === Scheduler Triggers ===
    "scheduler.cron": {
        "model_name": "CronTrigger",
        "description": "Run the workflow on a recurring cron schedule.",
        "required_params": ["expression"],
        "category": "trigger"
    },

    "webhook.receive": {
        "model_name": "WebhookTrigger",
        "description": "Trigger a workflow via incoming webhook.",
        "required_params": [],
        "category": "trigger"
    }
}
