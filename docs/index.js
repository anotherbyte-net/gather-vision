URLS=[
"gather_vision/index.html",
"gather_vision/app.html",
"gather_vision/cli.html",
"gather_vision/model.html",
"gather_vision/plugin.html",
"gather_vision/utils.html"
];
INDEX=[
{
"ref":"gather_vision",
"url":0,
"doc":"Documentation for the gather vision package.  gather-vision Obtain, extract, organise, and store information.  Install Install from PyPI using pip:   pip install gather-vision   [![PyPI](https: img.shields.io/pypi/v/gather-vision)](https: pypi.org/project/gather-vision/) ![PyPI - Python Version](https: img.shields.io/pypi/pyversions/gather-vision) [![GitHub Workflow Status (branch)](https: img.shields.io/github/workflow/status/anotherbyte-net/gather-vision/Test%20Package/main)](https: github.com/anotherbyte-net/gather-vision/actions)  Change log  [v0.0.2](https: github.com/anotherbyte-net/gather-vision/compare/v0.0.1 .v0.0.2) - Added WebData base class - Changed CI to run via tox and not release to PyPI  [v0.0.1](https: github.com/anotherbyte-net/gather-vision/commits/v0.0.1) - Created initial plugin implementation using [entry points](https: setuptools.pypa.io/en/latest/userguide/entry_point.html entry-points-for-plugins) - Created basic cli using argparse - Created initial tests"
},
{
"ref":"gather_vision.app",
"url":1,
"doc":"The main application features."
},
{
"ref":"gather_vision.app.App",
"url":1,
"doc":"The main application."
},
{
"ref":"gather_vision.app.App.group",
"url":1,
"doc":""
},
{
"ref":"gather_vision.app.App.entry_points",
"url":1,
"doc":""
},
{
"ref":"gather_vision.app.App.plugins",
"url":1,
"doc":""
},
{
"ref":"gather_vision.app.App.collect",
"url":1,
"doc":"Collect the available plugins. Returns: A collection of EntryPoints.",
"func":1
},
{
"ref":"gather_vision.app.App.load",
"url":1,
"doc":"Load the plugin class for each plugin. Returns: A list of",
"func":1
},
{
"ref":"gather_vision.app.App.get",
"url":1,
"doc":"Get the class for a plugin. Args: name: The name of the plugin. Returns: The plugin entry class.",
"func":1
},
{
"ref":"gather_vision.app.App.update",
"url":1,
"doc":"Execute the update action for the plugin with the given name. Args: args: The update arguments. Returns: The result of running the plugin's update process.",
"func":1
},
{
"ref":"gather_vision.app.App.list",
"url":1,
"doc":"List all available plugins. Args: args: The list arguments. Returns: A list of plugins.",
"func":1
},
{
"ref":"gather_vision.cli",
"url":2,
"doc":"Command line for gather vision."
},
{
"ref":"gather_vision.cli.cli_update",
"url":2,
"doc":"Run the update action from the cli. Args: args: The arguments for the update action. Returns: True if there were no errors.",
"func":1
},
{
"ref":"gather_vision.cli.cli_list",
"url":2,
"doc":"Run the list action from the cli. Args: args: The arguments for the list action. Returns: True if there were no errors.",
"func":1
},
{
"ref":"gather_vision.cli.main",
"url":2,
"doc":"Run as a command line program. Args: args: The program arguments. Returns: int: Program exit code.",
"func":1
},
{
"ref":"gather_vision.model",
"url":3,
"doc":"Models used by other modules."
},
{
"ref":"gather_vision.model.UpdateArgs",
"url":3,
"doc":"The arguments for the update command."
},
{
"ref":"gather_vision.model.UpdateArgs.name",
"url":3,
"doc":"The action name."
},
{
"ref":"gather_vision.model.UpdateArgs.data_source",
"url":3,
"doc":"The plugin data source name."
},
{
"ref":"gather_vision.model.UpdateResult",
"url":3,
"doc":"The result from the update command."
},
{
"ref":"gather_vision.model.ListArgs",
"url":3,
"doc":"The arguments for the list command."
},
{
"ref":"gather_vision.model.ListArgs.name",
"url":3,
"doc":"The plugin name."
},
{
"ref":"gather_vision.model.ListArgs.data_source",
"url":3,
"doc":"The plugin data source name."
},
{
"ref":"gather_vision.model.ListResult",
"url":3,
"doc":"The result from the list command."
},
{
"ref":"gather_vision.model.ListResult.items",
"url":3,
"doc":"The map of plugin name and data sources."
},
{
"ref":"gather_vision.model.WebDataAvailable",
"url":3,
"doc":"The web data available for providing new urls and/or items."
},
{
"ref":"gather_vision.model.WebDataAvailable.request_url",
"url":3,
"doc":"The requested url."
},
{
"ref":"gather_vision.model.WebDataAvailable.request_method",
"url":3,
"doc":"The method used for the request."
},
{
"ref":"gather_vision.model.WebDataAvailable.response_url",
"url":3,
"doc":"The url that provided the response."
},
{
"ref":"gather_vision.model.WebDataAvailable.body_text",
"url":3,
"doc":"The raw response body text."
},
{
"ref":"gather_vision.model.WebDataAvailable.body_data",
"url":3,
"doc":"The structure body data from json or xml."
},
{
"ref":"gather_vision.model.WebDataAvailable.selector",
"url":3,
"doc":"The selector for obtaining parts of the body data."
},
{
"ref":"gather_vision.model.WebDataAvailable.status",
"url":3,
"doc":"The response status code."
},
{
"ref":"gather_vision.model.WebDataAvailable.headers",
"url":3,
"doc":"The response headers."
},
{
"ref":"gather_vision.model.WebDataAvailable.meta",
"url":3,
"doc":"The metadata associated with the request and response."
},
{
"ref":"gather_vision.model.IsDataclass",
"url":3,
"doc":"Allows specifying type to be any dataclass."
},
{
"ref":"gather_vision.model.WebData",
"url":3,
"doc":"A class that retrieves web data and converts it into more urls and/or items."
},
{
"ref":"gather_vision.model.WebData.initial_urls",
"url":3,
"doc":"Get the initial urls. Returns: A stream of string items.",
"func":1
},
{
"ref":"gather_vision.model.WebData.parse_response",
"url":3,
"doc":"Parse a web response and provide urls and items. Args: data: The web data available for parsing. Returns: Yield urls and/or items from the web data.",
"func":1
},
{
"ref":"gather_vision.plugin",
"url":4,
"doc":"Available to plugins."
},
{
"ref":"gather_vision.plugin.Entry",
"url":4,
"doc":"The entry point class for plugins. Compatible plugins must implement this class."
},
{
"ref":"gather_vision.plugin.Entry.update",
"url":4,
"doc":"Update the data sources that match the args. Args: args: The arguments for update. Returns: The result of the update action.",
"func":1
},
{
"ref":"gather_vision.plugin.Entry.list",
"url":4,
"doc":"List the plugins and data sources that match the args. Args: args: The arguments for list. Returns: The result of the list action.",
"func":1
},
{
"ref":"gather_vision.utils",
"url":5,
"doc":"Small utility functions."
},
{
"ref":"gather_vision.utils.get_name_dash",
"url":5,
"doc":"Get the package name with word separated by dashes.",
"func":1
},
{
"ref":"gather_vision.utils.get_name_under",
"url":5,
"doc":"Get the package name with word separated by underscores.",
"func":1
},
{
"ref":"gather_vision.utils.get_version",
"url":5,
"doc":"Get the package version.",
"func":1
},
{
"ref":"gather_vision.utils.validate",
"url":5,
"doc":"Validate that a value is one of the expected values.",
"func":1
},
{
"ref":"gather_vision.utils.validate_path",
"url":5,
"doc":"Validate a path.",
"func":1
},
{
"ref":"gather_vision.utils.GatherVisionException",
"url":5,
"doc":"A gather vision error."
}
]