# Testing imports
from plone.app.testing import PloneSandboxLayer, quickInstallProduct, PLONE_FIXTURE, applyProfile
from plone.app.testing.layers import IntegrationTesting
import unittest2 as unittest
from plone.testing import z2
import transaction
from Products.Five.browser import BrowserView
from zope.component import queryMultiAdapter
from zope.viewlet.interfaces import IViewletManager
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, login, setRoles

# Plone imports
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from zope.security.interfaces import NoInteraction

# Product imports
from agsci.blognewsletter.events import onBlogCreation, onNewsletterCreation

class BlogNewsletterLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        #: Load ZCML for the package being tested.
        import agsci.blognewsletter
        self.loadZCML(package=agsci.blognewsletter)
        z2.installProduct(app, 'agsci.blognewsletter')


    def setUpPloneSite(self, portal):
        #Install the package in the Plone site.
        applyProfile(portal, 'agsci.blognewsletter:default')

        # Run the Blog setup routine
        self.setUpBlog(portal)

    def setUpBlog(self, portal):

        # Set role of test user to 'Manager' and log in as that user
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)

        # Create a blog
        blog_id = portal.invokeFactory(id="blog",
                      type_name="Blog",
                      title="Blog",
                      description="My Blog Description",
                      available_public_tags=['Sample Tag'])

        transaction.commit()

        blog = portal[blog_id]

        # Run event handler for blog
        onBlogCreation(blog, None)

        # Create newsletter
        newsletter_id = blog.invokeFactory(id="my-newsletter",
                      type_name="Newsletter",
                      title="My Newsletter",
                      description="My Newsletter Description")

        transaction.commit()

        # Run event handler for newsletter.  Note, this should rename it to 'newsletter' as the short id.
        onNewsletterCreation(blog[newsletter_id], None)


        # publish blog
        portal_workflow = getToolByName(portal, 'portal_workflow')

        #Apparently, we need to tell Plone what it's default workflow is before this will work.
        portal_workflow.setDefaultChain('simple_publication_workflow')

        childObjects = [x[1] for x in portal.ZopeFind(blog, search_sub=1)]
        childObjects.append(blog)

        for obj in childObjects:
            try:
                if not portal_workflow.getInfoFor(obj, 'review_state').lower().count('publish'):
                    portal_workflow.doActionFor(obj, 'publish')
            except WorkflowException:
                continue # Must not support workflow

        transaction.commit()

        # Assign tag to sample news item
        for obj in childObjects:
            if obj.id == 'sample':
                obj.public_tags = ('Sample Tag', )
                obj.reindexObject()

        transaction.commit()


BLOGNEWSLETTER_FIXTURE = BlogNewsletterLayer()

BLOGNEWSLETTER_INTEGRATION_TESTING = IntegrationTesting(bases=(BLOGNEWSLETTER_FIXTURE,), name="BlogNewsletter:Integration")

class ViewTests(unittest.TestCase):

    layer = BLOGNEWSLETTER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        # Creating empty value for ACTUAL_URL to prevent KeyError related to 
        # view/prepareObjectTabs
        self.request['ACTUAL_URL'] = ''

    def test_newsletter_email(self):
        resource = self.portal.blog.newsletter.restrictedTraverse('@@newsletter_email')
        resource()

    def test_newsletter_view(self):
        resource = self.portal.blog.newsletter.restrictedTraverse('@@newsletter_view')
        resource()

    def test_newsletter_print(self):
        resource = self.portal.blog.newsletter.restrictedTraverse('@@newsletter_print')
        resource()

    def test_tags_view(self):
        resource = self.portal.blog.latest.unrestrictedTraverse('@@tags')
        resource()

class ViewletTests(unittest.TestCase):

    layer = BLOGNEWSLETTER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_tags_viewlet(self):
        # Grab the sample news item
        context = self.portal.blog.latest.queryCatalog()[0].getObject()
        request = self.request
        view = BrowserView(context, request)
        manager_name = "plone.belowcontenttitle"
        manager = queryMultiAdapter((context, request, view), IViewletManager, manager_name, default=None)
        self.failUnless(manager)
        manager.update()
        my_viewlet = [v for v in manager.viewlets if v.__name__ == 'agsci.blognewsletter.tags']
        self.failUnlessEqual(len(my_viewlet), 1)
        self.failUnless('Sample Tag' in my_viewlet[0].render())


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
