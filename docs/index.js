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
"doc":"Documentation for the leaf focus package.  gather-vision Obtain, extract, organise, and store information.  Install Install from PyPI using pip:   pip install gather-vision   [![PyPI](https: img.shields.io/pypi/v/gather-vision)](https: pypi.org/project/gather-vision/) ![PyPI - Python Version](https: img.shields.io/pypi/pyversions/gather-vision) ![GitHub Workflow Status (branch)](https: img.shields.io/github/workflow/status/anotherbyte-net/gather-vision/Create%20Package/main)  Change log  unreleased "
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
"ref":"gather_vision.app.App.show",
"url":1,
"doc":"Execute the show action for the plugin with the given name. Args: args: The show arguments. Returns: The details of the plugin.",
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
"ref":"gather_vision.cli.cli_show",
"url":2,
"doc":"Run the show action from the cli. Args: args: The arguments for the show action. Returns: True if there were no errors.",
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
"doc":""
},
{
"ref":"gather_vision.model.UpdateResult",
"url":3,
"doc":"The result from the update command."
},
{
"ref":"gather_vision.model.ShowArgs",
"url":3,
"doc":"The arguments for the show command."
},
{
"ref":"gather_vision.model.ShowArgs.name",
"url":3,
"doc":""
},
{
"ref":"gather_vision.model.ShowResult",
"url":3,
"doc":"The result from the show command."
},
{
"ref":"gather_vision.model.ListArgs",
"url":3,
"doc":"The arguments for the list command."
},
{
"ref":"gather_vision.model.ListResult",
"url":3,
"doc":"The result from the list command."
},
{
"ref":"gather_vision.model.ListResult.names",
"url":3,
"doc":""
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
"doc":"Run the update action. Args: args: The arguments for update. Returns: The result of the update action.",
"func":1
},
{
"ref":"gather_vision.plugin.Entry.show",
"url":4,
"doc":"Run the show action. Args: args: The arguments for show. Returns: The result of the show action.",
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