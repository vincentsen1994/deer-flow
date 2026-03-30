"""DingTalk channel - connects to DingTalk via Webhook."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import aiohttp

from app.channels.base import Channel
from app.channels.message_bus import InboundMessageType, MessageBus, OutboundMessage, ResolvedAttachment

logger = logging.getLogger(__name__)


class DingTalkChannel(Channel):
    """DingTalk IM channel using Webhook API.

    Configuration keys (in ``config.yaml`` under ``channels.dingtalk``):
        - ``webhook_url``: DingTalk robot webhook URL.
        - ``secret`` : (optional) DingTalk robot secret for signature.
        - ``at_all`` : (optional) Whether to @all when sending messages, default false.

    The channel uses HTTP POST to send messages to DingTalk webhook.

    Message flow:
        1. User sends a message in DingTalk group
        2. DingTalk robot receives the message via webhook
        3. Bot processes the message and returns a result
        4. Bot replies to the group via webhook
    """

    def __init__(self, bus: MessageBus, config: dict[str, Any]) -> None:
        super().__init__(name="dingtalk", bus=bus, config=config)
        self.webhook_url = self.config.get("webhook_url", "")
        self.secret = self.config.get("secret", "")
        self.at_all = self.config.get("at_all", False)
        self._session: aiohttp.ClientSession | None = None

    async def start(self) -> None:
        """Start the DingTalk channel."""
        if self._running:
            return

        if not self.webhook_url:
            logger.error("DingTalk channel requires webhook_url")
            return

        self._session = aiohttp.ClientSession()
        self._running = True
        logger.info("DingTalk channel started")

    async def stop(self) -> None:
        """Stop the DingTalk channel."""
        if not self._running:
            return

        self._running = False
        if self._session:
            await self._session.close()
        logger.info("DingTalk channel stopped")

    async def send(self, msg: OutboundMessage) -> None:
        """Send a message to DingTalk via webhook."""
        if not self._session:
            logger.error("DingTalk channel not started")
            return

        # Prepare DingTalk message format
        dingtalk_msg = {
            "msgtype": "text",
            "text": {
                "content": msg.text
            }
        }

        # Add @all if configured
        if self.at_all:
            dingtalk_msg["at"] = {
                "isAtAll": True
            }

        try:
            async with self._session.post(
                self.webhook_url,
                json=dingtalk_msg,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    logger.error("Failed to send message to DingTalk: %s", await response.text())
                else:
                    result = await response.json()
                    if result.get("errcode") != 0:
                        logger.error("DingTalk API error: %s", result.get("errmsg"))
        except Exception as e:
            logger.exception("Error sending message to DingTalk: %s", e)

    async def send_file(self, msg: OutboundMessage, attachment: ResolvedAttachment) -> bool:
        """DingTalk webhook does not support file uploads directly."""
        logger.warning("DingTalk webhook does not support file uploads")
        return False

    async def handle_webhook(self, data: dict[str, Any]) -> dict[str, Any]:
        """Handle incoming webhook from DingTalk.

        This method should be called by the webhook endpoint when DingTalk
        sends a message to the robot.

        Args:
            data: The webhook payload from DingTalk

        Returns:
            Response dict to send back to DingTalk
        """
        try:
            # Parse DingTalk message
            if "text" not in data:
                logger.warning("Invalid DingTalk webhook payload: %s", data)
                return {"errcode": 400, "errmsg": "Invalid payload"}

            # Get message content
            text_content = data["text"]["content"]
            
            # Get sender info
            sender_id = data.get("senderId", "unknown")
            sender_nick = data.get("senderNick", "unknown")
            
            # Create conversation ID (use conversationId if available, otherwise use sender)
            chat_id = data.get("conversationId", sender_id)
            
            # Skip messages from robots (prevent loops)
            if data.get("robot"):
                logger.info("Skipping message from robot")
                return {"errcode": 0, "errmsg": "OK"}

            # Create inbound message
            inbound_msg = self._make_inbound(
                chat_id=chat_id,
                user_id=sender_id,
                text=text_content,
                msg_type=InboundMessageType.CHAT,
                metadata={
                    "sender_nick": sender_nick,
                    "conversation_type": data.get("conversationType", "group")
                }
            )

            # Publish to message bus
            await self.bus.publish_inbound(inbound_msg)

            return {"errcode": 0, "errmsg": "OK"}
        except Exception as e:
            logger.exception("Error handling DingTalk webhook: %s", e)
            return {"errcode": 500, "errmsg": "Internal error"}
