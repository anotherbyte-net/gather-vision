import re
import unicodedata
from datetime import datetime
from typing import Iterable, Union, Optional
from zoneinfo import ZoneInfo

from django.utils.timezone import is_aware

from gather_vision.process.component.html_extract import HtmlUrlParser, HtmlDataParser


class Normalise:

    track_sep = "|"
    track_sep_spaced = " | "
    track_seps = [
        "[",
        "]",
        "{",
        "}",
        "(",
        ")",
        " ft ",
        " ft. ",
        " feat ",
        " feat. ",
        " featuring ",
        " w/ ",
        " x ",
        ",",
        " & ",
        " - ",
        " live at ",
        " from the ",
    ]

    def track(
        self,
        track_title: str,
        primary_artists: Union[str, Iterable[str]],
        featured_artists: Union[str, Iterable[str]],
    ):
        # normalise title
        name = track_title
        titles = self._track_norm_text(name)

        # normalise artists
        if primary_artists and isinstance(primary_artists, str):
            artist = primary_artists or ""
        else:
            artist = self.track_sep_spaced.join(primary_artists)

        if featured_artists and isinstance(featured_artists, str):
            artist += self.track_sep_spaced + featured_artists
        else:
            artist += self.track_sep_spaced + self.track_sep_spaced.join(
                featured_artists
            )

        artists = self._track_norm_text(artist)

        # extract title and artists
        title = ([titles[0]] if len(titles) > 0 else [""])[0]
        other = titles[1:] if len(titles) > 1 else []

        primary = [artists[0]] if len(artists) > 0 else [""]
        featured = artists[1:] if len(artists) > 1 else []
        featured = sorted(set(featured + other))

        if not title or not primary:
            raise ValueError(f"Invalid title '{title}' or primary artist '{primary}'.")

        # build the query strings
        queries = set()
        featured_count = len(featured)
        while featured_count > -1:
            featured_str = ", ".join(featured[0:featured_count])
            if featured_str:
                featured_str = ", " + featured_str

            queries.add(f"{title} - {primary[0]}{featured_str}")
            featured_count -= 1

        queries.add(f"{title} - {primary[0]}")

        queries = list(sorted(queries, key=lambda x: len(x), reverse=True))

        result = title, primary, featured, queries
        return result

    def _track_norm_text(self, value: str):
        norm = value or ""

        for sep in self.track_seps:
            norm = norm.replace(sep, self.track_sep_spaced)

        norm = norm.split(self.track_sep)

        result = []
        for item in norm:
            item = unicodedata.normalize("NFKC", item)
            item = item.lower()
            item = re.sub(r"[^\w\s\-\\'\.]+", " ", item)
            item = item.replace("-", " ").replace("_", " ")
            item = re.sub(r"\s+", " ", item)
            item = item.strip()
            if item:
                result.append(item)

        return result

    def parse_date(self, value: str, tz: ZoneInfo):
        if not value or not value.strip():
            return None
        patterns = [
            "%a, %d %b %Y %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%d %H:%M:%S",
            # 4/17/2014 10:00:00 PM
            "%m/%d/%Y %I:%M:%S %p",
            # 16/05/2020 12:00 AM
            "%d/%m/%Y %I:%M %p",
            "%d/%m/%Y",
            "%a, %d %b %Y",
            # 12:00 AM
            "%I:%M %p",
            "%d %B %Y %I:%M %p",
            "%Y-%m-%dT%H%M%S%z",
        ]
        for pattern in patterns:
            try:
                result = datetime.strptime(value.strip(), pattern)
                if not is_aware(result):
                    result = result.replace(tzinfo=tz)
                return result
            except ValueError:
                continue
            except OverflowError:
                continue
        raise ValueError(f"No datetime pattern matched '{value}'.")

    def petition_text(self, value: str):
        if not value:
            value = ""
        value = value.replace("\r\n", "\n")
        value = value.replace("\n\r", "\n")
        value = value.replace("\r", "\n")
        value = value.replace("\n", ", ")
        return value.strip()

    def regex_match(
        self,
        patterns: list[re.Pattern],
        value: str,
        unmatched_key: Optional[str] = None,
    ):
        for pattern in patterns:
            match = pattern.search(value)
            if not match:
                continue
            return match.groupdict()
        if unmatched_key:
            return {unmatched_key: value}
        raise ValueError(f"No patterns matched '{value}'.")

    def norm_signatures(self, value: str):
        value = value.replace("(View signature)", "")
        value = value.replace("\t", "")
        value = value.replace("\r", "")
        value = value.replace("\n", "")
        value = value.replace("signatures", "")
        value = value.replace("signature", "")
        value = value.strip()
        sig = int(value, 10) if value else 0
        return sig

    def extract_url_text(self, html: str):
        """Extract html anchor href and data."""
        parser = HtmlUrlParser()
        links = parser.extract(html)
        return links

    def extract_html_data(self, html: str):
        """Extract plain text from html."""
        parser = HtmlDataParser()
        links = parser.extract(html)
        return links
