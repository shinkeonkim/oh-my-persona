import logging
from typing import List

from django.conf import settings

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)


class SlackUtil:
    @staticmethod
    def send_slack_plain_message(
        blocks: List[dict],
        channel_id: str = None,
        fallback_text: str = "Default message",
    ) -> None:
        if settings.ENVIRONMENT in ("test", "development"):
            logger.info("Slack message sending is skipped in test/development environment.")
            return
        if channel_id is None:
            channel_id = settings.SLACK_CHANNEL_ID

        slack_client = WebClient(token=settings.SLACK_BOT_TOKEN)
        try:
            slack_client.chat_postMessage(
                channel=channel_id,
                text=fallback_text,
                blocks=blocks,
            )
        except SlackApiError as e:
            logger.error("Error sending message to Slack: %s", e.response["error"])

    @staticmethod
    def create_slack_section_block(text: str) -> dict:
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": text,
            },
        }

    @staticmethod
    def create_slack_divider_block() -> dict:
        return {"type": "divider"}

    @staticmethod
    def create_slack_header_block(text: str) -> dict:
        return {
            "type": "header",
            "text": {"type": "plain_text", "text": text, "emoji": True},
        }
