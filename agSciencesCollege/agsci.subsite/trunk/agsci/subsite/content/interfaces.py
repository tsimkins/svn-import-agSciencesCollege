# -*- coding: utf-8 -*-

from zope.interface import Interface, Attribute

class ISubsite(Interface):
    """Subsites are folders designed specifically for subsites
    """

class IBlog(Interface):
    """Blogs are folders designed specifically for news items
    """