from typing import List, Optional, TYPE_CHECKING


if TYPE_CHECKING:
    from .bot import RubikaBot

from .enums import (
    ButtonCalendarTypeEnum,
    ButtonLocationTypeEnum,
    ButtonSelectionGetEnum,
    ButtonSelectionSearchEnum,
    ButtonSelectionTypeEnum,
    ButtonTextboxTypeKeypadEnum,
    ButtonTextboxTypeLineEnum,
    ButtonTypeEnum,
    EnumChatAccess,
    EventJoinTypeEnum,
    EventTypeEnum,
    MetadataTypeEnum,
    UpdateTypeEnum,
    ChatTypeEnum,
)


def _enum_value(enum_type, value):
    """Convert an API string to an enum member; preserve unknown values as None."""
    if isinstance(value, enum_type):
        return value
    if isinstance(value, str):
        try:
            return enum_type(value)
        except ValueError:
            return None
    return None


def _nested(model_type, value):
    """Create a nested model from a dict, or pass through an existing model."""
    if isinstance(value, model_type):
        return value
    if isinstance(value, dict):
        return model_type(value)
    return value


def _nested_list(model_type, value):
    """Create a list of models from dicts, models, or a mix of both."""
    if not isinstance(value, list):
        return value
    result = []
    for item in value:
        if isinstance(item, model_type):
            result.append(item)
        elif isinstance(item, dict):
            result.append(model_type(item))
    return result


# ==========================================
# مدل های پایه
# ==========================================

class File:
    def __init__(self, data: dict):
        if isinstance(data, File):
            self.__dict__.update(data.__dict__)
            return
        self.file_id: str = data.get("file_id", "")
        self.file_name: str = data.get("file_name", "")
        self.size: str = data.get("size", "")


class Location:
    def __init__(self, data: dict):
        if isinstance(data, Location):
            self.__dict__.update(data.__dict__)
            return
        self.longitude: str = data.get("longitude", "")
        self.latitude: str = data.get("latitude", "")


class AuxData:
    def __init__(self, data: dict):
        if isinstance(data, AuxData):
            self.__dict__.update(data.__dict__)
            return
        self.start_id: str = data.get("start_id", "")
        self.button_id: str = data.get("button_id", "")


class ForwardedFrom:
    def __init__(self, data: dict):
        if isinstance(data, ForwardedFrom):
            self.__dict__.update(data.__dict__)
            return
        self.type_from: str = data.get("type_from", "")
        self.message_id: str = data.get("message_id", "")
        self.from_chat_id: str = data.get("from_chat_id", "")
        self.from_sender_id: str = data.get("from_sender_id", "")


class ContactMessage:
    def __init__(self, data: dict):
        if isinstance(data, ContactMessage):
            self.__dict__.update(data.__dict__)
            return
        self.phone_number: str = data.get("phone_number", "")
        self.first_name: str = data.get("first_name", "")
        self.last_name: str = data.get("last_name", "")


class PollStatus:
    def __init__(self, data: dict):
        if isinstance(data, PollStatus):
            self.__dict__.update(data.__dict__)
            return
        self.state: str = data.get("state", "")
        self.selection_index: int = data.get("selection_index", -1)
        self.percent_vote_options: List[int] = data.get("percent_vote_options", [])
        self.total_vote: int = data.get("total_vote", 0)
        self.show_total_votes: bool = data.get("show_total_votes", False)


class Poll:
    def __init__(self, data: dict):
        if isinstance(data, Poll):
            self.__dict__.update(data.__dict__)
            return
        self.question: str = data.get("question", "")
        self.options: List[str] = data.get("options", [])
        self.poll_status: Optional[PollStatus] = _nested(
            PollStatus, data.get("poll_status")
        )


class Sticker:
    def __init__(self, data: dict):
        if isinstance(data, Sticker):
            self.__dict__.update(data.__dict__)
            return
        self.sticker_id: str = data.get("sticker_id", "")
        self.file: Optional[File] = _nested(File, data.get("file"))
        self.emoji_character: str = data.get("emoji_character", "")


