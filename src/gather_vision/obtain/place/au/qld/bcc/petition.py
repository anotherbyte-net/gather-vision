import dataclasses
from datetime import datetime, timezone
import typing

from gather_vision.obtain.core import data


@dataclasses.dataclass(frozen=True)
class BrisbaneCityCouncilPetitionItem(data.GatherDataItem):
    view_url: str
    sign_url: str
    title: str
    reference_id: str
    principal: str
    body: str
    signatures: str
    retrieved_at: datetime
    closed_at: datetime


class BrisbaneCityCouncilPetitionsWebData(data.WebData):
    @property
    def name(self):
        return "au-qld-bcc-petitions"

    @property
    def tags(self) -> dict[str, str]:
        return {
            "country": "Australia",
            "region": "Queensland",
            "district": "Brisbane City Council",
            "locality": "City of Brisbane",
            "data_source_location": "web",
            "data_source_category": "petition",
        }

    list_url = "https://www.epetitions.brisbane.qld.gov.au"
    archive_url = f"{list_url}/petition/archives"
    item_url = f"{list_url}/petition/view/pid"
    signed_url = f"{list_url}/petition/signatures/pid"
    sign_url = f"{list_url}/petition/sign/pid"
    closed_fmt = "%a, %d %b %Y"

    def initial_urls(self) -> typing.Iterable[str]:
        # TODO: add archived petitions?
        return [self.list_url]

    def web_resources(
        self, web_data: data.WebDataAvailable
    ) -> typing.Iterable[typing.Union[data.GatherDataRequest, data.GatherDataItem]]:
        url = web_data.response_url.strip("/")
        if url in [self.list_url, self.archive_url]:
            for raw in self._parse_petitions_table(web_data):
                yield data.GatherDataRequest(
                    url=f"{self.item_url}/{raw.get('item_id')}",
                    data=raw,
                )

        elif url.startswith(self.item_url):
            raw = self._parse_petition(web_data)
            yield BrisbaneCityCouncilPetitionItem(
                gather_name=self.name,
                tags=self.tags,
                view_url=raw.get("view_url"),
                sign_url=raw.get("sign_url"),
                title=raw.get("title"),
                reference_id=raw.get("reference_id"),
                principal=raw.get("principal"),
                body=raw.get("body"),
                signatures=raw.get("signatures"),
                retrieved_at=raw.get("retrieved_at"),
                closed_at=raw.get("closed_at"),
            )

        elif url.startswith(self.signed_url):
            # TODO: consider gathering the signature suburbs?
            yield None

        elif url.startswith(self.sign_url):
            yield None

        else:
            raise ValueError(f"Unexpected url '{url}'.")

    def _parse_petitions_table(self, web_data: data.WebDataAvailable):
        for table_petition in web_data.selector.css("table.petitions"):
            for table_row in table_petition.css("tr"):
                table_cells = table_row.css("td")
                if len(table_cells) < 3:
                    continue
                title = table_cells[0].css("::text").get()
                item_id = table_cells[0].css("a").attrib.get("href").split("/")[-1]
                principal = table_cells[1].css("::text").get()
                closed_raw = table_cells[2].css("::text").get()

                yield {
                    "title": title,
                    "item_id": item_id,
                    "principal": principal,
                    "closed_at": datetime.strptime(closed_raw, self.closed_fmt),
                }

    def _parse_petition(self, web_data: data.WebDataAvailable):
        meta = web_data.meta
        title = meta.get("title")
        title_len = len(title)
        item_id = meta.get("item_id")
        principal = meta.get("principal")
        principal_len = len(principal)
        closed_at = meta.get("closed_at")

        s = web_data.selector
        title_item = s.css(".page-title h1::text").get()
        if len(title_item) > title_len:
            title = title_item
        content_raw = s.css("#petition-details ::text").getall()
        content = self.str_collapse("\n".join(content_raw))
        view_url = web_data.response_url.strip("/")
        sign_url = f"{self.sign_url}/{item_id}"

        signatures: typing.Optional[int] = None
        for table_index, table_row in enumerate(s.css(".petition-details tr")):
            table_cells = table_row.css("td")
            data_key = table_cells[0].css("::text").get().strip().lower()
            data_value = table_cells[1].css("::text").get().strip()

            if table_index == 0 and "principal" in data_key:
                if len(data_value) > principal_len:
                    principal = data_value

            elif table_index == 1 and "date" in data_key:
                closed_at_item = datetime.strptime(data_value, self.closed_fmt)
                if closed_at_item > closed_at:
                    closed_at = closed_at_item

            elif table_index == 2 and "signature" in data_key:
                signatures = int(data_value.split("signature")[0].strip())

            else:
                raise ValueError(f"Unexpected table row '{data_key}': '{data_value}'.")

        return {
            "view_url": view_url,
            "sign_url": sign_url,
            "title": title,
            "reference_id": item_id,
            "principal": principal,
            "body": content,
            "signatures": signatures,
            "retrieved_at": datetime.now(timezone.utc),
            "closed_at": closed_at,
        }
