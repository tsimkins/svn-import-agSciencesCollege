from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='collective.tagmanager',
      version=version,
      description="Allows hierarchical management of tags",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Tim Simkins',
      author_email='trs22@psu.edu',
      url='https://weblion.psu.edu/svn/weblion/agSciencesCollege/collective.tagmanager/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """
      )
