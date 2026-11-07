# this is a silplified version of metadata.py from rubka module
# https://github.com/Mahdy-Ahmadi/rubka/blob/main/rubka/metadata.py


import re
from html.parser import HTMLParser
from typing import Any, Dict, List


def _normalize_multiline_quote(text: str) -> str:
    lines = text.splitlines()
    normalized_lines = []
    quote_block = []

    for line in lines + [""]:
        if line.startswith(">"):
            quote_block.append(line[1:].strip())
        else:
            if quote_block:
                normalized_lines.append("$" + "\n".join(quote_block) + "$")
                quote_block = []
            normalized_lines.append(line)
    return "\n".join(normalized_lines).strip()


class _HtmlToMarkdown(HTMLParser):
    """
    تبدیل‌کننده‌ی سبک HTML به Markdown (بدون وابستگی خارجی).
    تگ‌های پشتیبانی‌شده: b/strong, i/em, u, s/strike/del, code, pre,
    a, blockquote, br, p, span.spoiler, و بقیه به‌صورت متن خام.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._out: List[str] = []
        self._stack: List[str] = []

    # --- helpers ---
    def _emit(self, text: str):
        self._out.append(text)

    def _wrap(self, tag: str, mark: str):
        self._emit(mark)
        self._stack.append(tag)

    # --- HTMLParser hooks ---
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ("b", "strong"):
            self._wrap(tag, "**")
        elif tag in ("i", "em"):
            self._wrap(tag, "||")  # در کد اصلی <i> به || (spoiler) تبدیل می‌شد
        elif tag == "u":
            self._wrap(tag, "--")
        elif tag in ("s", "strike", "del"):
            self._wrap(tag, "~~")
        elif tag == "code":
            self._wrap(tag, "`")
        elif tag == "pre":
            self._wrap(tag, "```\n")
        elif tag == "a":
            href = attrs.get("href", "")
            self._wrap(tag, f"[")
            self._stack.append(f"]({href})")
        elif tag == "blockquote":
            self._wrap(tag, "> ")
        elif tag == "br":
            self._emit("\n")
        elif tag == "p":
            self._emit("\n\n")
        elif tag == "span" and "spoiler" in (attrs.get("class") or ""):
            self._wrap(tag, "||")
        else:
            # تگ‌های ناشناخته: فقط متن داخلش رو نگه می‌داریم
            self._stack.append(tag)

    def handle_endtag(self, tag):
        if not self._stack:
            return
        # بستن mark مربوطه
        if tag in ("b", "strong"):
            self._emit("**")
        elif tag in ("i", "em"):
            self._emit("||")
        elif tag == "u":
            self._emit("--")
        elif tag in ("s", "strike", "del"):
            self._emit("~~")
        elif tag == "code":
            self._emit("`")
        elif tag == "pre":
            self._emit("\n```")
        elif tag == "a":
            # آخرین آیتم استک باید `](href)` باشه
            if self._stack and self._stack[-1].startswith("]("):
                self._emit(self._stack.pop())
        elif tag == "blockquote":
            pass
        elif tag == "span":
            # اگه spoiler بود، || بسته شد
            if self._stack and self._stack[-1] == "span":
                self._emit("||")
        # پاک کردن از استک
        if self._stack and self._stack[-1] == tag:
            self._stack.pop()

    def handle_data(self, data):
        self._emit(data)

    def get_markdown(self) -> str:
        return "".join(self._out)


def _html_to_markdown(html: str) -> str:
    parser = _HtmlToMarkdown()
    parser.feed(html)
    parser.close()
    return parser.get_markdown()


class Track_parsed:
    _PATT = re.compile(
        r"(?P<pre>```(?P<pre_c>[\s\S]*?)```)"
        r"|(?P<bold>\*\*(?P<bold_c>.*?)\*\*)"
        r"|(?P<mono>`(?P<mono_c>.*?)`)"
        r"|(?P<italic>__(?P<italic_c>.*?)__)"
        r"|(?P<underline>--(?P<underline_c>.*?)--)"
        r"|(?P<link>\[(?P<link_text>.*?)\]\((?P<link_url>\S+?)\))"
        r"|(?P<quote>\$(?P<quote_c>[\s\S]*?)\$)"
        r"|(?P<quote_md>^>(?P<quote_md_c>.*?)(?:\n|$))"
        r"|(?P<strike>~~(?P<strike_c>.*?)~~)"
        r"|(?P<spoiler>\|\|(?P<spoiler_c>.*?)\|\|)",
        flags=re.DOTALL,
    )
    _TYPE_MAP = {
        "pre": "Pre",
        "bold": "Bold",
        "mono": "Mono",
        "italic": "Italic",
        "underline": "Underline",
        "strike": "Strike",
        "spoiler": "Spoiler",
        "quote": "Quote",
        "quote_md": "Quote",
        "link": "Link",
        "mention": "MentionText",
    }

    @staticmethod
    def _utf16_len_java_style(s: str) -> int:
        return len(s.encode("utf-16-be")) // 2

    @staticmethod
    def _html2md(src: str) -> str:
        src = re.sub(r"<i>(.*?)</i>", r"||\1||", src, flags=re.DOTALL)
        src = re.sub(
            r'<span class="spoiler">(.*?)</span>', r"||\1||", src, flags=re.DOTALL
        )
        src = _html_to_markdown(src).strip()
        src = src.replace("@@SPOILER@@", "||")
        return src

    def transcribe(self, src: str, mode: str = "MARKDOWN") -> Dict[str, Any]:
        if mode and mode.upper() == "HTML":
            src = self._html2md(src)
        src = _normalize_multiline_quote(src)
        payload_parts: List[Dict[str, Any]] = []
        normalized_text = src
        byte_offset = 0
        char_offset = 0
        matches = list(self._PATT.finditer(src))
        for m in matches:
            whole = m.group(0)
            start, end = m.span()
            adj_from = self._utf16_len_java_style(src[:start]) - byte_offset
            adj_char_from = start - char_offset
            gname = m.lastgroup
            if not gname:
                continue
            if gname == "link":
                inner = m.group("link_text") or ""
                link_href = m.group("link_url")
                if link_href.startswith("u0"):
                    gname = "mention"
            else:
                inner = m.group(f"{gname}_c") or ""
                link_href = None
            if gname in [
                "quote",
                "quote_md",
                "bold",
                "italic",
                "underline",
                "spoiler",
                "strike",
                "mention",
            ]:
                inner_metadata = self.transcribe(inner, mode="MARKDOWN")
                inner = inner_metadata["text"]
                if "metadata" in inner_metadata:
                    for part in inner_metadata["metadata"]["meta_data_parts"]:
                        part["from_index"] += adj_from
                        payload_parts.append(part)
            if inner == "":
                continue
            content_utf16_len = self._utf16_len_java_style(inner)
            part: Dict[str, Any] = {
                "type": self._TYPE_MAP.get(gname, "Unknown"),
                "from_index": adj_from,
                "length": content_utf16_len,
            }
            if gname == "mention":
                part["type"] = "MentionText"
                part["mention_text_user_id"] = link_href
            elif link_href:
                part["type"] = "Link"
                part["link_url"] = link_href
            payload_parts.append(part)
            normalized_text = (
                normalized_text[:adj_char_from]
                + inner
                + normalized_text[end - char_offset :]
            )
            byte_offset += self._utf16_len_java_style(whole) - content_utf16_len
            char_offset += (end - start) - len(inner)

        result: Dict[str, Any] = {"text": normalized_text.strip()}
        if payload_parts:
            result["metadata"] = {"meta_data_parts": payload_parts}

        return result

    def parse(self, text: str, parse_mode: str = "MARKDOWN") -> Dict[str, Any]:
        return self.transcribe(text, mode=parse_mode)