class Bot:
    def __init__(self, data: dict):
        if isinstance(data, Bot):
            self.__dict__.update(data.__dict__)
            return
        self.bot_id: str = data.get("bot_id", "")
        self.bot_title: str = data.get("bot_title", "")
        self.avatar: Optional[File] = _nested(File, data.get("avatar"))
        self.description: str = data.get("description", "")
        self.username: str = data.get("username", "")
        self.start_message: str = data.get("start_message", "")
        self.share_url: str = data.get("share_url", "")

class Message:
    def __init__(self, data: dict, chat_id: str, bot: "RubikaBot"):
        self.bot = bot
        self.data = data

        if isinstance(data, Message):
            self.__dict__.update(data.__dict__)
            return

        self.message_id: str = data.get("message_id", "")
        self.text: str = data.get("text", "")
        self.time: int = data.get("time", 0)
        self.chat_id: str = chat_id
        self.is_edited: bool = data.get("is_edited", False)
        self.sender_type: str = data.get("sender_type", "")
        self.sender_id: str = data.get("sender_id", "")
        self.aux_data: Optional[AuxData] = _nested(
            AuxData, data.get("aux_data")
        )
        self.file: Optional[File] = _nested(File, data.get("file"))
        self.reply_to_message_id: str = data.get("reply_to_message_id", "")
        self.forwarded_from: Optional[ForwardedFrom] = _nested(
            ForwardedFrom, data.get("forwarded_from")
        )
        self.forwarded_no_link: str = data.get("forwarded_no_link", "")
        self.location: Optional[Location] = _nested(
            Location, data.get("location")
        )
        self.sticker: Optional[Sticker] = _nested(
            Sticker, data.get("sticker")
        )
        self.contact_message: Optional[ContactMessage] = _nested(
            ContactMessage, data.get("contact_message")
        )
        self.poll: Optional[Poll] = _nested(Poll, data.get("poll"))

    def reply_text(self, text: str):
        return self.bot.send_message(
            chat_id=self.chat_id,
            text=text,
            reply_to_message_id=self.message_id
        )

    def reply_video(self, text: str):
        return self.bot.send_message(
            chat_id=self.chat_id,
            text=text,
            reply_to_message_id=self.message_id
        )

    def reply_photo(self, text: str):
        return self.bot.send_message(
            chat_id=self.chat_id,
            text=text,
            reply_to_message_id=self.message_id
        )
    
    def delete(self):
        return self.bot.delete_message(
            chat_id=self.chat_id,
            message_id=self.message_id
        )

    def forward(self, to_chat_id: str):
        return self.bot.forward_message(
            from_chat_id=self.chat_id,
            message_id=self.message_id,
            to_chat_id=to_chat_id
        )


class Event:
    def __init__(self, data: dict):
        if isinstance(data, Event):
            self.__dict__.update(data.__dict__)
            return
        self.type: Optional[EventTypeEnum] = _enum_value(
            EventTypeEnum, data.get("type")
        )

        raw_access_list = data.get("access_list")
        self.access_list: Optional[List[EnumChatAccess]] = None
        if isinstance(raw_access_list, list):
            self.access_list = [
                access
                for item in raw_access_list
                if (access := _enum_value(EnumChatAccess, item)) is not None
            ]

        self.join_type: Optional[EventJoinTypeEnum] = _enum_value(
            EventJoinTypeEnum, data.get("join_type")
        )

def _msg_nested(data,bot,chat_id):
    if isinstance(data, Message):
        return data
    if isinstance(data, dict):
        return Message(data,chat_id,bot)
    return data


class Update:
    def __init__(self, data: dict , bot):
        if isinstance(data, Update):
            self.__dict__.update(data.__dict__)
            return
        self.type: Optional[UpdateTypeEnum] = _enum_value(
            UpdateTypeEnum, data.get("type")
        )
        self.chat_id: str = data.get("chat_id", "")
        self.removed_message_id: Optional[str] = data.get("removed_message_id")
        self.new_message: Optional[Message] = _msg_nested(
           data.get("new_message"),bot,self.chat_id
        )
        self.updated_message: Optional[Message] = _msg_nested(
            data.get("updated_message"),bot,self.chat_id
        )
        self.event_data: Optional[Event] = _nested(Event, data.get("event_data"))


