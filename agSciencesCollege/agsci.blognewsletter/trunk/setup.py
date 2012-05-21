from setuptools import setup, find_packages
import os

version = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 
    'agsci', 'blognewsletter', 'version.txt')).read().strip()

setup(name='agsci.blognewsletter',
    version=version,
    description="Plone blog/newsletter package based on the PSU AgSci products.",
    long_description=open("README.txt").read() + "\n" +
                     open("HISTORY.txt").read(),
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
      "Framework :: Plone",
      "Programming Language :: Python",
      "Topic :: Software Development :: Libraries :: Python Modules",
      "Development Status :: 2 - Pre-Alpha",
      ],
    keywords='',
    author='Tim Simkins, College of Agricultural Sciences, Penn State University',
    author_email='trs22@psu.edu',
    url='http://agsci.psu.edu/',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['agsci'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
      'Products.CMFPlone',
      'setuptools',
      'premailer',
      'plone.app.registry',
      'BeautifulSoup',
      'archetypes.schemaextender',
      'collective.monkeypatcher',
      # -*- Extra requirements: -*-
      ],

    extras_require = {
        'test': [
                'plone.app.testing',
            ]
    },

    entry_points="""
      # -*- Entry points: -*-
      """,
    )


