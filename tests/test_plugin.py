from gather_vision import app
from gather_vision.plugin import entry

from gather_vision_gov_au_plugin.plugin import PluginEntry


def test_list(capsys, caplog):
    app_args = entry.ListArgs()
    main_app = app.App()
    result = main_app.list(app_args)
    assert result == entry.ListResult(
        items={
            PluginEntry.name: [
                "air.queensland.QueenslandAir",
                "election.australia.AustraliaElection",
                "electricity.queensland_energex.QueenslandEnergexElectricity",
                "electricity.queensland_ergon_energy.QueenslandErgonEnergyElectricity",
                "petition.australia.AustralianGovernmentPetitions",
                "petition.queensland.QueenslandGovernmentPetitions",
                "petition.queensland_brisbane.BrisbaneCityCouncilPetitions",
                "transport.queensland_fuel.QueenslandFuel",
            ]
        }
    )

    stdout, stderr = capsys.readouterr()
    assert stdout == ""
    assert stderr == ""
    assert caplog.record_tuples == [
        ("gather_vision.app", 20, "Loaded 1 plugins."),
        ("gather_vision_gov_au_plugin.plugin", 20, "List gov_au"),
    ]


def test_update(capsys, caplog):
    app_args = entry.UpdateArgs(name=PluginEntry.name)
    main_app = app.App()
    result = main_app.update(app_args)
    assert not result.local_data == entry.UpdateResult(web_data=[], local_data=[])
    assert len(result.web_data) == 8
    assert not result.web_data[0].data

    stdout, stderr = capsys.readouterr()
    assert stdout == ""
    assert (
        "AttributeError: 'QueenslandAir' object has no attribute 'list_url'" in stderr
    )
    assert len(caplog.record_tuples) == 20
    assert (
        "gather_vision_gov_au_plugin.plugin",
        20,
        "Update gov_au",
    ) in caplog.record_tuples
