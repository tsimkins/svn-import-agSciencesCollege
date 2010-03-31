"""Definition of the Food content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from Products.nutritionfacts import nutritionfactsMessageFactory as _
from Products.nutritionfacts.interfaces import IFood
from Products.nutritionfacts.config import PROJECTNAME

FoodSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.LinesField(
        'food_type',
        storage=atapi.AnnotationStorage(),
        widget=atapi.LinesWidget(
            label=_(u"Food Type(s)"),
            description=_(u"one per line"),
        ),
        required=True,
    ),

    atapi.FloatField(
        'serving_size',
        storage=atapi.AnnotationStorage(),
        widget=atapi.DecimalWidget(
            label=_(u"Serving Size"),
            description=_(u""),
        ),
        required=True,
        validators=('isDecimal'),
    ),

    atapi.StringField(
        'serving_size_units',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Serving Size Units"),
            description=_(u""),
        ),
        required=True,
    ),

    atapi.FloatField(
        'serving_weight',
        storage=atapi.AnnotationStorage(),
        widget=atapi.DecimalWidget(
            label=_(u"Serving Weight"),
            description=_(u"in grams"),
        ),
        required=True,
        validators=('isDecimal'),
    ),

    atapi.FloatField(
        'servings_per_container',
        storage=atapi.AnnotationStorage(),
        widget=atapi.DecimalWidget(
            label=_(u"Servings Per Container"),
            description=_(u""),
        ),
        required=True,
        validators=('isDecimal'),
    ),

    atapi.IntegerField(
        'calories',
        storage=atapi.AnnotationStorage(),
        widget=atapi.IntegerWidget(
            label=_(u"Calories"),
            description=_(u""),
        ),
        required=True,
        validators=('isInt'),
    ),

    atapi.IntegerField(
        'fat_calories',
        storage=atapi.AnnotationStorage(),
        widget=atapi.IntegerWidget(
            label=_(u"Fat Calories"),
            description=_(u""),
        ),
        required=True,
        validators=('isInt'),
    ),

    atapi.FloatField(
        'total_fat',
        storage=atapi.AnnotationStorage(),
        widget=atapi.DecimalWidget(
            label=_(u"Total Fat"),
            description=_(u""),
        ),
        required=True,
        validators=('isDecimal'),
    ),

    atapi.FloatField(
        'saturated_fat',
        storage=atapi.AnnotationStorage(),
        widget=atapi.DecimalWidget(
            label=_(u"Saturated Fat"),
            description=_(u""),
        ),
        required=True,
        validators=('isDecimal'),
    ),

    atapi.FloatField(
        'trans_fat',
        storage=atapi.AnnotationStorage(),
        widget=atapi.DecimalWidget(
            label=_(u"Trans Fat"),
            description=_(u""),
        ),
        required=True,
        validators=('isDecimal'),
    ),

    atapi.FloatField(
        'cholesterol',
        storage=atapi.AnnotationStorage(),
        widget=atapi.DecimalWidget(
            label=_(u"Cholesterol),
            description=_(u""),
        ),
        required=True,
        validators=('isDecimal'),
    ),

    atapi.FloatField(
        'sodium',
        storage=atapi.AnnotationStorage(),
        widget=atapi.DecimalWidget(
            label=_(u"Sodium"),
            description=_(u""),
        ),
        required=True,
        validators=('isDecimal'),
    ),

    atapi.FloatField(
        'total_carbohydrate',
        storage=atapi.AnnotationStorage(),
        widget=atapi.DecimalWidget(
            label=_(u"Total Carbohydrate"),
            description=_(u""),
        ),
        required=True,
        validators=('isDecimal'),
    ),

    atapi.FloatField(
        'dietary_fiber',
        storage=atapi.AnnotationStorage(),
        widget=atapi.DecimalWidget(
            label=_(u"Dietary Fiber"),
            description=_(u""),
        ),
        required=True,
        validators=('isDecimal'),
    ),

    atapi.FloatField(
        'sugars',
        storage=atapi.AnnotationStorage(),
        widget=atapi.DecimalWidget(
            label=_(u"Sugars"),
            description=_(u""),
        ),
        required=True,
        validators=('isDecimal'),
    ),

    atapi.FloatField(
        'protein',
        storage=atapi.AnnotationStorage(),
        widget=atapi.DecimalWidget(
            label=_(u"Protein"),
            description=_(u""),
        ),
        required=True,
        validators=('isDecimal'),
    ),

    atapi.FloatField(
        'vitamin_a',
        storage=atapi.AnnotationStorage(),
        widget=atapi.DecimalWidget(
            label=_(u"Vitamin A"),
            description=_(u"percent"),
        ),
        required=True,
        validators=('isDecimal'),
    ),

    atapi.FloatField(
        'vitamin_c',
        storage=atapi.AnnotationStorage(),
        widget=atapi.DecimalWidget(
            label=_(u"Vitamin C"),
            description=_(u"percent"),
        ),
        required=True,
        validators=('isDecimal'),
    ),

    atapi.FloatField(
        'calcium',
        storage=atapi.AnnotationStorage(),
        widget=atapi.DecimalWidget(
            label=_(u"Calcium"),
            description=_(u"percent"),
        ),
        required=True,
        validators=('isDecimal'),
    ),

    atapi.FloatField(
        'iron',
        storage=atapi.AnnotationStorage(),
        widget=atapi.DecimalWidget(
            label=_(u"Iron"),
            description=_(u"percent"),
        ),
        required=True,
        validators=('isDecimal'),
    ),

    atapi.FloatField(
        'vitamin_d',
        storage=atapi.AnnotationStorage(),
        widget=atapi.DecimalWidget(
            label=_(u"Vitamin D"),
            description=_(u"percent"),
        ),
        required=True,
        validators=('isDecimal'),
    ),

    atapi.LinesField(
        'ingredients',
        storage=atapi.AnnotationStorage(),
        widget=atapi.LinesWidget(
            label=_(u"Ingredients"),
            description=_(u"one per line"),
        ),
        required=True,
    ),

    atapi.TextField(
        'body_text',
        storage=atapi.AnnotationStorage(),
        widget=atapi.TextAreaWidget(
            label=_(u"Body Text"),
            description=_(u"More information about this food"),
        ),
    ),

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

FoodSchema['title'].storage = atapi.AnnotationStorage()
FoodSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(FoodSchema, moveDiscussion=False)

class Food(base.ATCTContent):
    """Information about a Food"""
    implements(IFood)

    meta_type = "Food"
    schema = FoodSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    food_type = atapi.ATFieldProperty('food_type')

    serving_size = atapi.ATFieldProperty('serving_size')

    serving_size_units = atapi.ATFieldProperty('serving_size_units')

    serving_weight = atapi.ATFieldProperty('serving_weight')

    servings_per_container = atapi.ATFieldProperty('servings_per_container')

    calories = atapi.ATFieldProperty('calories')

    fat_calories = atapi.ATFieldProperty('fat_calories')

    total_fat = atapi.ATFieldProperty('total_fat')

    saturated_fat = atapi.ATFieldProperty('saturated_fat')

    trans_fat = atapi.ATFieldProperty('trans_fat')

    cholesterol = atapi.ATFieldProperty('cholesterol')

    sodium = atapi.ATFieldProperty('sodium')

    total_carbohydrate = atapi.ATFieldProperty('total_carbohydrate')

    dietary_fiber = atapi.ATFieldProperty('dietary_fiber')

    sugars = atapi.ATFieldProperty('sugars')

    protein = atapi.ATFieldProperty('protein')

    vitamin_a = atapi.ATFieldProperty('vitamin_a')

    vitamin_c = atapi.ATFieldProperty('vitamin_c')

    calcium = atapi.ATFieldProperty('calcium')

    iron = atapi.ATFieldProperty('iron')

    vitamin_d = atapi.ATFieldProperty('vitamin_d')

    ingredients = atapi.ATFieldProperty('ingredients')

    body_text = atapi.ATFieldProperty('body_text')

atapi.registerType(Food, PROJECTNAME)
