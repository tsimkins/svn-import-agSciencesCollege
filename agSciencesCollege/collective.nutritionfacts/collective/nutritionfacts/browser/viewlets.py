from zope.component import getMultiAdapter
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFCore.utils import getToolByName


class NutritionFactsViewlet(ViewletBase):   
    index = ViewPageTemplateFile('templates/nutritionfacts.pt')

    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.anonymous = self.portal_state.anonymous()
        self.numbers = {}
        self.percents = {}
        
        for value in [
                        'serving_size', 
                        'serving_weight', 
                        'servings_per_container', 
                        'calories', 
                        'fat_calories', 
                        'total_fat', 
                        'saturated_fat', 
                        'trans_fat', 
                        'cholesterol', 
                        'sodium', 
                        'total_carbohydrate', 
                        'dietary_fiber', 
                        'sugars', 
                        'protein', 
                        'vitamin_a', 
                        'vitamin_c', 
                        'calcium', 
                        'iron', 
                        'vitamin_d']:
    
            
            self.numbers[value] = str(self.context[value])

            if self.numbers[value].endswith('.0'):
                self.numbers[value] = self.numbers[value].replace('.0', '')
        rda = {
            'total_fat': 65, 
            'saturated_fat' : 20, 
            'cholesterol' : 300, 
            'sodium' : 2400, 
            'total_carbohydrate' : 300, 
            'dietary_fiber' : 25, 
            'sugars' : 1, 
            'protein' : 1
        }
        
        for value in [
                        'total_fat', 
                        'saturated_fat', 
                        'cholesterol', 
                        'sodium', 
                        'total_carbohydrate', 
                        'dietary_fiber', 
                        'sugars', 
                        'protein']:

            self.percents[value] = int(round(100*float(self.context[value])/rda[value], 0))