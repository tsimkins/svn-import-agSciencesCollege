from setuptools import setup, find_packages
import os

version = '1.1.7'

setup(name='collective.contentleadimage',
      version=version,
      description="Adds lead image to any content in plone site",
      long_description=open("README.txt").read() + "\n\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone',
      author='Radim Novotny',
      author_email='novotny.radim@gmail.com',
      url='http://pypi.python.org/pypi/collective.contentleadimage',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'archetypes.schemaextender',
          'plone.browserlayer',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
