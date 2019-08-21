import json
import os

import requests

webhook_url = os.environ['SLACK_WEBHOOK_URL']

data = dict(
    channel='#niels-test',
    username="afvalcontainers-bot",
    blocks=[{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "This is a mrkdwn section block :ghost: *this is bold*, and ~this is crossed out~, and <https://google.com|this is a link>"
        }
    }, {
        "type": "divider"
    }, {
        "type": "section",
        "text": {
            "type": "plain_text",
            "text": "This is a plain text section block.",
            "emoji": True
        }
    }]
)
response = requests.post(
    webhook_url,
    data=json.dumps(data),
    headers={'Content-Type': 'application/json'}
)

if response.status_code != 200:
    raise ValueError(
        'Request to slack returned an error %s, the response is:\n%s' %
        (response.status_code, response.text)
    )
