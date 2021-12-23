from zoneinfo import ZoneInfo
from lxml import html

from django.utils import timezone
from gather_vision import models as app_models
from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise


class AuQld:

    code = "au_qld"

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
        self._logger.info("Updating Queensland Government petitions.")

        retrieved_date = timezone.now()

        petitions_seen = 0
        petitions_created = 0
        changes_seen = 0
        changes_added = 0

        petitions = self.get_petitions()
        for petition in petitions:
            data = self.get_petition(petition)

            body = data["body"]
            eligibility = data["eligibility"]
            principal = data["principal"]
            signatures = data["signatures"]
            sponsor = data["sponsor"]
            opened_date = data["posted_date"]
            closed_date = data["closing_date"]
            title = data["title"]

            ref_id = petition["ref_id"]
            view_url = petition["view_url"]

            obj, created = app_models.PetitionItem.objects.update_or_create(
                source=self._source,
                code=ref_id,
                defaults={
                    "title": title,
                    "view_url": view_url,
                    "principal": principal,
                    "body": body,
                    "closed_date": closed_date,
                    "sponsor": sponsor,
                    "opened_date": opened_date,
                    "eligibility": eligibility,
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
        url_base = "https://www.parliament.qld.gov.au"
        url = f"{url_base}/Work-of-the-Assembly/Petitions/Current-EPetitions"
        r = self._http_client.get(url)
        tree = html.fromstring(r.text)

        if tree is None:
            raise ValueError("No html available.")

        table = tree.xpath('//div[contains(@class, "current-petitions")]')
        if len(table) != 1:
            raise ValueError("Found other than 1 table in html.")

        rows = table[0].xpath('div[contains(@class,"petitions-listing")]')
        for row in rows:
            title = row.xpath(".//a/text()")[0].strip()
            closed_date = (
                row.xpath('.//span[@class="petitions-listing__subtext"]/text()')[0]
                .split(":")[-1]
                .strip()
            )
            view_url = row.xpath(".//a/@href")[0].strip()
            signatures = (
                row.xpath(
                    './/span[@class="petitions-listing__signatures-highlight"]/text()'
                )[0]
                .strip()
                .replace("Signatures", "")
                .replace("Signature", "")
                .replace(",", "")
            )
            ref_id = view_url.split("=")[-1]
            item = {
                "ref_id": ref_id,
                "title": title,
                "view_url": url_base + view_url,
                "signatures": int(signatures),
                "closed_at": self._normalise.parse_date(closed_date, self._tz),
            }
            yield item

    def get_petition(self, data: dict):
        url = data.get("view_url")
        r = self._http_client.get(url)
        tree = html.fromstring(r.text)

        if tree is None:
            raise ValueError("No html available.")

        table = tree.xpath('//div[@class="petition-details"]')
        if len(table) != 1:
            raise ValueError("Found other than 1 table in html.")

        details = table[0]
        title = details.xpath("./h3/text()")[0].strip()
        eligibility = (
            details.xpath('.//span[@class="petition-details__elegibility"]/text()')[0]
            .replace("Eligibility - ", "")
            .strip()
        )
        principal = details.xpath(
            './/div[@class="petition-details__petitioner-details-wrapper"]//text()'
        )
        principal = ", ".join([i.strip() for i in principal if i.strip()])
        signatures = (
            " ".join(
                details.xpath('.//div[@class="petition-details__signatures"]//text()')
            )
            .replace("Total Signatures", "")
            .replace(",", "")
            .replace("-", "")
            .strip()
        )
        body = ", ".join(
            [
                i.strip()
                for i in details.xpath(
                    './/div[@class="petition-details__content--body"]//text()'
                )
                if i.strip()
            ]
        ).strip()

        sponsor = None
        posted_date = None
        closing_date = None

        props = details.xpath('.//div[@class="petition-details__prop"]')
        for prop in props:
            prop_text = " ".join([i.strip() for i in prop.xpath(".//text()")]).strip()
            if prop_text.startswith("Sponsoring Member:"):
                sponsor = prop_text[18:].strip()
            if prop_text.startswith("Posting Date:"):
                posted_date = prop_text[13:].strip()
            if prop_text.startswith("Closing Date:"):
                closing_date = prop_text[13:].strip()

        item = {
            "title": title,
            "body": body,
            "eligibility": eligibility,
            "principal": principal,
            "signatures": int(signatures),
            "sponsor": sponsor,
            "posted_date": self._normalise.parse_date(posted_date, self._tz),
            "closing_date": self._normalise.parse_date(closing_date, self._tz),
        }
        return item
