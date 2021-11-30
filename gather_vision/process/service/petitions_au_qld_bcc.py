import pytz

from gather_vision.process.component.html_extract import HtmlExtract
from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise


class PetitionsAuQldBcc:
    code = "au_qld_bcc"

    def __init__(
        self,
        logger: Logger,
        http_client: HttpClient,
        normalise: Normalise,
        html_extract: HtmlExtract,
        tz: pytz.timezone,
    ):
        self._logger = logger
        self._http_client = http_client
        self._normalise = normalise
        self._html_extract = html_extract
        self._tz = tz

    def update_petitions(self):
        raise NotImplementedError()
