from datetime import datetime
from zoneinfo import ZoneInfo

from django.utils import timezone

from gather_vision import models as app_models
from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise
from gather_vision.process.item.water_quality_measure import WaterQualityMeasure
from gather_vision.process.service.water_quality.au_qld_bcc_waterways import (
    AuQldBccWaterways,
)


class WaterQuality:
    def __init__(self, logger: Logger, tz: ZoneInfo, http_client: HttpClient):
        normalise = Normalise()

        self._logger = logger
        self._http_client = http_client
        self._normalise = normalise
        self._tz = tz

    def run_update(self):
        self._logger.info("Updating water quality measures.")

        retrieved_date = timezone.now()

        source, source_created = self.create_au_qld_bcc_waterways()
        bcc_ww = AuQldBccWaterways(
            self._logger,
            self._http_client,
            self._normalise,
            self._tz,
        )

        count_seen = 0
        count_created = 0
        count_updated = 0

        measurements = bcc_ww.update_measurements()
        for measurement in measurements:
            obj, created = self.update_measurements(retrieved_date, source, measurement)

            count_seen += 1
            if created:
                count_created += 1
            else:
                count_updated += 1

            if count_seen % 100 == 0:
                self._logger.info(
                    f"Running total measurements {count_seen} "
                    f"({count_updated} updated, {count_created} created)."
                )

        self._logger.info(
            f"Measurements {count_seen} "
            f"({count_updated} updated, {count_created} created)."
        )
        self._logger.info("Finished updating water quality measures.")

    def create_au_qld_bcc_waterways(self):
        (obj, created) = app_models.InformationSource.objects.aget_or_create(
            name=AuQldBccWaterways.code,
            defaults={
                "title": AuQldBccWaterways.title,
                "info_url": AuQldBccWaterways.page_url,
            },
        )
        return obj, created

    def update_measurements(
        self,
        retrieved_date: datetime,
        source: app_models.InformationSource,
        item: WaterQualityMeasure,
    ):
        site, site_created = app_models.WaterQualitySite.objects.update_or_create(
            source=source,
            code=str(item.site_number),
            title=item.site_name,
            latitude=item.location_latitude,
            longitude=item.location_longitude,
            defaults={
                "description": item.location_description,
            },
        )

        sample, sample_created = app_models.WaterQualitySample.objects.update_or_create(
            site=site,
            sample_date=item.observation_date,
            sample_value=item.observation_value,
            sample_status=item.observation_status,
            defaults={
                "retrieved_date": retrieved_date,
            },
        )

        return sample, sample_created
