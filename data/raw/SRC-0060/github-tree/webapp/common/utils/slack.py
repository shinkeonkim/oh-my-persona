import logging
from typing import List

from django.conf import settings

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)

SLACK_BOT_SETTINGS_BY_CATEGOTY = settings.SLACK_BOT_SETTINGS_BY_CATEGOTY


class SlackUtil:

  @staticmethod
  def send_slack_plain_message(
    blocks: List[dict],
    category: str = "data_collect",
    fallback_text: str = "Default message",
  ) -> None:
    # if settings.ENVIRONMENT in ("test", "development"):
    # logger.info("Slack message sending is skipped in test/development environment.")
    # return
    if category not in SLACK_BOT_SETTINGS_BY_CATEGOTY:
      logger.error("Invalid Slack category: %s", category)
      return

    channel_id = SLACK_BOT_SETTINGS_BY_CATEGOTY[category]["channel_id"]
    token = SLACK_BOT_SETTINGS_BY_CATEGOTY[category]["bot_token"]

    slack_client = WebClient(token=token)
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
      "text": {
        "type": "plain_text",
        "text": text,
        "emoji": True
      },
    }
