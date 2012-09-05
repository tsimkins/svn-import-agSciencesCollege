#!/usr/bin/python

from collective.tagmanager import outputConfig

config = {
    'Administrative' : [
        ['campus', 'Campus Designation'],
        ['findfacility', 'Facility Capabilities'],
        ['faq', 'FAQ Sections'],
        ['admin', 'Miscellaneous'],
    ],
    'For Content Providers' : [
        ['events', 'Events'],
        ['spotlight', 'Highlight/Promote'],
        ['research', 'Institutes'],
        ['center', 'Centers of Excellence'],
        ['gradprg', 'Graduate Programs'],
        ['facility', 'Shared Instrumentation Facilities'],
    ],
}

keyOrder = config.keys()
keyOrder.sort()
keyOrder.reverse()

return outputConfig( (config, keyOrder) )