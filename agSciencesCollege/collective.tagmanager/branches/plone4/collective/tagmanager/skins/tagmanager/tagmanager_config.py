#!/usr/bin/python

from collective.tagmanager import outputConfig

config = {
    'Administrative' : [
        ['county', 'Counties'],
        ['main', 'Topics'],
        ['front', 'Front Page'],
        ['department', 'Departments'],
        ['spotlight', 'Spotlight'],
    ],
    'Programs' : [
        ['disaster', 'Disaster'],
        ['diabetes', 'Dining With Diabetes'],
        ['energy', 'Energy'],    
        ['farmbusiness', 'Farm Business'],    
        ['green', 'Green Industry'],
        ['naturalgas', 'Natural Gas'],
        ['food-safety', 'Food Safety'],
        ['field-crop-news', 'Field Crop News'],
        ['wildlife', 'Wildlife'],
        ['agronomy-guide', 'Agronomy Guide'],
        ['backyard-composting', 'Backyard Composting'],
        ['cmeg', 'Crop Management Extension Group'],
        ['consumers', 'Consumer Issues'],
        ['dhia', 'Dairy Record Analysis Training'],
        ['ecd', 'Economic and Community Development'],
        ['edata', 'Extension Data System (e-data)'],
        ['income-tax', 'Your Money Your Taxes'],
        ['kinship', 'PA Kinship Navigator'],
        ['late-blight', 'Late Blight'],
        ['leadership', 'Learning Today, Leading Tomorrow'],
        ['moneywise', 'Moneywise'],
        ['nutrient-management', 'Nutrient Management'],
        ['on-farm', 'On-Farm Research'],
        ['pa-pipe', 'PA PIPE'],
        ['paforeststewards', 'PA Forest Stewards'],
        ['parenting', 'Parenting'],
        ['private-forests', 'Private Forests'],
        ['readyag', 'ReadyAg'],
        ['small-grains', 'Small Grains'],
        ['start-farming', 'Start Farming'],
        ['timber-market-report', 'Timber Market Report'],
        ['vegetable-fruit', 'Vegetable and Small Fruit Production'],
        ['water', 'Water Resources'],
        ['weeds', 'Weed Management'],
    ],
}

return outputConfig(config)
