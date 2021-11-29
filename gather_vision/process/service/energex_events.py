from datetime import tzinfo

from gather_vision.process.component.html_extract import HtmlExtract
from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise


class EnergexEvents:
    code = "energex"

    base_url = "https://www.energex.com.au"
    api_url = f"{base_url}/api/outages/v0.3"
    usage_url = f"{base_url}/static/Energex/Network%20Demand/networkdemand.txt"
    outage_summary_url = f"{api_url}/summary"
    outage_councils_url = f"{api_url}/council?council="
    outage_suburbs_url = f"{api_url}/suburb?council=&suburb="
    outage_council_suburbs_url = f"{api_url}/suburb?council={{}}&suburb="
    outage_suburb_url = f"{api_url}/search?suburb={{}}"

    def __init__(
        self,
        logger: Logger,
        http_client: HttpClient,
        normalise: Normalise,
        html_extract: HtmlExtract,
        tz: tzinfo,
    ):
        self._logger = logger
        self._http_client = http_client
        self._normalise = normalise
        self._html_extract = html_extract
        self._tz = tz

    # TODO
    # def run(self):
    #     current_time = datetime.today()
    #
    #     demand = {
    #         "demand": None,
    #         "rating": None,
    #         "retrieved_at": current_time.strftime(self.iso_datetime_format),
    #     }
    #     summary = {
    #         "retrieved_at": current_time.strftime(self.iso_datetime_format),
    #         "updated_at": None,
    #         "total_cust": None,
    #     }
    #     data = []
    #
    #     self._logger.info("Reading usage")
    #     usage_page = self.download_text(self.usage_url)
    #     demand["demand"] = usage_page
    #     demand["rating"] = self.demand_rating(usage_page)
    #
    #     self._logger.info("Reading outage summary")
    #     outage_summary_page = self.download_json(self.outage_summary_url)
    #     total_cust = outage_summary_page["data"]["totalCustomersAffected"]
    #     updated_at = datetime.strptime(
    #         outage_summary_page["data"]["lastUpdated"], "%d %B %Y %I:%M %p"
    #     ).strftime(self.iso_datetime_format)
    #     summary["total_cust"] = total_cust
    #     summary["updated_at"] = updated_at
    #
    #     self._logger.info("Reading Councils list")
    #     outage_councils_page = self.download_json(self.outage_councils_url)
    #     outage_councils = outage_councils_page["data"]
    #
    #     self._logger.info("Reading Suburbs list")
    #     outage_suburbs_page = self.download_json(self.outage_suburbs_url)
    #     outage_suburbs = outage_suburbs_page["data"]
    #
    #     for council in outage_councils:
    #         outage_council_suburbs_page = self.download_json(
    #             self.outage_council_suburbs_url.format(council["name"])
    #         )
    #         suburbs = outage_council_suburbs_page["data"]
    #
    #         for suburb in suburbs:
    #             outage_suburb_page = self.download_json(
    #                 self.outage_suburb_url.format(suburb["name"])
    #             )
    #             events = outage_suburb_page["data"]
    #
    #             for event in events:
    #                 data.append(
    #                     {
    #                         "event_name": event["event"].lower(),
    #                         "council": event["council"].title(),
    #                         "suburb": event["suburb"].title(),
    #                         "post_code": event["postcode"],
    #                         "cust": event["customersAffected"],
    #                         "cause": event["cause"],
    #                         "restore_at": datetime.strptime(
    #                             event["restoreTime"].replace(":", ""),
    #                             "%Y-%m-%dT%H%M%S%z",
    #                         ).strftime(self.iso_datetime_format),
    #                         "streets": str.join(
    #                             ",", sorted(s.title() for s in event["streets"])
    #                         ),
    #                         "retrieved_at": current_time.strftime(
    #                             self.iso_datetime_format
    #                         ),
    #                     }
    #                 )
    #
    #     self._logger.info("")
    #
    #     # insert data
    #     self._logger.info(
    #         "Adding demand {} with rating {}"
    #         .format(demand["demand"], demand["rating"])
    #     )
    #     self.sqlite_demand_row_insert(db_conn, demand)
    #
    #     self._logger.info(
    #         "Adding summary customers affected {} last updated {}".format(
    #             summary["total_cust"], summary["updated_at"]
    #         )
    #     )
    #     self.sqlite_summary_row_insert(db_conn, summary)
    #
    #     self._logger.info("")
    #     count_added = 0
    #     count_skipped = 0
    #     for item in data:
    #         row_exists = self.sqlite_data_row_exists(db_conn, item)
    #         if row_exists:
    #             self._logger.info(
    #                 "Already exists with same data {}: {}, {} - {} due to {}".format(
    #                     item["event_name"],
    #                     item["council"],
    #                     item["suburb"],
    #                     item["cust"],
    #                     item["cause"],
    #                 )
    #             )
    #             count_skipped += 1
    #         else:
    #             self._logger.info(
    #                 "Adding outage {}: {}, {} - {} due to {}".format(
    #                     item["event_name"],
    #                     item["council"],
    #                     item["suburb"],
    #                     item["cust"],
    #                     item["cause"],
    #                 )
    #             )
    #             self.sqlite_data_row_insert(db_conn, item)
    #             count_added += 1
    #
    #     self._logger.info(
    #         "Added {}, skipped {}, total {}".format(
    #             count_added, count_skipped, count_added + count_skipped
    #         )
    #     )
    #     self._logger.info("Completed successfully.")
    #
    # def demand_rating(self, demand: str):
    #     demand = int(demand)
    #
    #     # demand min: 0, demand max: 5500
    #     # found in:
    # https://www.energex.com.au/__data/assets/js_file_folder/0011/653996/main.js?version=0.3.59
    #
    #     # divided into 4 equal parts: low, moderate, high, extreme
    #     # then into 3 parts = approx 458.3 per smallest part
    #     # demand_min = 0
    #     demand_max = 5500
    #     rating_min = 1
    #     rating_max = 12
    #
    #     demand_part = demand_max / 4 / 3
    #     rating = int(demand / demand_part)
    #
    #     if rating < rating_min:
    #         rating = rating_min
    #
    #     if rating > rating_max:
    #         rating = rating_max
    #
    #     return rating
