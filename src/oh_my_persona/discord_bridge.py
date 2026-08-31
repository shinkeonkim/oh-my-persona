from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass

from .conversations import ConversationStore

DISCORD_API = "https://discord.com/api/v10"


@dataclass
class DiscordBridge:
    store: ConversationStore
    bot_token: str | None = None
    forum_channel_id: str | None = None

    def __post_init__(self) -> None:
        self.bot_token = self.bot_token or os.environ.get("PERSONA_DISCORD_BOT_TOKEN")
        self.forum_channel_id = self.forum_channel_id or os.environ.get(
            "PERSONA_DISCORD_FORUM_CHANNEL_ID"
        )

    @property
    def configured(self) -> bool:
        return bool(self.bot_token and self.forum_channel_id)

    def mirror_exchange(
        self,
        conversation_id: str,
        visitor_message: str,
        ai_answer: str,
        origin: str | None = None,
    ) -> None:
        if not self.configured:
            return
        metadata = self.store.metadata(conversation_id)
        content = (
            f"**방문자**\n{visitor_message[:850]}\n\n"
            f"**AI 김신건**\n{ai_answer[:850]}"
        )
        thread_id = metadata.get("discord_thread_id")
        if thread_id:
            self._request("PATCH", f"/channels/{thread_id}", {"archived": False})
            self._request("POST", f"/channels/{thread_id}/messages", {"content": content})
            return
        label = (origin or metadata.get("widget_origin") or "web").replace("https://", "")
        response = self._request(
            "POST",
            f"/channels/{self.forum_channel_id}/threads",
            {
                "name": f"웹 상담 · {label[:50]} · {conversation_id[:8]}",
                "message": {"content": content},
            },
        )
        if response.get("id"):
            self.store.update_metadata(conversation_id, {"discord_thread_id": str(response["id"])})

    def accept_owner_message(self, thread_id: str, author_id: str, content: str) -> str | None:
        allowed = {
            item.strip() for item in os.environ.get("PERSONA_DISCORD_OWNER_IDS", "").split(",")
            if item.strip()
        }
        if not content.strip() or not allowed or author_id not in allowed:
            return None
        conversation_id = self.store.conversation_for_discord_thread(thread_id, active_days=30)
        if not conversation_id:
            return None
        self.store.append(conversation_id, "owner", content.strip())
        return conversation_id

    def _request(self, method: str, path: str, payload: dict) -> dict:
        request = urllib.request.Request(
            f"{DISCORD_API}{path}",
            data=json.dumps(payload, ensure_ascii=False).encode(),
            method=method,
            headers={
                "Authorization": f"Bot {self.bot_token}",
                "Content-Type": "application/json",
                "User-Agent": "oh-my-persona (https://github.com/shinkeonkim/oh-my-persona, 1)",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as error:
            body = error.read().decode(errors="replace")
            raise RuntimeError(f"Discord API {error.code}: {body[:500]}") from error


def run_worker() -> None:
    import discord

    store = ConversationStore()
    store.initialize()
    bridge = DiscordBridge(store)
    if not bridge.configured:
        raise SystemExit("Discord bot token and forum channel id are required")

    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_message(message):
        if message.author.bot or not getattr(message.channel, "parent_id", None):
            return
        if str(message.channel.parent_id) != bridge.forum_channel_id:
            return
        bridge.accept_owner_message(
            str(message.channel.id), str(message.author.id), message.content
        )

    client.run(bridge.bot_token)
