from plone.app.layout.viewlets.common import SearchBoxViewlet
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class MultiSearchViewlet(SearchBoxViewlet):
    index = ViewPageTemplateFile('templates/custom_searchbox.pt')

    def getSearchOptions(self):
        ad54_props = getToolByName(getToolByName(self.context, 'portal_properties'), 'ad54elements_properties', None)

        if ad54_props is None:
            return []

        keys = ad54_props.getProperty('searchKeys')
        descriptions = ad54_props.getProperty('searchDescriptions')
        selected = ad54_props.getProperty('searchDefaultKey')

        # build a list of searches, if possible
        searches = []
        if keys is not None and descriptions is not None:
            for index in range(0,min(len(keys),len(descriptions))):
                searches.append({'key' : keys[index],
                                 'description' : descriptions[index],
                                 'selected' : selected == keys[index]})

        return searches

