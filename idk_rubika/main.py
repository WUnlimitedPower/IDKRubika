import requests
import asyncio
import logging
from typing import Optional, List, Callable, Awaitable, Any, Dict
from enum import Enum
from dataclasses import dataclass, field


# ==========================================
# بخش ۱: Enum ها و مدل های پایه
# ==========================================

class UpdateTypeEnum(str, Enum):
    UpdatedMessage = "UpdatedMessage"
    NewMessage = "NewMessage"
    RemovedMessage = "RemovedMessage"
    StartedBot = "StartedBot"
    StoppedBot = "StoppedBot"
    EventData = "EventData"


class EventTypeEnum(str, Enum):
    BotJoined = "BotJoined"
    BotRemoved = "BotRemoved"
    BotPermissionsChanged = "BotPermissionsChanged"


class EventJoinTypeEnum(str, Enum):
    Member = "Member"
    Admin = "Admin"


class EnumChatAccess(str, Enum):
    SendMessages = "SendMessages"
    EditMyMessages = "EditMyMessages"
    EditAllMessages = "EditAllMessages"
    DeleteGlobalAllMessages = "DeleteGlobalAllMessages"
    ViewMembers = "ViewMembers"
    BanMember = "BanMember"


class ButtonTypeEnum(str, Enum):
    Simple = "Simple"
    Selection = "Selection"
    Calendar = "Calendar"
    NumberPicker = "NumberPicker"
    StringPicker = "StringPicker"
    Location = "Location"
    CameraImage = "CameraImage"
    CameraVideo = "CameraVideo"
    GalleryImage = "GalleryImage"
    GalleryVideo = "GalleryVideo"
    File = "File"
    Audio = "Audio"
    RecordAudio = "RecordAudio"
    Textbox = "Textbox"
    Link = "Link"
    AskMyPhoneNumber = "AskMyPhoneNumber"
    AskMyLocation = "AskMyLocation"
    Barcode = "Barcode"


class ButtonSelectionTypeEnum(str, Enum):
    TextOnly = "TextOnly"
    TextImgThu = "TextImgThu"
    TextImgBig = "TextImgBig"


class ButtonSelectionSearchEnum(str, Enum):
    None_ = "None"
    Local = "Local"
    Api = "Api"


class ButtonSelectionGetEnum(str, Enum):
    Local = "Local"
    Api = "Api"


class ButtonCalendarTypeEnum(str, Enum):
    DatePersian = "DatePersian"
    DateGregorian = "DateGregorian"


class ButtonTextboxTypeKeypadEnum(str, Enum):
    String = "String"
    Number = "Number"


class ButtonTextboxTypeLineEnum(str, Enum):
    SingleLine = "SingleLine"
    MultiLine = "MultiLine"


class ButtonLocationTypeEnum(str, Enum):
    Picker = "Picker"
    View = "View"


class ChatKeypadTypeEnum(str, Enum):
    None_ = "None"
    New = "New"
    Remove = "Remove"


class MetadataTypeEnum(str, Enum):
    Bold = "Bold"
    Italic = "Italic"
    Mono = "Mono"
    Underline = "Underline"
    Strike = "Strike"
    Spoiler = "Spoiler"
    Link = "Link"
    MentionText = "MentionText"
    Pre = "Pre"
    Quote = "Quote"


# ==========================================
# بخش ۲: مدل های داده (مطابق با مستندات)
# ==========================================

class File:
    def __init__(self, data: dict):
        self.file_id: str = data.get("file_id", "")
        self.file_name: str = data.get("file_name", "")
        self.size: str = data.get("size", "")


class Location:
    def __init__(self, data: dict):
        self.longitude: str = data.get("longitude", "")
        self.latitude: str = data.get("latitude", "")


class AuxData:
    def __init__(self, data: dict):
        self.start_id: str = data.get("start_id", "")
        self.button_id: str = data.get("button_id", "")


class ForwardedFrom:
    def __init__(self, data: dict):
        self.type_from: str = data.get("type_from", "")
        self.message_id: str = data.get("message_id", "")
        self.from_chat_id: str = data.get("from_chat_id", "")
        self.from_sender_id: str = data.get("from_sender_id", "")


