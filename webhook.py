from datetime import datetime
from enum import Enum
import requests


class ThemeColor(Enum):
    INFO_COLOR = "5bc0de"
    SUCCESS_COLOR = "5cb85c"
    ERROR_COLOR = "d9534f"


header = {"Content-Type": "application/json"}
JSON_TEMPLATE = '''{
    "@type": "MessageCard",
    "@context": "http://schema.org/extensions",
    "themeColor": "%s",
    "summary": "%s",
    "sections": [{
        "activityTitle": "%s",
        "activitySubtitle": "%s",
        "activityImage": "https://teamsnodesample.azurewebsites.net/static/img/image5.png",
        "facts": %s,
        "markdown": true
    }]
}
'''


def generate_payload(title: str, subtitle: str, facts: dict, color: ThemeColor):
    facts["Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_facts = [{'name': k, 'value': v} for k, v in facts.items()]
    return JSON_TEMPLATE % (color.value, title, title, subtitle, str(formatted_facts))


def send_webhook(url: str, title: str, subtitle: str = "", facts: dict = {},
                 color: ThemeColor = ThemeColor.INFO_COLOR):
    content = generate_payload(title, subtitle, facts, color)
    requests.post(url, data=content, headers=header)
