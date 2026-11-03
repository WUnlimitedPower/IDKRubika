import asyncio
from typing import List, Optional

import requests

from .models import Bot


class RubikaBot:
    def __init__(self, token: str, base_url: str = "https://botapi.rubika.ir/v3/"):
        self.token = token
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = 30

    def _post(self, method: str, data: dict = None, timeout: int = -1) -> dict:
        if timeout < 0:
            timeout = self.timeout

        response = requests.post(
            url=f"{self.base_url}{self.token}/{method}",
            headers={"Content-Type": "application/json"},
            json=data if data is not None else {},
            timeout=timeout,
        )
        response.raise_for_status()

        result = response.json()
        if not isinstance(result, dict):
            raise ValueError(f"Invalid response from Rubika API for {method}: expected a JSON object")
        return result

    def get_me(self) -> Bot:
        return Bot(self._post("getMe").get("data", {}).get("bot", {}))

    def get_updates(self, offset_id: str = "", limit: int = 100) -> dict:
        return self._post("getUpdates", {"offset_id": offset_id, "limit": limit})

    async def send_message(self, chat_id: str, text: str, **kwargs):
        data = {"chat_id": chat_id, "text": text, **kwargs}
        return await asyncio.to_thread(self._post, "sendMessage", data)

    async def send_poll(self, chat_id: str, question: str, options: List[str], **kwargs):
        data = {"chat_id": chat_id, "question": question, "options": options, **kwargs}
        return await asyncio.to_thread(self._post, "sendPoll", data)

    async def send_location(self, chat_id: str, latitude: str, longitude: str, **kwargs):
        data = {"chat_id": chat_id, "latitude": latitude, "longitude": longitude, **kwargs}
        return await asyncio.to_thread(self._post, "sendLocation", data)

    async def send_contact(
        self,
        chat_id: str,
        first_name: str,
        last_name: str,
        phone_number: str,
        **kwargs,
    ):
        data = {
            "chat_id": chat_id,
            "first_name": first_name,
            "last_name": last_name,
            "phone_number": phone_number,
            **kwargs,
        }
        return await asyncio.to_thread(self._post, "sendContact", data)

    async def get_chat(self, chat_id: str):
        return await asyncio.to_thread(self._post, "getChat", {"chat_id": chat_id})

    async def forward_message(
        self, from_chat_id: str, message_id: str, to_chat_id: str, **kwargs
    ):
        data = {
            "from_chat_id": from_chat_id,
            "message_id": message_id,
            "to_chat_id": to_chat_id,
            **kwargs,
        }
        return await asyncio.to_thread(self._post, "forwardMessage", data)

    async def edit_message_text(
        self, chat_id: str, message_id: str, text: str, **kwargs
    ):
        data = {"chat_id": chat_id, "message_id": message_id, "text": text, **kwargs}
        return await asyncio.to_thread(self._post, "editMessageText", data)

    async def edit_message_keypad(
        self, chat_id: str, message_id: str, inline_keypad: dict, **kwargs
    ):
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "inline_keypad": inline_keypad,
            **kwargs,
        }
        return await asyncio.to_thread(self._post, "editMessageKeypad", data)

    async def delete_message(self, chat_id: str, message_id: str):
        data = {"chat_id": chat_id, "message_id": message_id}
        return await asyncio.to_thread(self._post, "deleteMessage", data)

    async def set_commands(self, bot_commands: List[dict]):
        return await asyncio.to_thread(self._post, "setCommands", {"bot_commands": bot_commands})

    async def update_bot_endpoints(self, url: str, type: str = "ReceiveUpdate"):
        data = {"url": url, "type": type}
        return await asyncio.to_thread(self._post, "updateBotEndpoints", data)

    async def edit_chat_keypad(
        self,
        chat_id: str,
        chat_keypad_type: str = "Remove",
        chat_keypad: Optional[dict] = None,
    ):
        data = {"chat_id": chat_id, "chat_keypad_type": chat_keypad_type}
        if chat_keypad is not None:
            data["chat_keypad"] = chat_keypad
        return await asyncio.to_thread(self._post, "editChatKeypad", data)

    async def get_file(self, file_id: str):
        return await asyncio.to_thread(self._post, "getFile", {"file_id": file_id})

    async def send_file(self, chat_id: str, file_id: str, **kwargs):
        data = {"chat_id": chat_id, "file_id": file_id, **kwargs}
        return await asyncio.to_thread(self._post, "sendFile", data)

    async def request_send_file(self, type: str = "File"):
        return await asyncio.to_thread(self._post, "requestSendFile", {"type": type})

    async def ban_chat_member(self, chat_id: str, user_id: str):
        data = {"chat_id": chat_id, "user_id": user_id}
        return await asyncio.to_thread(self._post, "banChatMember", data)

    async def unban_chat_member(self, chat_id: str, user_id: str):
        data = {"chat_id": chat_id, "user_id": user_id}
        return await asyncio.to_thread(self._post, "unbanChatMember", data)
