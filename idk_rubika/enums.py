from enum import Enum


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
