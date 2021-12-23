import re
import string
import urllib.parse
from itertools import groupby

from zoneinfo import ZoneInfo
from lxml import html

from django.utils import timezone
from gather_vision import models as app_models
from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise


class AuQldBcc:
    code = "au_qld_bcc"

    _regex_collapse_newline = re.compile(r"[\n\r]+")
    _regex_collapse_whitespace = re.compile(r"\s{2,}")
    _regex_signatures = re.compile("signatures.*", re.DOTALL)

    def __init__(
        self,
        logger: Logger,
        http_client: HttpClient,
        normalise: Normalise,
        tz: ZoneInfo,
    ):
        self._logger = logger
        self._http_client = http_client
        self._normalise = normalise
        self._tz = tz

        self._source = app_models.InformationSource.objects.get(name=self.code)

    def update_petitions(self):
        self._logger.info("Updating Brisbane City Council petitions.")

        retrieved_date = timezone.now()

        petitions_seen = 0
        petitions_created = 0
        changes_seen = 0
        changes_added = 0

        petitions = self.get_petitions()
        for petition in petitions:
            data = self.get_petition(petition)

            ref_id = petition["ref_id"]
            title = petition["title"]
            closed_date = petition["closed_at"]

            view_url = data["view_url"]
            principal = data["principal"]
            body = data["body"]

            signatures = data["signatures"]

            obj, created = app_models.PetitionItem.objects.update_or_create(
                source=self._source,
                code=ref_id,
                defaults={
                    "title": title,
                    "view_url": view_url,
                    "principal": principal,
                    "body": body,
                    "closed_date": closed_date,
                },
            )

            petitions_seen += 1
            if created:
                petitions_created += 1

            change, created = app_models.PetitionChange.objects.get_or_create(
                petition=obj,
                retrieved_date=retrieved_date,
                defaults={
                    "signatures": signatures,
                },
            )
            changes_seen += 1
            if created:
                changes_added += 1

            if petitions_seen % 5 == 0:
                self._logger.info(
                    f"Running total petitions {petitions_seen} "
                    f"({petitions_created} created) "
                    f"changes {changes_seen} ({changes_added} added)."
                )

        self._logger.info(
            f"Petitions {petitions_seen} ({petitions_created} created) "
            f"changes {changes_seen} ({changes_added} added)."
        )
        self._logger.info("Finished updating petitions.")

    def get_petitions(self):
        url = "https://epetitions.brisbane.qld.gov.au/"
        r = self._http_client.get(url)
        tree = html.fromstring(r.text)

        if tree is None:
            raise ValueError("No html available.")

        table = tree.xpath('//table[contains(@class, "petitions")]')
        if len(table) != 1:
            raise ValueError("Found other than 1 table in html.")

        rows = table[0].xpath("//tr")
        for row in rows:
            if len(row.xpath("th")) == 3 and len(row.xpath("td")) == 0:
                continue
            cells = row.xpath("td")
            title = cells[0].xpath(".//text()")[0].strip()
            principal = cells[1].xpath("text()")[0].strip()
            closed_date = cells[2].xpath("text()")[0].strip()
            view_url = cells[0].xpath("a/@href")[0].strip()
            ref_id = view_url.split("/")[-1]
            item = {
                "ref_id": ref_id,
                "title": title,
                "view_url": view_url,
                "principal": principal,
                "closed_at": self._normalise.parse_date(closed_date, self._tz),
            }
            yield item

    def get_petition(self, data: dict):
        ref_id = data["ref_id"]
        url = "https://epetitions.brisbane.qld.gov.au/petition/view/pid/"
        url += urllib.parse.quote(ref_id)
        r = self._http_client.get(url)
        tree = html.fromstring(r.text)

        title = tree.xpath(
            '//div[@class="page-title"]/h1/text()',
        )[0].strip()

        principal = tree.xpath(
            '((//table[@class="petition-details"]//tr)[1]/td)[2]/text()',
        )[0].strip()

        closed_at = tree.xpath(
            '((//table[@class="petition-details"]//tr)[2]/td)[2]/text()',
        )[0].strip()

        sig_xpath = '((//table[@class="petition-details"]//tr)[3]/td)[2]'
        signatures = tree.xpath(sig_xpath)[0].text_content() or ""
        signatures = (
            signatures.casefold()
            .replace("(view signatures)", "")
            .replace("(view signature)", "")
            .replace("signatures", "")
            .replace("signature", "")
        ).strip()

        body = tree.xpath('//div[@id="petition-details"]')[0].text_content() or ""
        body = self._regex_collapse_whitespace.sub(
            " ", self._regex_collapse_newline.sub("\n", body)
        ).strip()

        item = {
            "title": title,
            "principal": principal,
            "body": body,
            "signatures": int(signatures) if signatures else 0,
            "closed_at": self._normalise.parse_date(closed_at, self._tz),
            "view_url": url,
            "ref_id": ref_id,
        }

        return item

    def _allowed_chars(self):
        return string.digits + string.ascii_letters + string.punctuation

    def _normalise_string(self, value):
        if not value:
            return ""

        value = value.replace("’", "'")
        remove_newlines = value.replace("\n", " ").replace("\r", " ").strip()
        result = "".join(
            c if c in self._allowed_chars() else " " for c in remove_newlines
        ).strip()
        return result

    def _custom_split(self, value, chars):
        return ["".join(gp) for _, gp in groupby(value, lambda char: char in chars)]
