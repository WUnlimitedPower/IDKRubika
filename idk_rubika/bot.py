import asyncio
from typing import List, Optional

import json
import requests
import logging

from .models import (
    Bot, Chat, BotCommand, Message, Update,
    File, Keypad,DeleteResult,detect_chat_type
)
from .enums import (
    FileTypeEnum, UpdateEndpointTypeEnum, ChatKeypadTypeEnum,
)

from .database import Database
from .metadata import Track_parsed
from .chat_data_saver import ChatDataSaver

class RubikaBot:
    def __init__(self, token: str ,temp_messages_database: bool = False,timeout: int = 30, base_url: str = "https://botapi.rubika.ir/v3/"):
        self.token = token
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout

        if temp_messages_database:
            self.database_name: str = "temp_messages"
        else:
            self.database_name: str = "messages"

        self.message_database: Database = Database(f"{self.database_name}.db")
        self.tparse: Track_parsed = Track_parsed()
        self.chat_data_saver: ChatDataSaver = ChatDataSaver()

    def _post(self, method: str, data: Optional[dict] = None, timeout: int = -1) -> dict:
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

    def _extract_message(self,chat_id,result: dict) -> Optional[Message]:
        """از پاسخ sendMessage/sendPoll/... مدل Message می‌سازه (اگه موجود باشه)"""
        data = result.get("data", {})
        msg = data.get("message")
        if isinstance(msg, dict):
            return Message(msg,chat_id,self)
        return None

    def _idk_make_metadata(self, text: str, parse_mode: str = "MARKDOWN"):
        parsed = self.tparse.parse(text, parse_mode)
        return parsed.get("text", text), parsed.get("metadata")

    def get_message(self,chat_id: str, message_id: str) -> Optional[Message]:
        data: dict = json.loads(self.message_database.get(
            "message",{"chat_id": chat_id,"message_id": message_id}
        ))['data']
        
        return Message(data,data['chat_id'],self)


    def get_me(self) -> Bot:
        return Bot(self._post("getMe").get("data", {}).get("bot", {}))

    async def get_updates(self, offset_id: str = "", limit: int = 100) -> tuple[List[Update], str]:
        result = await asyncio.to_thread(self._post, "getUpdates", {"offset_id": offset_id, "limit": limit})
        data = result.get("data", {})
        updates = [Update(u,self) for u in data.get("updates", []) if isinstance(u, dict)]
        next_offset = data.get("next_offset_id", "")
        return updates, next_offset
    
    async def send_message(
        self, chat_id: str, text: str, parse_mode: str = "MARKDOWN", **kwargs
    ) -> Optional[Message]:
        data = {"chat_id": chat_id, "text": text, **kwargs}
        parsed_text, metadata = self._idk_make_metadata(text, parse_mode=parse_mode)
        data["text"] = parsed_text
        if metadata:
            data["metadata"] = metadata
        result = await asyncio.to_thread(self._post, "sendMessage", data)
        return self._extract_message(chat_id, result)
    
    
    async def send_poll(self, chat_id: str, question: str, options: List[str], **kwargs) -> Optional[Message]:
        data = {"chat_id": chat_id, "question": question, "options": options, **kwargs}
        result = await asyncio.to_thread(self._post, "sendPoll", data)
        return self._extract_message(chat_id,result)
    
    async def send_location(self, chat_id: str, latitude: str, longitude: str, **kwargs) -> Optional[Message]:
        data = {"chat_id": chat_id, "latitude": latitude, "longitude": longitude, **kwargs}
        result = await asyncio.to_thread(self._post, "sendLocation", data)
        return self._extract_message(chat_id,result)
    
    async def send_contact(self, chat_id: str, first_name: str, last_name: str, phone_number: str, **kwargs) -> Optional[Message]:
        data = {
            "chat_id": chat_id,
            "first_name": first_name,
            "last_name": last_name,
            "phone_number": phone_number,
            **kwargs,
        }
        result = await asyncio.to_thread(self._post, "sendContact", data)
        return self._extract_message(chat_id,result)

    async def get_chat(self, chat_id: str) -> Chat:
        chat_type = detect_chat_type(chat_id)

        chat_data = None
        if self.chat_data_saver.exist(chat_id, chat_type):
            chat_data = self.chat_data_saver.get(chat_id, chat_type)

        if not chat_data:
            result = await asyncio.to_thread(self._post, "getChat", {"chat_id": chat_id})
            chat_data = result.get("data", {}).get("chat", {})
            if chat_data:
                self.chat_data_saver.set(chat_data)

        return Chat(chat_data or {})
    
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
        self, chat_id: str, message_id: str, text: str, parse_mode: str = "MARKDOWN", **kwargs
    ):
        data = {"chat_id": chat_id, "message_id": message_id, "text": text, **kwargs}
        parsed_text, metadata = self._idk_make_metadata(text, parse_mode=parse_mode)
        data["text"] = parsed_text
        if metadata:
            data["metadata"] = metadata
        return await asyncio.to_thread(self._post, "editMessageText", data)

    async def edit_message_keypad(self, chat_id: str, message_id: str, inline_keypad: Keypad, **kwargs):
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "inline_keypad": inline_keypad,
            **kwargs,
        }
        return await asyncio.to_thread(self._post, "editMessageKeypad", data)
    
    async def delete_message(self, chat_id: str, message_id: str) -> DeleteResult:
        data = {"chat_id": chat_id, "message_id": message_id}
        return DeleteResult(await asyncio.to_thread(self._post, "deleteMessage", data))

    async def set_commands(self, bot_commands: List[BotCommand]):
        data = {
            "bot_commands": [
                {"command": c.command, "description": c.description}
                for c in bot_commands
            ]
        }
        return await asyncio.to_thread(self._post, "setCommands", data)
    
    async def update_bot_endpoints(self, url: str, type: UpdateEndpointTypeEnum = UpdateEndpointTypeEnum.ReceiveUpdate):
        type_value = type.value if isinstance(type, UpdateEndpointTypeEnum) else type
        data = {"url": url, "type": type_value}
        return await asyncio.to_thread(self._post, "updateBotEndpoints", data)
    
    async def edit_chat_keypad(
        self,
        chat_id: str,
        chat_keypad_type: ChatKeypadTypeEnum = ChatKeypadTypeEnum.Remove,
        chat_keypad: Optional[Keypad] = None,
    ):
        type_value = chat_keypad_type.value if isinstance(chat_keypad_type, ChatKeypadTypeEnum) else chat_keypad_type
        data: dict = {"chat_id": chat_id, "chat_keypad_type": type_value}
        if chat_keypad is not None:
            data["chat_keypad"] = chat_keypad
        return await asyncio.to_thread(self._post, "editChatKeypad", data)

    async def get_file(self, file_id: str) -> Optional[File]:
        result = await asyncio.to_thread(self._post, "getFile", {"file_id": file_id})
        data = result.get("data", {})
        if "download_url" in data:
            # getFile فقط download_url برمی‌گردونه، نه File کامل
            # برای سازگاری، یه File با file_id می‌سازیم
            return File({"file_id": file_id})
        return None

    async def request_send_file(self, type: FileTypeEnum = FileTypeEnum.File) -> dict:
        type_value = type.value if isinstance(type, FileTypeEnum) else type
        return await asyncio.to_thread(self._post, "requestSendFile", {"type": type_value})

    async def ban_chat_member(self, chat_id: str, user_id: str):
        data = {"chat_id": chat_id, "user_id": user_id}
        return await asyncio.to_thread(self._post, "banChatMember", data)

    async def unban_chat_member(self, chat_id: str, user_id: str):
        data = {"chat_id": chat_id, "user_id": user_id}
        return await asyncio.to_thread(self._post, "unbanChatMember", data)
    
    async def _upload_file(self, file_path: str, file_type: FileTypeEnum) -> Optional[str]:
        """آپلود فایل و برگرداندن file_id"""
        req = await self.request_send_file(file_type)
        upload_url = req.get("data", {}).get("upload_url")
        if not upload_url:
            logging.error(f"requestSendFile failed: {req}")
            return None
        try:
            with open(file_path, "rb") as f:
                res = await asyncio.to_thread(
                    requests.post, upload_url, files={"file": f}, timeout=self.timeout
                )
                return res.json().get("data", {}).get("file_id")
        except Exception as e:
            logging.error(f"Upload failed: {e}")
            return None

    async def _send_file_common(
        self, chat_id: str, file_path: str, file_type: FileTypeEnum,
        caption: str = "", parse_mode: str = "MARKDOWN", **kwargs
    ) -> Optional[Message]:
        file_id = await self._upload_file(file_path, file_type)
        if not file_id:
            return None
        data = {"chat_id": chat_id, "file_id": file_id, **kwargs}
        if caption:
            parsed_caption, metadata = self._idk_make_metadata(caption, parse_mode=parse_mode)
            data["text"] = parsed_caption
            if metadata:
                data["metadata"] = metadata
        result = await asyncio.to_thread(self._post, "sendFile", data)
        return self._extract_message(chat_id, result)
    
    async def send_photo(self, chat_id: str, photo_path: str, caption: str = "", parse_mode: str = "MARKDOWN", **kwargs) -> Optional[Message]:
        return await self._send_file_common(chat_id, photo_path, FileTypeEnum.Image, caption, parse_mode=parse_mode, **kwargs)

    async def send_video(self, chat_id: str, video_path: str, caption: str = "", parse_mode: str = "MARKDOWN", **kwargs) -> Optional[Message]:
        return await self._send_file_common(chat_id, video_path, FileTypeEnum.Video, caption, parse_mode=parse_mode, **kwargs)

    async def send_voice(self, chat_id: str, voice_path: str, caption: str = "", parse_mode: str = "MARKDOWN", **kwargs) -> Optional[Message]:
        return await self._send_file_common(chat_id, voice_path, FileTypeEnum.Voice, caption, parse_mode=parse_mode, **kwargs)

    async def send_music(self, chat_id: str, music_path: str, caption: str = "", parse_mode: str = "MARKDOWN", **kwargs) -> Optional[Message]:
        return await self._send_file_common(chat_id, music_path, FileTypeEnum.Music, caption, parse_mode=parse_mode, **kwargs)

    async def send_gif(self, chat_id: str, gif_path: str, caption: str = "", parse_mode: str = "MARKDOWN", **kwargs) -> Optional[Message]:
        return await self._send_file_common(chat_id, gif_path, FileTypeEnum.Gif, caption, parse_mode=parse_mode, **kwargs)

    async def send_document(self, chat_id: str, file_path: str, caption: str = "", parse_mode: str = "MARKDOWN", **kwargs) -> Optional[Message]:
        return await self._send_file_common(chat_id, file_path, FileTypeEnum.File, caption, parse_mode=parse_mode, **kwargs)