class ContactMessage:
    def __init__(self, data: dict):
        self.phone_number: str = data.get("phone_number", "")
        self.first_name: str = data.get("first_name", "")
        self.last_name: str = data.get("last_name", "")


class PollStatus:
    def __init__(self, data: dict):
        self.state: str = data.get("state", "")
        self.selection_index: int = data.get("selection_index", -1)
        self.percent_vote_options: List[int] = data.get("percent_vote_options", [])
        self.total_vote: int = data.get("total_vote", 0)
        self.show_total_votes: bool = data.get("show_total_votes", False)


class Poll:
    def __init__(self, data: dict):
        self.question: str = data.get("question", "")
        self.options: List[str] = data.get("options", [])
        ps = data.get("poll_status")
        self.poll_status: Optional[PollStatus] = PollStatus(ps) if isinstance(ps, dict) else ps


class Sticker:
    def __init__(self, data: dict):
        self.sticker_id: str = data.get("sticker_id", "")
        f = data.get("file")
        self.file: Optional[File] = File(f) if isinstance(f, dict) else f
        self.emoji_character: str = data.get("emoji_character", "")


class Bot:
    def __init__(self, data: dict):
        self.bot_id: str = data.get("bot_id", "")
        self.bot_title: str = data.get("bot_title", "")
        av = data.get("avatar")
        self.avatar: Optional[File] = File(av) if isinstance(av, dict) else av
        self.description: str = data.get("description", "")
        self.username: str = data.get("username", "")
        self.start_message: str = data.get("start_message", "")
        self.share_url: str = data.get("share_url", "")


class Message:
    def __init__(self, data: dict):
        self.message_id: str = data.get("message_id", "")
        self.text: str = data.get("text", "")
        self.time: int = data.get("time", 0)
        self.is_edited: bool = data.get("is_edited", False)
        self.sender_type: str = data.get("sender_type", "")
        self.sender_id: str = data.get("sender_id", "")
        
        aux = data.get("aux_data")
        self.aux_data: Optional[AuxData] = AuxData(aux) if isinstance(aux, dict) else aux
        
        f = data.get("file")
        self.file: Optional[File] = File(f) if isinstance(f, dict) else f
        
        self.reply_to_message_id: str = data.get("reply_to_message_id", "")
        
        ff = data.get("forwarded_from")
        self.forwarded_from: Optional[ForwardedFrom] = ForwardedFrom(ff) if isinstance(ff, dict) else ff
        
        self.forwarded_no_link: str = data.get("forwarded_no_link", "")
        
        loc = data.get("location")
        self.location: Optional[Location] = Location(loc) if isinstance(loc, dict) else loc
        
        st = data.get("sticker")
        self.sticker: Optional[Sticker] = Sticker(st) if isinstance(st, dict) else st
        
        cm = data.get("contact_message")
        self.contact_message: Optional[ContactMessage] = ContactMessage(cm) if isinstance(cm, dict) else cm
        
        pl = data.get("poll")
        self.poll: Optional[Poll] = Poll(pl) if isinstance(pl, dict) else pl


class Event:
    def __init__(self, data: dict):
        rt = data.get("type")
        self.type: Optional[EventTypeEnum] = None
        if isinstance(rt, EventTypeEnum):
            self.type = rt
        elif isinstance(rt, str):
            try:
                self.type = EventTypeEnum(rt)
            except ValueError:
                pass
        
        ra = data.get("access_list")
        self.access_list: Optional[List[EnumChatAccess]] = None
        if isinstance(ra, list):
            self.access_list = []
            for item in ra:
                if isinstance(item, EnumChatAccess):
                    self.access_list.append(item)
                elif isinstance(item, str):
                    try:
                        self.access_list.append(EnumChatAccess(item))
                    except ValueError:
                        pass
        
        rj = data.get("join_type")
        self.join_type: Optional[EventJoinTypeEnum] = None
        if isinstance(rj, EventJoinTypeEnum):
            self.join_type = rj
        elif isinstance(rj, str):
            try:
                self.join_type = EventJoinTypeEnum(rj)
            except ValueError:
                pass


