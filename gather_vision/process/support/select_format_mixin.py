from django.utils.html import escape


class SelectFormatMixin:
    def select_format(self, extension: str):
        """
        Select the format to render data.
        The format can be selected by
        extension in the final path segment or querystring 'ext'.

        Returns dict with keys 'status_code', 'message', 'extension', 'media_type'.
        """

        available_formats = {
            "txt": "text/plain",
            "json": "application/json",
            "csv": "text/csv",
            "ics": "text/calendar",
        }
        default_ext = "txt"

        if not extension or not extension.strip():
            extension = default_ext

        extension = extension.strip().strip(".")

        if extension not in available_formats:
            return {
                "status_code": 406,
                "message": escape(f"Format {extension} is not available."),
                "extension": None,
                "media_type": None,
            }

        return {
            "status_code": 200,
            "message": escape("Found matching media type."),
            "extension": escape(extension),
            "media_type": available_formats[extension],
        }
