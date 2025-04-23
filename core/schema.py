from typing import Optional, List, Dict, Literal, Union
from pydantic import BaseModel, Field

class CronTrigger(BaseModel):
    type: Literal["scheduler"]
    event: Literal["cron"]
    params: dict = Field(default_factory=lambda: {"expression": "0 9 * * *"})

class GitHubTrigger(BaseModel):
    type: Literal["github"]
    event: Literal["issue_created"]
    params: dict = Field(default_factory=lambda: {"repo": "my-org/my-repo"})

class WebhookTrigger(BaseModel):
    type: Literal["webhook"]
    event: str
    params: dict = Field(default_factory=lambda: {"url": "https://example.com/webhook"})

Trigger = Union[CronTrigger, GitHubTrigger, WebhookTrigger]

from typing import Literal

class AISummarizeStep(BaseModel):
    type: Literal["ai.summarize"]
    params: dict = Field(default_factory=lambda: {"text": ""})
    class Config:
        extra = "forbid"

class EmailSendStep(BaseModel):
    type: Literal["email.send"]
    params: dict = Field(default_factory=lambda: {
        "to": "you@example.com",
        "subject": "Subject",
        "body": "Body text"
    })

class HackerNewsFetchStep(BaseModel):
    type: Literal["api.fetch_hacker_news"]
    params: dict = Field(default_factory=lambda: {
        "limit": 3
    })
class NotionCreateTaskStep(BaseModel):
    type: Literal["notion.create_task"]
    params: dict = Field(default_factory=lambda: {
        "title": "Task Title",
        "content": "Task Content"
    })

Step = Union[AISummarizeStep, EmailSendStep, HackerNewsFetchStep, NotionCreateTaskStep]

class Workflow(BaseModel):
    type: Literal["workflow"] = "workflow"
    name: str
    trigger: Trigger
    steps: List[Step] 
    version: str = "1.0"