class Update:
    def __init__(self, data: dict):
        rt = data.get("type")
        self.type: Optional[UpdateTypeEnum] = None
        if isinstance(rt, UpdateTypeEnum):
            self.type = rt
        elif isinstance(rt, str):
            try:
                self.type = UpdateTypeEnum(rt)
            except ValueError:
                pass
        
        self.chat_id: str = data.get("chat_id", "")
        self.removed_message_id: Optional[str] = data.get("removed_message_id")
        
        nm = data.get("new_message")
        self.new_message: Optional[Message] = Message(nm) if isinstance(nm, dict) else nm
        
        um = data.get("updated_message")
        self.updated_message: Optional[Message] = Message(um) if isinstance(um, dict) else um
        
        ed = data.get("event_data")
        self.event_data: Optional[Event] = Event(ed) if isinstance(ed, dict) else ed


# --- مدل های دکمه و کیپد ---

class ButtonSelectionItem:
    def __init__(self, data: dict):
        self.text: str = data.get("text", "")
        self.image_url: str = data.get("image_url", "")
        rt = data.get("type")
        if isinstance(rt, str):
            try:
                self.type = ButtonSelectionTypeEnum(rt)
            except ValueError:
                self.type = None
        else:
            self.type = rt


class ButtonSelection:
    def __init__(self, data: dict):
        self.selection_id: str = data.get("selection_id", "")
        rs = data.get("search_type")
        self.search_type = None
        if isinstance(rs, str):
            try:
                self.search_type = ButtonSelectionSearchEnum(rs)
            except ValueError:
                pass
        elif isinstance(rs, ButtonSelectionSearchEnum):
            self.search_type = rs
            
        rg = data.get("get_type")
        self.get_type = None
        if isinstance(rg, str):
            try:
                self.get_type = ButtonSelectionGetEnum(rg)
            except ValueError:
                pass
        elif isinstance(rg, ButtonSelectionGetEnum):
            self.get_type = rg
            
        self.items: List[ButtonSelectionItem] = [
            ButtonSelectionItem(i) for i in data.get("items", []) if isinstance(i, dict)
        ]
        self.is_multi_selection: bool = data.get("is_multi_selection", False)
        self.columns_count: str = data.get("columns_count", "")
        self.title: str = data.get("title", "")


class ButtonCalendar:
    def __init__(self, data: dict):
        self.default_value: Optional[str] = data.get("default_value")
        rt = data.get("type")
        self.type = None
        if isinstance(rt, str):
            try:
                self.type = ButtonCalendarTypeEnum(rt)
            except ValueError:
                pass
        elif isinstance(rt, ButtonCalendarTypeEnum):
            self.type = rt
        self.min_year: str = data.get("min_year", "")
        self.max_year: str = data.get("max_year", "")
        self.title: str = data.get("title", "")


class ButtonNumberPicker:
    def __init__(self, data: dict):
        self.min_value: str = data.get("min_value", "")
        self.max_value: str = data.get("max_value", "")
        self.default_value: Optional[str] = data.get("default_value")
        self.title: str = data.get("title", "")


class ButtonStringPicker:
    def __init__(self, data: dict):
        self.items: List[str] = data.get("items", [])
        self.default_value: Optional[str] = data.get("default_value")
        self.title: Optional[str] = data.get("title")


class ButtonTextbox:
    def __init__(self, data: dict):
        rl = data.get("type_line")
        self.type_line = None
        if isinstance(rl, str):
            try:
                self.type_line = ButtonTextboxTypeLineEnum(rl)
            except ValueError:
                pass
        elif isinstance(rl, ButtonTextboxTypeLineEnum):
            self.type_line = rl
            
        rk = data.get("type_keypad")
        self.type_keypad = None
        if isinstance(rk, str):
            try:
                self.type_keypad = ButtonTextboxTypeKeypadEnum(rk)
            except ValueError:
                pass
        elif isinstance(rk, ButtonTextboxTypeKeypadEnum):
            self.type_keypad = rk
            
        self.place_holder: Optional[str] = data.get("place_holder")
        self.title: Optional[str] = data.get("title")
        self.default_value: Optional[str] = data.get("default_value")


class ButtonLocation:
    def __init__(self, data: dict):
        dp = data.get("default_pointer_location")
        self.default_pointer_location = Location(dp) if isinstance(dp, dict) else dp
        dm = data.get("default_map_location")
        self.default_map_location = Location(dm) if isinstance(dm, dict) else dm
        rt = data.get("type")
        self.type = None
        if isinstance(rt, str):
            try:
                self.type = ButtonLocationTypeEnum(rt)
            except ValueError:
                pass
        elif isinstance(rt, ButtonLocationTypeEnum):
            self.type = rt
        self.title: Optional[str] = data.get("title")


