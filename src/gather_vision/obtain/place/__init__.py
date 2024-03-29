from gather_vision.obtain.place.au.qld.bcc.government import (
    BrisbaneCityCouncilGovernmentPersonItem,
    BrisbaneCityCouncilGovernmentSittingDateItem,
    BrisbaneCityCouncilGovernmentMeetingPersonAttendanceItem,
    BrisbaneCityCouncilGovernmentMeetingVoteItem,
    BrisbaneCityCouncilGovernmentWebData,
)
from gather_vision.obtain.place.au.qld.bcc.petition import (
    BrisbaneCityCouncilPetitionsWebData,
    BrisbaneCityCouncilPetitionItem,
)
from gather_vision.obtain.place.au.qld.bcc.transport import (
    BrisbaneTranslinkNoticesWebData,
    BrisbaneTranslinkNoticesItem,
)
from gather_vision.obtain.place.au.qld.bcc.water import (
    BrisbaneCityCouncilWaterQualityItem,
    BrisbaneCityCouncilWaterLevelItem,
    BrisbaneCityCouncilWaterWebData,
)
from gather_vision.obtain.place.au.qld.air import (
    QueenslandAirItem,
    QueenslandAirWebData,
)
from gather_vision.obtain.place.au.qld.election import (
    QueenslandGovernmentElectionsWebData,
)
from gather_vision.obtain.place.au.qld.electricity import (
    QueenslandEnergexElectricityItem,
    QueenslandEnergexElectricityWebData,
    QueenslandErgonEnergyElectricityItem,
    QueenslandErgonEnergyElectricityWebData,
)
from gather_vision.obtain.place.au.qld.petition import (
    QueenslandGovernmentPetitionItem,
    QueenslandGovernmentPetitionsWebData,
)
from gather_vision.obtain.place.au.qld.transport import (
    QueenslandFuelItem,
    QueenslandFuelWebData,
    QueenslandRailEvents,
)
from gather_vision.obtain.place.au.election import (
    AustraliaElectionItem,
    AustraliaElectionWebData,
)
from gather_vision.obtain.place.au.petition import (
    AustralianGovernmentPetitionItem,
    AustralianGovernmentPetitionsWebData,
)

# all
available_web_data = [
    BrisbaneCityCouncilGovernmentWebData,
    BrisbaneCityCouncilPetitionsWebData,
    BrisbaneTranslinkNoticesWebData,
    BrisbaneCityCouncilWaterWebData,
    QueenslandAirWebData,
    QueenslandEnergexElectricityWebData,
    QueenslandErgonEnergyElectricityWebData,
    QueenslandGovernmentElectionsWebData,
    QueenslandGovernmentPetitionsWebData,
    QueenslandFuelWebData,
    AustraliaElectionWebData,
    AustralianGovernmentPetitionsWebData,
]
available_web_items = [
    BrisbaneCityCouncilGovernmentPersonItem,
    BrisbaneCityCouncilGovernmentSittingDateItem,
    BrisbaneCityCouncilGovernmentMeetingPersonAttendanceItem,
    BrisbaneCityCouncilGovernmentMeetingVoteItem,
    BrisbaneCityCouncilPetitionItem,
    BrisbaneCityCouncilWaterQualityItem,
    BrisbaneCityCouncilWaterLevelItem,
    BrisbaneTranslinkNoticesItem,
    QueenslandAirItem,
    QueenslandEnergexElectricityItem,
    QueenslandErgonEnergyElectricityItem,
    QueenslandGovernmentPetitionItem,
    QueenslandFuelItem,
    AustraliaElectionItem,
    AustralianGovernmentPetitionItem,
]
