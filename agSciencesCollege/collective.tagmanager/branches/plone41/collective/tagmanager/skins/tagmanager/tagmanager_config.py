#!/usr/bin/python

from collective.tagmanager import outputConfig

config = {
    'Administrative' : [
        ['county', 'Counties'],
        ['main', 'Topics'],
        ['front', 'Front Page'],
        ['department', 'Departments'],
    ],
    'Programs' : [
        ['disaster', 'Disaster'],
        ['diabetes', 'Dining With Diabetes'],
        ['energy', 'Energy'],    
        ['farmbusiness', 'Farm Business'],    
        ['green', 'Green Industry'],
        ['naturalgas', 'Natural Gas'],
    ],
}

return outputConfig(config)