class Button:
    def __init__(self, data: dict):
        self.id: str = data.get("id", "")
        rt = data.get("type")
        self.type = None
        if isinstance(rt, str):
            try:
                self.type = ButtonTypeEnum(rt)
            except ValueError:
                pass
        elif isinstance(rt, ButtonTypeEnum):
            self.type = rt
        self.button_text: str = data.get("button_text", "")
        
        sel = data.get("button_selection")
        self.button_selection = ButtonSelection(sel) if isinstance(sel, dict) else sel
        cal = data.get("button_calendar")
        self.button_calendar = ButtonCalendar(cal) if isinstance(cal, dict) else cal
        np = data.get("button_number_picker")
        self.button_number_picker = ButtonNumberPicker(np) if isinstance(np, dict) else np
        sp = data.get("button_string_picker")
        self.button_string_picker = ButtonStringPicker(sp) if isinstance(sp, dict) else sp
        loc = data.get("button_location")
        self.button_location = ButtonLocation(loc) if isinstance(loc, dict) else loc
        tb = data.get("button_textbox")
        self.button_textbox = ButtonTextbox(tb) if isinstance(tb, dict) else tb


class KeypadRow:
    def __init__(self, data: dict):
        self.buttons: List[Button] = [
            Button(b) for b in data.get("buttons", []) if isinstance(b, dict)
        ]


class Keypad:
    def __init__(self, data: dict):
        self.rows: List[KeypadRow] = [
            KeypadRow(r) for r in data.get("rows", []) if isinstance(r, dict)
        ]
        self.resize_keyboard: bool = data.get("resize_keyboard", False)
        self.one_time_keyboard: bool = data.get("one_time_keyboard", False)


class MetadataPart:
    def __init__(self, data: dict):
        rt = data.get("type")
        self.type = None
        if isinstance(rt, str):
            try:
                self.type = MetadataTypeEnum(rt)
            except ValueError:
                pass
        elif isinstance(rt, MetadataTypeEnum):
            self.type = rt
        self.from_index: int = data.get("from_index", 0)
        self.length: int = data.get("length", 0)
        self.link_url: str = data.get("link_url", "")
        self.mention_text_user_id: str = data.get("mention_text_user_id", "")


class Metadata:
    def __init__(self, data: dict):
        self.meta_data_parts: List[MetadataPart] = [
            MetadataPart(p) for p in data.get("meta_data_parts", []) if isinstance(p, dict)
        ]


# ==========================================
# بخش ۳: زیرساخت Handler و Filter (به سبک PTB)
# ==========================================

class CallbackContext:
    def __init__(self, bot: "RubikaBot", update: Update):
        self.bot = bot
        self.update = update
        self.user_data: Dict[str, Any] = {}
        self.chat_data: Dict[str, Any] = {}


class BaseFilter:
    def __call__(self, update: Update) -> bool:
        raise NotImplementedError

    def __and__(self, other: "BaseFilter") -> "BaseFilter":
        return AndFilter(self, other)

    def __or__(self, other: "BaseFilter") -> "BaseFilter":
        return OrFilter(self, other)

    def __invert__(self) -> "BaseFilter":
        return InvertFilter(self)


class AndFilter(BaseFilter):
    def __init__(self, f1, f2):
        self.f1, self.f2 = f1, f2
    def __call__(self, update):
        return self.f1(update) and self.f2(update)


class OrFilter(BaseFilter):
    def __init__(self, f1, f2):
        self.f1, self.f2 = f1, f2
    def __call__(self, update):
        return self.f1(update) or self.f2(update)


class InvertFilter(BaseFilter):
    def __init__(self, f):
        self.f = f
    def __call__(self, update):
        return not self.f(update)


