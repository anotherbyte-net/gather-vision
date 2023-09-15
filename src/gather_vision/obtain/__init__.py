from gather_vision.obtain.au.qld.bcc.government import (
    BrisbaneCityCouncilGovernmentPersonItem,
    BrisbaneCityCouncilGovernmentSittingDateItem,
    BrisbaneCityCouncilGovernmentMeetingPersonAttendanceItem,
    BrisbaneCityCouncilGovernmentMeetingVoteItem,
    BrisbaneCityCouncilGovernmentWebData,
)
from gather_vision.obtain.au.qld.bcc.petition import (
    BrisbaneCityCouncilPetitionItem,
    BrisbaneCityCouncilPetitionsWebData,
)
from gather_vision.obtain.au.qld.bcc.transport import BrisbaneTranslinkNoticesWebData
from gather_vision.obtain.au.qld.bcc.water import (
    BrisbaneCityCouncilWaterQualityItem,
    BrisbaneCityCouncilWaterLevelItem,
    BrisbaneCityCouncilWaterWebData,
)
from gather_vision.obtain.au.qld.air import QueenslandAirItem, QueenslandAirWebData
from gather_vision.obtain.au.qld.electricity import (
    QueenslandEnergexElectricityItem,
    QueenslandEnergexElectricityWebData,
    QueenslandErgonEnergyElectricityItem,
    QueenslandErgonEnergyElectricityWebData,
)
from gather_vision.obtain.au.qld.petition import (
    QueenslandGovernmentPetitionItem,
    QueenslandGovernmentPetitionsWebData,
)
from gather_vision.obtain.au.qld.transport import (
    QueenslandFuelItem,
    QueenslandFuelWebData,
    QueenslandRailEvents,
)
from gather_vision.obtain.au.election import (
    AustraliaElectionItem,
    AustraliaElectionWebData,
)
from gather_vision.obtain.au.petition import (
    AustralianGovernmentPetitionItem,
    AustralianGovernmentPetitionsWebData,
)

# all
available_web_data = [
    BrisbaneCityCouncilGovernmentWebData(),
    BrisbaneCityCouncilPetitionsWebData(),
    BrisbaneTranslinkNoticesWebData(),
    BrisbaneCityCouncilWaterWebData(),
    QueenslandAirWebData(),
    QueenslandEnergexElectricityWebData(),
    QueenslandErgonEnergyElectricityWebData(),
    QueenslandGovernmentPetitionsWebData(),
    QueenslandFuelWebData(),
    AustraliaElectionWebData(),
    AustralianGovernmentPetitionsWebData(),
]
