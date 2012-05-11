from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

import unittest

from Products.CMFCore.utils import getToolByName
from zope.publisher.browser import TestRequest 

from agsci.blognewsletter.browser import views
from agsci.blognewsletter.events import onBlogCreation, onNewsletterCreation

from agsci.blognewsletter.config import PRODUCT_DEPENDENCIES, DEPENDENCIES

PRODUCTS = list()
PRODUCTS += DEPENDENCIES
PRODUCTS.append('agsci.blognewsletter')


def setup_product():
    fiveconfigure.debug_mode = True
    import agsci.blognewsletter
    zcml.load_config('configure.zcml', agsci.blognewsletter)
    fiveconfigure.debug_mode = False
    for dependency in PRODUCTS:
        ztc.installProduct(dependency)
    ztc.installPackage('agsci.blognewsletter')

ptc.setupPloneSite(products=PRODUCTS) 

setup_product()


#----------
request = TestRequest()

class test_sample_test(ptc.PloneTestCase):
    def test_sample_test(self):
        self.failUnlessEqual(2,2)

class test_views(ptc.PloneTestCase):

    def test_create_blog(self):
        import pdb; pdb.set_trace()
        blog_id = self.portal.invokeFactory(id="my-blog", 
                      type_name="Blog", 
                      title="My Blog", 
                      description="My Blog Description")
        self.blog = self.portal[blog_id]
        onBlogCreation(self.blog)
        newsletter_id = self.blog.invokeFactory(id="my-newsletter", 
                      type_name="Newsletter", 
                      title="My Newsletter", 
                      description="My Newsletter Description")
        onNewsletterCreation(self.blog[newsletter_id])
        self.failUnless('newsletter' in self.blog.objectIds())
        self.newsletter = self.blog.newsletter


    def test_newsletter_view(self):
        #import pdb; pdb.set_trace()
        #v = views.NewsletterView(
        self.failUnlessEqual(2,2)
    
def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)