class filters:
    class _Text(BaseFilter):
        def __call__(self, update: Update) -> bool:
            return update.new_message is not None and bool(update.new_message.text)
    text = _Text()

    class _NewMessage(BaseFilter):
        def __call__(self, update: Update) -> bool:
            return update.type == UpdateTypeEnum.NewMessage
    new_message = _NewMessage()

    class _Command(BaseFilter):
        def __init__(self, commands):
            if isinstance(commands, str):
                commands = [commands]
            self.commands = [c if c.startswith('/') else f'/{c}' for c in commands]
        def __call__(self, update: Update) -> bool:
            if not update.new_message or not update.new_message.text:
                return False
            text = update.new_message.text.strip()
            return any(text.startswith(cmd) for cmd in self.commands)

    @staticmethod
    def command(commands) -> BaseFilter:
        return filters._Command(commands)

    # NEW: فیلتر بر اساس نوع Update
    class _UpdateType(BaseFilter):
        def __init__(self, update_type: UpdateTypeEnum):
            self.update_type = update_type
        def __call__(self, update: Update) -> bool:
            return update.type == self.update_type

    @staticmethod
    def update_type(t: UpdateTypeEnum) -> BaseFilter:
        return filters._UpdateType(t)

    # NEW: فیلتر بر اساس نوع Event
    class _EventType(BaseFilter):
        def __init__(self, event_type: EventTypeEnum):
            self.event_type = event_type
        def __call__(self, update: Update) -> bool:
            return (update.event_data is not None
                    and update.event_data.type == self.event_type)

    @staticmethod
    def event_type(t: EventTypeEnum) -> BaseFilter:
        return filters._EventType(t)

    # NEW: فیلترهای آماده
    edited_message = _UpdateType(UpdateTypeEnum.UpdatedMessage)
    removed_message = _UpdateType(UpdateTypeEnum.RemovedMessage)
    started_bot = _UpdateType(UpdateTypeEnum.StartedBot)
    stopped_bot = _UpdateType(UpdateTypeEnum.StoppedBot)
    event_data = _UpdateType(UpdateTypeEnum.EventData)


class Handler:
    def __init__(self, callback: Callable[[Update, CallbackContext], Awaitable[None]], filter_: Optional[BaseFilter] = None):
        self.callback = callback
        self.filter = filter_

    def check(self, update: Update) -> bool:
        if self.filter is None:
            return True
        return self.filter(update)


class MessageHandler(Handler):
    def __init__(self, filter_: BaseFilter, callback):
        super().__init__(callback, filter_)


class CommandHandler(MessageHandler):
    def __init__(self, command, callback):
        super().__init__(filters.command(command), callback)


# NEW: هندلر رویدادها (BotJoined, BotRemoved, BotPermissionsChanged)
class EventHandler(Handler):
    def __init__(self, event_type: EventTypeEnum, callback):
        super().__init__(callback, filters.event_type(event_type))


# NEW: هندلر عمومی برای هر نوع Update (ویرایش/حذف پیام و ...)
class UpdateHandler(Handler):
    def __init__(self, update_type: UpdateTypeEnum, callback):
        super().__init__(callback, filters.update_type(update_type))


# ==========================================
# بخش ۴: شبکه و API (RubikaBot)
# ==========================================