# ==========================================
# مدل های دکمه و کیپد
# ==========================================

class ButtonSelectionItem:
    def __init__(self, data: dict):
        if isinstance(data, ButtonSelectionItem):
            self.__dict__.update(data.__dict__)
            return
        self.text: str = data.get("text", "")
        self.image_url: str = data.get("image_url", "")
        self.type: Optional[ButtonSelectionTypeEnum] = _enum_value(
            ButtonSelectionTypeEnum, data.get("type")
        )


class ButtonSelection:
    def __init__(self, data: dict):
        if isinstance(data, ButtonSelection):
            self.__dict__.update(data.__dict__)
            return
        self.selection_id: str = data.get("selection_id", "")
        self.search_type: Optional[ButtonSelectionSearchEnum] = _enum_value(
            ButtonSelectionSearchEnum, data.get("search_type")
        )
        self.get_type: Optional[ButtonSelectionGetEnum] = _enum_value(
            ButtonSelectionGetEnum, data.get("get_type")
        )
        self.items: List[ButtonSelectionItem] = _nested_list(
            ButtonSelectionItem, data.get("items", [])
        )
        self.is_multi_selection: bool = data.get("is_multi_selection", False)
        self.columns_count: str = data.get("columns_count", "")
        self.title: str = data.get("title", "")


class ButtonCalendar:
    def __init__(self, data: dict):
        if isinstance(data, ButtonCalendar):
            self.__dict__.update(data.__dict__)
            return
        self.default_value: Optional[str] = data.get("default_value")
        self.type: Optional[ButtonCalendarTypeEnum] = _enum_value(
            ButtonCalendarTypeEnum, data.get("type")
        )
        self.min_year: str = data.get("min_year", "")
        self.max_year: str = data.get("max_year", "")
        self.title: str = data.get("title", "")


class ButtonNumberPicker:
    def __init__(self, data: dict):
        if isinstance(data, ButtonNumberPicker):
            self.__dict__.update(data.__dict__)
            return
        self.min_value: str = data.get("min_value", "")
        self.max_value: str = data.get("max_value", "")
        self.default_value: Optional[str] = data.get("default_value")
        self.title: str = data.get("title", "")


class ButtonStringPicker:
    def __init__(self, data: dict):
        if isinstance(data, ButtonStringPicker):
            self.__dict__.update(data.__dict__)
            return
        self.items: List[str] = data.get("items", [])
        self.default_value: Optional[str] = data.get("default_value")
        self.title: Optional[str] = data.get("title")


class ButtonTextbox:
    def __init__(self, data: dict):
        if isinstance(data, ButtonTextbox):
            self.__dict__.update(data.__dict__)
            return
        self.type_line: Optional[ButtonTextboxTypeLineEnum] = _enum_value(
            ButtonTextboxTypeLineEnum, data.get("type_line")
        )
        self.type_keypad: Optional[ButtonTextboxTypeKeypadEnum] = _enum_value(
            ButtonTextboxTypeKeypadEnum, data.get("type_keypad")
        )
        self.place_holder: Optional[str] = data.get("place_holder")
        self.title: Optional[str] = data.get("title")
        self.default_value: Optional[str] = data.get("default_value")


class ButtonLocation:
    def __init__(self, data: dict):
        if isinstance(data, ButtonLocation):
            self.__dict__.update(data.__dict__)
            return
        self.default_pointer_location = _nested(
            Location, data.get("default_pointer_location")
        )
        self.default_map_location = _nested(
            Location, data.get("default_map_location")
        )
        self.type: Optional[ButtonLocationTypeEnum] = _enum_value(
            ButtonLocationTypeEnum, data.get("type")
        )
        self.title: Optional[str] = data.get("title")


