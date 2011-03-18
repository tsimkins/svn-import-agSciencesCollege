from Products.PythonScripts.Utility import allow_module
from Products.CMFCore.DirectoryView import registerDirectory

allow_module('collective.tagmanager')

GLOBALS = globals()
registerDirectory('skins', GLOBALS)

def initialize(context):
    """Initializer called when used as a Zope 2 product."""

def outputConfig(config):
    final_config = ['']
    config_keys = config.keys()
    config_keys.sort()
    
    for key in config_keys:
    
        final_config.append('categoryList = addTagCategory("%s")' % key)
    
        items = config[key]
        items.sort()
        
        for item in items:
            final_config.append('manageTags(categoryList, "%s", "%s")' % tuple(item));
    
    return ("\n"+" "*8).join(final_config)