class RubikaBot:
    def __init__(self, token: str, base_url: str = "https://botapi.rubika.ir/v3/"):
        self.token = token
        self.base_url = base_url
        self.timeout = 30

    def _post(self, method: str, data: dict = None, timeout: int = -1) -> dict:
        if timeout < 0:
            timeout = self.timeout
        headers = {"Content-Type": "application/json"}
        res = requests.post(
            url=f"{self.base_url}{self.token}/{method}",
            headers=headers,
            json=data if data is not None else {},
            timeout=timeout
        )
        return res.json()

    
    def get_me(self) -> Bot:
        return Bot(self._post("getMe").get("data", {}).get("bot", {}))

    def get_updates(self, offset_id: str = "", limit: int = 100) -> dict:
        return self._post("getUpdates", {'offset_id': offset_id, 'limit': limit})

    async def send_message(self, chat_id: str, text: str, **kwargs):
        data = {"chat_id": chat_id, "text": text, **kwargs}
        return await asyncio.to_thread(self._post, "sendMessage", data)

    async def send_poll(self, chat_id: str, question: str, options: List[str], **kwargs):
        data = {"chat_id": chat_id, "question": question, "options": options, **kwargs}
        return await asyncio.to_thread(self._post, "sendPoll", data)

    async def send_location(self, chat_id: str, latitude: str, longitude: str, **kwargs):
        data = {"chat_id": chat_id, "latitude": latitude, "longitude": longitude, **kwargs}
        return await asyncio.to_thread(self._post, "sendLocation", data)

    async def send_contact(self, chat_id: str, first_name: str, last_name: str, phone_number: str, **kwargs):
        data = {"chat_id": chat_id, "first_name": first_name, "last_name": last_name, "phone_number": phone_number, **kwargs}
        return await asyncio.to_thread(self._post, "sendContact", data)

    async def get_chat(self, chat_id: str):
        return await asyncio.to_thread(self._post, "getChat", {"chat_id": chat_id})

    async def forward_message(self, from_chat_id: str, message_id: str, to_chat_id: str, **kwargs):
        data = {"from_chat_id": from_chat_id, "message_id": message_id, "to_chat_id": to_chat_id, **kwargs}
        return await asyncio.to_thread(self._post, "forwardMessage", data)

    async def edit_message_text(self, chat_id: str, message_id: str, text: str, **kwargs):
        data = {"chat_id": chat_id, "message_id": message_id, "text": text, **kwargs}
        return await asyncio.to_thread(self._post, "editMessageText", data)

    async def edit_message_keypad(self, chat_id: str, message_id: str, inline_keypad: dict, **kwargs):
        data = {"chat_id": chat_id, "message_id": message_id, "inline_keypad": inline_keypad, **kwargs}
        return await asyncio.to_thread(self._post, "editMessageKeypad", data)

    async def delete_message(self, chat_id: str, message_id: str):
        return await asyncio.to_thread(self._post, "deleteMessage", {"chat_id": chat_id, "message_id": message_id})

    async def set_commands(self, bot_commands: List[dict]):
        return await asyncio.to_thread(self._post, "setCommands", {"bot_commands": bot_commands})

    async def update_bot_endpoints(self, url: str, type: str = "ReceiveUpdate"):
        return await asyncio.to_thread(self._post, "updateBotEndpoints", {"url": url, "type": type})

    async def edit_chat_keypad(self, chat_id: str, chat_keypad_type: str = "Remove", chat_keypad: Optional[dict] = None):
        data = {"chat_id": chat_id, "chat_keypad_type": chat_keypad_type}
        if chat_keypad:
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
        return await asyncio.to_thread(self._post, "banChatMember", {"chat_id": chat_id, "user_id": user_id})

    async def unban_chat_member(self, chat_id: str, user_id: str):
        return await asyncio.to_thread(self._post, "unbanChatMember", {"chat_id": chat_id, "user_id": user_id})


# ==========================================
# بخش ۵: Application (مدیریت Loop و Handler)
# ==========================================

class Application:
    def __init__(self, token: str, base_url: str = "https://botapi.rubika.ir/v3/"):
        self.token = token
        self.base_url = base_url
        self.handlers: List[Handler] = []
        self._offset_id = ""
        self._running = False
        self.bot = RubikaBot(token, base_url)

    def add_handler(self, handler: Handler):
        self.handlers.append(handler)

    async def _process_update(self, update: Update):
        context = CallbackContext(self.bot, update)
        for handler in self.handlers:
            if handler.check(update):
                try:
                    await handler.callback(update, context)
                except Exception as e:
                    logging.error(f"Error in handler: {e}", exc_info=True)

    async def _drain_pending_updates(self, max_rounds: int = 20):
        """
        آپدیت‌های قدیمی موجود در سرور را تا حد امکان پاک می‌کند.
        از offset_id خالی شروع می‌کنیم و صرفاً next_offset_id واقعی را دنبال می‌کنیم.
        """
        logging.info("Draining pending updates...")
        probe_offset = ""
        last_offset = ""

        for _ in range(max_rounds):
            try:
                resp = await asyncio.to_thread(
                    self.bot.get_updates, offset_id=probe_offset, limit=100
                )
                if resp.get("status") == "INVALID_INPUT":
                    logging.warning("Drain skipped: INVALID_INPUT from server.")
                    self._offset_id = last_offset
                    return

                data = resp.get("data", {})
                updates = data.get("updates", [])
                next_offset = data.get("next_offset_id")

                if not updates:
                    logging.info("No more pending updates. Drain complete.")
                    self._offset_id = next_offset or last_offset
                    return

                last_offset = next_offset or last_offset
                probe_offset = last_offset

                logging.info(f"Drained {len(updates)} pending updates, offset={last_offset}")

            except Exception as e:
                logging.error(f"Error during drain: {e}")
                self._offset_id = last_offset
                return

        logging.warning("Drain reached max rounds; there might still be pending updates.")
        self._offset_id = last_offset    

    async def run_polling(self, poll_interval: float = 1.0, drop_pending: bool = True):
        
        if drop_pending:
            await self._drain_pending_updates()
        
        self._running = True
        logging.info("Bot started polling...")
        while self._running:
            try:
                response = await asyncio.to_thread(
                    self.bot.get_updates, offset_id=self._offset_id, limit=100
                )

                if response.get("status") == "INVALID_INPUT":
                    logging.warning("Invalid offset, resetting to empty.")
                    self._offset_id = ""
                    await asyncio.sleep(poll_interval)
                    continue

                data = response.get("data", {})
                updates_raw = data.get("updates", [])
                next_offset = data.get("next_offset_id")

                for raw_update in updates_raw:
                    update = Update(raw_update)
                    await self._process_update(update)

                if next_offset:
                    self._offset_id = next_offset

                await asyncio.sleep(poll_interval)
            except Exception as e:
                logging.error(f"Polling error: {e}")
                await asyncio.sleep(5)

    def stop(self):
        self._running = False


