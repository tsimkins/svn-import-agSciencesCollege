from Products.PythonScripts.Utility import allow_module
from Products.CMFCore.DirectoryView import registerDirectory

allow_module('collective.tagmanager')

GLOBALS = globals()
registerDirectory('skins', GLOBALS)

def initialize(context):
    """Initializer called when used as a Zope 2 product."""

def outputConfig(configOptions):
    """Called from the javascript Ready() function and used to
       process the configuration settings making javascript
       function calls as necessary.
       """
    final_config = []
    for key in configOptions[1]:
        final_config.append('categoryList = addTagCategory("%s")' % key)
        for item in configOptions[0][key]:
            final_config.append('manageTags(categoryList, "%s", "%s")' % tuple(item));
    
    return ("\n"+" "*8).join(final_config)