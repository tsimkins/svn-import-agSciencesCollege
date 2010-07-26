# -*- coding: utf-8 -*-

from zope.interface import Interface, Attribute

class ISubsite(Interface):
    """Subsites are folders designed specifically for subsites
    """

class ICountySite(Interface):
    """CountySites are folders designed specifically for Extension counties
    """

class ISection(Interface):
    """Sections are parts of a subsite with their own navigation
    """

class IBlog(Interface):
    """Blogs are folders designed specifically for news items
    """