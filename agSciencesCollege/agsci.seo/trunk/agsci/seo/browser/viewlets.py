from zope.component import getMultiAdapter
from plone.app.layout.viewlets.common import ViewletBase
from DateTime import DateTime

class CanonicalURLViewlet(ViewletBase):

    def update(self):

        self.canonical_url = ''

        # Look up canonical URL refs
        refs = self.context.getReferences(relationship = 'IsCanonicalURLFor')

        if refs:
            # Just in case it has multiples
            self.canonical_url = refs[0].absolute_url()
        else:
            # Look for the string field
            try:
                if self.context.canonical_url_text:
                    self.canonical_url = self.context.canonical_url_text
            except AttributeError:
                pass


class RobotsMetaViewlet(ViewletBase):

    def update(self):

        self.norobots = False
        
        # Explicit Exclude from Robots checked
        
        try:
            if self.context.exclude_from_robots:
                self.norobots = True
        except AttributeError:
            pass

        now = DateTime()

        # Event is over

        if self.context.portal_type in ['Event'] and self.context.end() < now:
            self.norobots = True

        # Content is expired

        if self.context.expires() < now:
            self.norobots = True