class Button:
    def __init__(self, data: dict):
        if isinstance(data, Button):
            self.__dict__.update(data.__dict__)
            return
        self.id: str = data.get("id", "")
        self.type: Optional[ButtonTypeEnum] = _enum_value(
            ButtonTypeEnum, data.get("type")
        )
        self.button_text: str = data.get("button_text", "")
        self.button_selection = _nested(
            ButtonSelection, data.get("button_selection")
        )
        self.button_calendar = _nested(ButtonCalendar, data.get("button_calendar"))
        self.button_number_picker = _nested(
            ButtonNumberPicker, data.get("button_number_picker")
        )
        self.button_string_picker = _nested(
            ButtonStringPicker, data.get("button_string_picker")
        )
        self.button_location = _nested(ButtonLocation, data.get("button_location"))
        self.button_textbox = _nested(ButtonTextbox, data.get("button_textbox"))


class KeypadRow:
    def __init__(self, data):
        if isinstance(data, KeypadRow):
            self.__dict__.update(data.__dict__)
            return
        if isinstance(data, list):
            data = {"buttons": data}
        self.buttons: List[Button] = _nested_list(Button, data.get("buttons", []))


class Keypad:
    def __init__(self, data):
        if isinstance(data, Keypad):
            self.__dict__.update(data.__dict__)
            return
        self.rows: List[KeypadRow] = _nested_list(KeypadRow, data.get("rows", []))
        self.resize_keyboard: bool = data.get("resize_keyboard", False)
        self.one_time_keyboard: bool = data.get("one_time_keyboard", False)


class MetadataPart:
    def __init__(self, data: dict):
        if isinstance(data, MetadataPart):
            self.__dict__.update(data.__dict__)
            return
        self.type: Optional[MetadataTypeEnum] = _enum_value(
            MetadataTypeEnum, data.get("type")
        )
        self.from_index: int = data.get("from_index", 0)
        self.length: int = data.get("length", 0)
        self.link_url: str = data.get("link_url", "")
        self.mention_text_user_id: str = data.get("mention_text_user_id", "")


class Metadata:
    def __init__(self, data: dict):
        if isinstance(data, Metadata):
            self.__dict__.update(data.__dict__)
            return
        self.meta_data_parts: List[MetadataPart] = _nested_list(
            MetadataPart, data.get("meta_data_parts", [])
        )


class Chat:
    def __init__(self, data: dict):
        if isinstance(data, Chat):
            self.__dict__.update(data.__dict__)
            return
        self.chat_id: str = data.get("chat_id", "")
        self.chat_type: Optional[ChatTypeEnum] = _enum_value(
            ChatTypeEnum, data.get("chat_type")
        )
        self.user_id: str = data.get("user_id", "")
        self.first_name: str = data.get("first_name", "")
        self.last_name: str = data.get("last_name", "")
        self.title: str = data.get("title", "")
        self.username: str = data.get("username", "")


class BotCommand:
    def __init__(self, data: dict):
        if isinstance(data, BotCommand):
            self.__dict__.update(data.__dict__)
            return
        self.command: str = data.get("command", "")
        self.description: str = data.get("description", "")


class InlineMessage:
    def __init__(self, data: dict):
        if isinstance(data, InlineMessage):
            self.__dict__.update(data.__dict__)
            return
        self.sender_id: str = data.get("sender_id", "")
        self.text: str = data.get("text", "")
        self.file: Optional[File] = _nested(File, data.get("file"))
        self.location: Optional[Location] = _nested(Location, data.get("location"))
        self.aux_data: Optional[AuxData] = _nested(AuxData, data.get("aux_data"))
        self.message_id: str = data.get("message_id", "")
        self.chat_id: str = data.get("chat_id", "")


class MessageTextUpdate:
    def __init__(self, data: dict):
        if isinstance(data, MessageTextUpdate):
            self.__dict__.update(data.__dict__)
            return
        self.message_id: str = data.get("message_id", "")
        self.text: str = data.get("text", "")


class MessageKeypadUpdate:
    def __init__(self, data: dict):
        if isinstance(data, MessageKeypadUpdate):
            self.__dict__.update(data.__dict__)
            return
        self.message_id: str = data.get("message_id", "")
        self.inline_keypad: Optional[Keypad] = _nested(Keypad, data.get("inline_keypad"))
