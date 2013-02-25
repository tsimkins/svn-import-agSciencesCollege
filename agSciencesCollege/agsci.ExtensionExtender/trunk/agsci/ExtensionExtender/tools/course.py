from zope.component import getUtility
from Products.CMFCore.utils import UniqueObject
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
import xlrd
from plone.registry import field
from plone.registry.interfaces import IRegistry
from plone.registry.record import Record
from plone.registry.registry import Registry

class ExtensionCourseTool(UniqueObject, SimpleItem):

    id = 'extension_course_tool'
    meta_type = 'Extension Course Tool'

    security = ClassSecurityInfo()

    configFile = 'extension_courses.xls'

    @property
    def registry(self):
        return getUtility(IRegistry)

    def getRegistryKey(self, key):
        return "%s_%s" % (self.id, key)

    def __init__(self):
        pass

    security.declarePrivate('loadCourses')
    def loadCourses(self):
        portal_skins = getToolByName(self, 'portal_skins')
        paths = portal_skins.getSkinPath(portal_skins.getDefaultSkin()).split(',')
        o = None
        for p in paths:
            if p in portal_skins.objectIds() and self.configFile in portal_skins[p].objectIds():
                o = portal_skins[p][self.configFile]
        if o:
            course_data = {}
            topic_data = {}
            subtopic_data = {}

            xls = xlrd.open_workbook(file_contents=o._readFile(False))
            sheet = xls.sheet_by_index(0)
            header = [x.value.strip() for x in sheet.row(0)]

            course_col = header.index('Course')
            category_col = header.index('Category')
            topic_col = header.index('Topic')
            subtopic_col = header.index('Subtopic')
            subtopic_col = header.index('Description')
            subtopic_col = header.index('Body Text')
                        
            for r in range(1,sheet.nrows):
                row = sheet.row(r)

                course_name = row[course_col].value.strip()
                category_name = row[category_col].value.strip()
                topic_name = "%s:%s" % (category_name, row[topic_col].value.strip())
                subtopic_name = row[subtopic_col].value.strip()

                if subtopic_name:
                    subtopic_name = "%s:%s" % (topic_name, subtopic_name)

                if not course_data.get(course_name):
                    course_data[course_name] = []

                if not topic_data.get(topic_name):
                    topic_data[topic_name] = []

                if not subtopic_data.get(subtopic_name):
                    subtopic_data[subtopic_name] = []

                i_course_data = {}

                for c in range(0,sheet.ncols):
                    h = header[c]
                    i_course_data[h] = row[c].value.strip()

                course_data[course_name].append(i_course_data)
                topic_data[topic_name].append(i_course_data)
                subtopic_data[subtopic_name].append(i_course_data)

            self.registry.records[self.getRegistryKey('course')] = Record(field.Dict(title=u"Course Data"), course_data)
            self.registry.records[self.getRegistryKey('topic')] = Record(field.Dict(title=u"Topic Data"), topic_data)
            self.registry.records[self.getRegistryKey('subtopic')] = Record(field.Dict(title=u"Subtopic Data"), subtopic_data)

    security.declarePublic('getCourses')
    def getCourses(self):
        data = self.registry.records[self.getRegistryKey('course')]
        return sorted(data.value.keys())

    security.declarePublic('getCourseInfo')
    def getCourseInfo(self, course):
        data = self.registry.records[self.getRegistryKey('course')]
        return data.value.get(course)

    security.declarePublic('getCoursesByTopic')
    def getCoursesByTopic(self, topic):
        data = self.registry.records[self.getRegistryKey('topic')]
        return [x.get('Course') for x in data.value.get(topic)]

    security.declarePublic('getCoursesBySubtopic')
    def getCoursesBySubtopic(self, subtopic):
        data = self.registry.records[self.getRegistryKey('subtopic')]
        return [x.get('Course') for x in data.value.get(subtopic)]

    security.declarePublic('getCourseTopics')
    def getCourseTopics(self, course):
        data = self.getCourseInfo(course)
        if data:
            return [":".join([x.get('Category'), x.get('Topic')]) for x in data]
        else:
            return []

    security.declarePublic('getCourseSubtopics')
    def getCourseSubtopics(self, course):
        data = self.getCourseInfo(course)
        if data:
            return [":".join([x.get('Category'), x.get('Topic'), x.get('Subtopic')]) for x in data if x.get('Subtopic')]
        else:
            return []



InitializeClass(ExtensionCourseTool)