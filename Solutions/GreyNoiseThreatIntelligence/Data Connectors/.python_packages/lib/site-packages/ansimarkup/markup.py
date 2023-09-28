import re
import builtins
from typing import Callable, List, Match, Optional, Mapping, Pattern, Sequence, Type, Union, Tuple

from colorama import Style

from .tags import style, background, foreground, all_tags


class AnsiMarkupError(Exception):
    pass


class MismatchedTag(AnsiMarkupError):
    pass


class UnbalancedTag(AnsiMarkupError):
    pass


UserTagsType = Mapping[str, Union[str, Callable[[], str]]]


class AnsiMarkup:
    """
    Produce colored terminal text with a tag-based markup.
    """

    def __init__(
        self,
        tags: Optional[UserTagsType] = None,
        always_reset: Optional[bool] = False,
        strict: Optional[bool] = False,
        tag_sep: Sequence[str] = "<>",
        ansistring_cls: Optional[Type[str]] = None,
        rawstring_cls: Optional[Type[str]] = None,
    ):
        """
        Parameters
        ----------
        tags: dict
           User-supplied tags, which are a mapping of tag names to the strings
           they will be substituted with.
        always_reset: bool
           Whether or not ``parse()`` should always end strings with a reset code.
        strict: bool
           Whether or not ``parse()`` should raise an error for missing closing tags.
        tag_sep: str
           The opening and closing characters of each tag (e.g. ``<>``, ``{}``).
        ansistring_cls: type
           String subtype to use in the ``ansistring()`` method.
        rawstring_cls: type
           Strign subtype to use to designate raw strings.
        """

        self.user_tags = tags if tags else {}
        self.always_reset = always_reset
        self.strict = strict
        self.tag_sep = tag_sep
        self.ansistring_cls = ansistring_cls if ansistring_cls else AnsiMarkupString
        self.rawstring_cls = self.raw = rawstring_cls if rawstring_cls else AnsiMarkupRawString

        self.re_tag = self.compile_tag_regex(tag_sep)

    def parse(self, *strings: str, aslist: bool = False) -> str:
        """Return a string with markup tags converted to ansi-escape sequences."""
        tags, results, res = [], [], []

        def re_sub(m):
            return self.sub_tag(m, tags, results)

        for _str in strings:
            if isinstance(_str, self.rawstring_cls):
                res.append(_str)
            else:
                res.append(self.re_tag.sub(re_sub, _str))

        if self.strict and tags:
            markup = "%s%s%s" % (self.tag_sep[0], tags.pop(0), self.tag_sep[1])
            raise MismatchedTag('opening tag "%s" has no corresponding closing tag' % markup)

        if self.always_reset:
            if not res[-1] == Style.RESET_ALL:
                res.append(Style.RESET_ALL)

        if aslist:
            return res
        return "".join(res)

    def ansiprint(self, *args: str, **kwargs):
        """Wrapper around builtins.print() that runs parse() on all arguments first."""

        new_args = (str(i) if not isinstance(i, str) else i for i in args)
        parts = self.parse(*new_args, aslist=True)
        builtins.print(*parts, **kwargs)

    def strip(self, text: str):
        """Return string with markup tags removed."""
        tags, results = [], []
        return self.re_tag.sub(lambda m: self.clear_tag(m, tags, results), text)

    def ansistring(self, markup: str):
        return self.ansistring_cls(self, markup)

    def __call__(self, text: str):
        return self.parse(text)

    def sub_tag(self, match: Match, tag_list: List[str], res_list: List[str]) -> str:
        markup, tag = match.group(0), match.group(1)
        closing = markup[1] == "/"
        res = None

        # Debug:
        # print(f"{markup=} {tag=} {tag_list=} {res_list=}")

        # Early exit if the closing tag matches the last known opening tag.
        if closing and tag_list and tag_list[-1] == tag:
            tag_list.pop()
            res_list.pop()
            return Style.RESET_ALL + "".join(res_list)

        # User-defined tags take preference over all other.
        if tag in self.user_tags:
            user_tag = self.user_tags[tag]
            res = user_tag() if callable(user_tag) else user_tag

        # Substitute on a direct match.
        elif tag in all_tags:
            res = all_tags[tag]

        # An alternative syntax for setting the color (e.g. <fg red>, <bg red>).
        elif tag.startswith("fg ") or tag.startswith("bg "):
            st, color = tag[:2], tag[3:]
            code = "38" if st == "fg" else "48"

            if st == "fg" and color in foreground:
                res = foreground[color]
            elif st == "bg" and color.islower() and color.upper() in background:
                res = background[color.upper()]
            elif color.isdigit() and int(color) <= 255:
                res = "\033[%s;5;%sm" % (code, color)
            elif re.match(r"#(?:[a-fA-F0-9]{3}){1,2}$", color):
                hex_color = color[1:]
                if len(hex_color) == 3:
                    hex_color *= 2
                res = "\033[%s;2;%s;%s;%sm" % ((code,) + hex_to_rgb(hex_color))
            elif color.count(",") == 2:
                colors = tuple(color.split(","))
                if all(x.isdigit() and int(x) <= 255 for x in colors):
                    res = "\033[%s;2;%s;%s;%sm" % ((code,) + colors)

        # Shorthand formats (e.g. <red,blue>, <bold,red,blue>).
        elif "," in tag:
            el_count = tag.count(",")

            if el_count == 1:
                fg, bg = tag.split(",")
                if fg in foreground and bg.islower() and bg.upper() in background:
                    res = foreground[fg] + background[bg.upper()]

            elif el_count == 2:
                st, fg, bg = tag.split(",")
                if st in style and (fg != "" or bg != ""):
                    if fg == "" or fg in foreground:
                        if bg == "" or (bg.islower() and bg.upper() in background):
                            res = style[st] + foreground.get(fg, "") + background.get(bg.upper(), "")

        # If nothing matches, return the full tag (i.e. <unknown>text</...>).
        if res is None:
            return markup

        # If closing tag is known, but did not early exit, something is wrong.
        if closing:
            if tag in tag_list:
                raise UnbalancedTag('closing tag "%s" violates nesting rules.' % markup)
            else:
                raise MismatchedTag('closing tag "%s" has no corresponding opening tag' % markup)

        tag_list.append(tag)
        res_list.append(res)

        return res

    def clear_tag(self, match: Match, tag_list: List[str], res_list: List[str]) -> str:
        pre_length = len(tag_list)
        try:
            self.sub_tag(match, tag_list, res_list)

            # If list did not change, the tag is unknown
            if len(tag_list) == pre_length:
                return match.group(0)

            # Otherwise, tag matched so remove it
            else:
                return ""

        # Tag matched but is invalid, remove it anyway
        except (UnbalancedTag, MismatchedTag):
            return ""

    def compile_tag_regex(self, tag_sep) -> Pattern:
        # Optimize the default:
        if tag_sep == "<>":
            tag_regex = re.compile(r"</?([^<>]+)>")
            return tag_regex

        if len(tag_sep) != 2:
            raise ValueError('tag_sep needs to have exactly two elements (e.g. "<>")')

        if tag_sep[0] == tag_sep[1]:
            raise ValueError("opening and closing characters cannot be the same")

        tag_regex = r"{0}/?([^{0}{1}]+){1}".format(tag_sep[0], tag_sep[1])
        return re.compile(tag_regex)


class AnsiMarkupRawString(str):
    pass


class AnsiMarkupString(str):
    """
    A string containing the original markup, the formatted string and the
    string with tags stripped off. Example usage::

      >>> t = AnsiMarkup().ansistring('<b>abc</b>')
      >>> repr(t)
      <b>abc</b>

      >>> print(t)
      abc  # in bold

      >>> len(t)
      3

      >>> len(AnsiMarkup().parse('<b>abc</b'))
      11

      >>> t.delta
      8

    """

    def __new__(cls, am, markup):
        parsed = am.parse(markup)

        new_str = str.__new__(cls, parsed)
        new_str.markup = markup
        new_str.stripped = am.strip(markup)

        # The difference in length between the formatted string and the string
        # with markup tags stripped off.
        new_str.delta: int = len(parsed) - len(new_str.stripped)

        return new_str

    def __len__(self):
        return len(self.stripped)

    def __repr__(self):
        return self.markup


def hex_to_rgb(value: str) -> Tuple[int, int, int]:
    return tuple(bytes.fromhex(value))
