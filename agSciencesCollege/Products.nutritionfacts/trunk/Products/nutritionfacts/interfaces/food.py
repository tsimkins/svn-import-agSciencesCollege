from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from Products.nutritionfacts import nutritionfactsMessageFactory as _

class IFood(Interface):
    """Information about a Food"""
    
    # -*- schema definition goes here -*-

    food_type = schema.List(
        title=_(u"Food Type(s)"), 
        required=True,
        description=_(u""),
    )
    
    serving_size = schema.Float(
        title=_(u"Serving Size"), 
        required=True,
        description=_(u""),
    )
    
    serving_size_units = schema.TextLine(
        title=_(u"Serving Size Units"), 
        required=True,
        description=_(u""),
    )

    serving_weight = schema.Float(
        title=_(u"Serving Weight"), 
        required=True,
        description=_(u""),
    )

    servings_per_container = schema.Float(
        title=_(u"Servings Per Container"), 
        required=True,
        description=_(u""),
    )

    calories = schema.Int(
        title=_(u"Calories"), 
        required=True,
        description=_(u""),
    )
    
    fat_calories = schema.Int(
        title=_(u"Fat Calories"), 
        required=True,
        description=_(u""),
    )

    total_fat = schema.Float(
        title=_(u"Total Fat"), 
        required=True,
        description=_(u""),
    )

    saturated_fat = schema.Float(
        title=_(u"Saturated Fat"), 
        required=True,
        description=_(u""),
    )

    trans_fat = schema.Float(
        title=_(u"Trans Fat"), 
        required=True,
        description=_(u""),
    )

    cholesterol = schema.Float(
        title=_(u"Cholesterol"), 
        required=True,
        description=_(u""),
    )

    sodium = schema.Float(
        title=_(u"Sodium"), 
        required=True,
        description=_(u""),
    )

    total_carbohydrate = schema.Float(
        title=_(u"Total Carbohydrate"), 
        required=True,
        description=_(u""),
    )

    dietary_fiber = schema.Float(
        title=_(u"Dietary Fiber"), 
        required=True,
        description=_(u""),
    )

    sugars = schema.Float(
        title=_(u"Sugars"), 
        required=True,
        description=_(u""),
    )

    protein = schema.Float(
        title=_(u"Protein"), 
        required=True,
        description=_(u""),
    )

    vitamin_a = schema.Float(
        title=_(u"Vitamin A"), 
        required=True,
        description=_(u""),
    )

    vitamin_c = schema.Float(
        title=_(u"Vitamin C"), 
        required=True,
        description=_(u""),
    )

    calcium = schema.Float(
        title=_(u"Calcium"), 
        required=True,
        description=_(u""),
    )

    iron = schema.Float(
        title=_(u"Iron"), 
        required=True,
        description=_(u""),
    )

    vitamin_d = schema.Float(
        title=_(u"Vitamin D"), 
        required=True,
        description=_(u""),
    )
###

    ingredients = schema.List(
        title=_(u"Ingredients"), 
        required=True,
        description=_(u""),
    )

    body_text = schema.Text(
        title=_(u"Body Text"), 
        required=False,
        description=_(u"Field description"),
    )

