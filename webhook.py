from datetime import datetime
import configparser
import requests
import sys

config = configparser.ConfigParser()
config.read("settings.ini")

header = {"Content-Type": "application/json"}
WEBHOOK_URL=config["DETAILS"]["base_url"]
JSON_TEMPLATE = '''{
    "@type": "MessageCard",
    "@context": "http://schema.org/extensions",
    "themeColor": "0076D7",
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


def generate_payload(title: str, subtitle: str = "", facts: dict = {}):
    facts["Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_facts = [{'name': k, 'value': v} for k, v in facts.items()]
    return JSON_TEMPLATE % (title, title, subtitle, str(formatted_facts))


def send_webhook(title: str, subtitle: str = "", facts: dict = {}):
    content = generate_payload(title, subtitle, facts)
    requests.post(WEBHOOK_URL, data=content, headers=header)


if __name__ == "__main__":
    send_webhook(sys.argv[1])