# ==========================================
# بخش ۶: پایگاه داده ساده (برای اجرای مستقیم)
# ==========================================

class Database:
    def __init__(self):
        self._tables: Dict[str, Dict[str, dict]] = {}

    def create_table(self, name: str, schema: dict = None):
        if name not in self._tables:
            self._tables[name] = {}

    def set(self, table: str, data: dict):
        if table not in self._tables:
            self._tables[table] = {}
        key = list(data.values())[0]
        self._tables[table][str(key)] = data

    def get(self, table: str, query: dict) -> Optional[dict]:
        if table not in self._tables:
            return None
        key = str(list(query.values())[0])
        return self._tables[table].get(key)


# ==========================================
# بخش ۷: مثال استفاده
# ==========================================

async def start_handler(update: Update, context: CallbackContext):
    if update.new_message:
        await context.bot.send_message(
            chat_id=update.chat_id,
            text="سلام! به بات خوش آمدید."
        )

async def echo_handler(update: Update, context: CallbackContext):
    if update.new_message and update.new_message.text:
        await context.bot.send_message(
            chat_id=update.chat_id,
            text=f"شما گفتید: {update.new_message.text}"
        )


# NEW: هندلر رویداد BotJoined
async def on_bot_joined(update: Update, context: CallbackContext):
    logging.info(f"Bot joined chat: {update.chat_id}")
    await context.bot.send_message(
        chat_id=update.chat_id,
        text="ممنون که منو اضافه کردید! برای شروع /start رو بزنید."
    )


# NEW: هندلر رویداد BotRemoved
async def on_bot_removed(update: Update, context: CallbackContext):
    logging.info(f"Bot removed from chat: {update.chat_id}")


# NEW: هندلر ویرایش پیام
async def on_message_edited(update: Update, context: CallbackContext):
    if update.updated_message:
        logging.info(f"Message {update.updated_message.message_id} edited in {update.chat_id}")


# NEW: هندلر حذف پیام
async def on_message_removed(update: Update, context: CallbackContext):
    logging.info(f"Message {update.removed_message_id} removed in {update.chat_id}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    TOKEN = ""
    app = Application(TOKEN)

    # هندلرهای پیام
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(MessageHandler(filters.text & ~filters.command("start"), echo_handler))

    # NEW: هندلرهای رویداد
    app.add_handler(EventHandler(EventTypeEnum.BotJoined, on_bot_joined))
    app.add_handler(EventHandler(EventTypeEnum.BotRemoved, on_bot_removed))

    # NEW: هندلرهای Update
    app.add_handler(UpdateHandler(UpdateTypeEnum.UpdatedMessage, on_message_edited))
    app.add_handler(UpdateHandler(UpdateTypeEnum.RemovedMessage, on_message_removed))

    try:
        asyncio.run(app.run_polling())
    except KeyboardInterrupt:
        app.stop()
        print("Bot stopped.")
