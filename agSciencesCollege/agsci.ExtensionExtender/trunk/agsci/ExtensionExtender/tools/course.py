from zope.component import getUtility
from Products.CMFCore.utils import UniqueObject
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
import xlrd
import sqlite3
import Zope2
import re

class ExtensionCourseTool(UniqueObject, SimpleItem):

    id = 'extension_course_tool'
    meta_type = 'Extension Course Tool'
    
    security = ClassSecurityInfo()

    configFile = 'extension_courses.xls'

    def conn(self):
        sqlite_dir = Zope2.os.getenv('SQLITE_DBDIR')
        return sqlite3.connect('%s/extension_courses.db' % sqlite_dir)
    
    security.declarePrivate('loadCourses')
    def loadCourses(self):
        conn = self.conn()
        c = conn.cursor()

        c.execute("""drop table if exists courses""")
        c.execute("""create table courses (category text, topic text, subtopic text, course text, description text, body_text text)""")

        portal_skins = getToolByName(self, 'portal_skins')
        paths = portal_skins.getSkinPath(portal_skins.getDefaultSkin()).split(',')

        o = None

        for p in paths:
            if p in portal_skins.objectIds() and self.configFile in portal_skins[p].objectIds():
                o = portal_skins[p][self.configFile]

        if o:
            xls = xlrd.open_workbook(file_contents=o._readFile(False))
            sheet = xls.sheet_by_index(0)
            header = [x.value.strip() for x in sheet.row(0)]

            course_col = header.index('Course')
            category_col = header.index('Category')
            topic_col = header.index('Topic')
            subtopic_col = header.index('Subtopic')
            description_col = header.index('Description')
            body_text_col = header.index('Body Text')
                        
            for r in range(1,sheet.nrows):
                row = sheet.row(r)

                course_name = row[course_col].value.strip()
                category_name = row[category_col].value.strip()
                topic_name = row[topic_col].value.strip()
                subtopic_name = row[subtopic_col].value.strip()
                description_name = row[description_col].value.strip()
                body_text_name = row[body_text_col].value.strip()

                c.execute("insert into courses (category, topic, subtopic, course, description, body_text) values (?, ?, ?, ?, ?, ?)", 
                          (category_name, topic_name, subtopic_name, course_name, description_name, body_text_name))

        conn.commit()
        conn.close()

        

    security.declarePublic('getCourses')
    def getCourses(self):
        conn = self.conn()

        c = conn.cursor()

        results = c.execute("""select distinct course from courses order by course""").fetchall()

        conn.close()

        return [x[0] for x in results]


    security.declarePublic('getCourseInfo')
    def getCourseInfo(self, course):
        
        conn = self.conn()

        c = conn.cursor()

        results = c.execute("""select course, description, body_text from courses where course = ? limit 1""", (course,)).fetchone()

        conn.close()

        return results

    security.declarePrivate('validateCourse')
    def validateCourse(self, course):
        
        conn = self.conn()

        c = conn.cursor()

        results = c.execute("""select distinct course, description, body_text from courses where course = ?""", (course,)).fetchall()

        conn.close()

        return results


    security.declarePublic('getCoursesByCategory')
    def getCoursesByCategory(self, category):
        
        conn = self.conn()

        c = conn.cursor()

        results = c.execute("""select course from courses where category = ? order by course""", (category,)).fetchall()

        conn.close()

        return results

    security.declarePublic('getCoursesByTopic')
    def getCoursesByTopic(self, category, topic):
        
        conn = self.conn()

        c = conn.cursor()

        results = c.execute("""select course from courses where category = ? and topic = ? order by course""", (category,topic)).fetchall()

        conn.close()

        return results


    security.declarePublic('getCoursesBySubtopic')
    def getCoursesBySubtopic(self, category, topic, subtopic):
        
        conn = self.conn()

        c = conn.cursor()

        results = c.execute("""select course from courses where category = ? and topic = ? and subtopic = ? order by course""", (category,topic,subtopic)).fetchall()

        conn.close()

        return results


    security.declarePublic('getCourseCategory')
    def getCourseCategory(self, course):
        
        conn = self.conn()

        c = conn.cursor()

        results = c.execute("""select distinct category from courses where course = ? order by category""", (course,)).fetchall()

        conn.close()

        return results


    security.declarePublic('getCourseTopics')
    def getCourseTopics(self, course):
        
        conn = self.conn()

        c = conn.cursor()

        results = c.execute("""select distinct category, topic from courses where course = ? order by category, topic""", (course,)).fetchall()

        conn.close()

        return results


    security.declarePublic('getCourseSubtopics')
    def getCourseSubtopics(self, course):
        
        conn = self.conn()

        c = conn.cursor()

        results = c.execute("""select distinct category, topic, subtopic from courses where course = ? order by category, topic, subtopic""", (course,)).fetchall()

        conn.close()

        return results


    security.declarePublic('getCategories')
    def getCategories(self):
        
        conn = self.conn()

        c = conn.cursor()

        results = c.execute("""select distinct category from courses order by category""").fetchall()

        conn.close()

        return [x[0] for x in results]


    security.declarePublic('getTopics')
    def getTopics(self, category=None):
        
        conn = self.conn()

        c = conn.cursor()

        results = c.execute("""select distinct category, topic from courses order by category, topic""").fetchall()

        conn.close()
        
        if category:
            return [x for x in results if x[0] == category]
        else:
            return results


    security.declarePublic('getSubtopics')
    def getSubtopics(self, category=None, topic=None):
        
        conn = self.conn()

        c = conn.cursor()

        results = c.execute("""select distinct category, topic, subtopic from courses where subtopic is not null and subtopic != '' order by category, topic, subtopic""").fetchall()

        conn.close()

        if category and topic:
            return [x for x in results if (x[0] == category and x[1] == topic and x[2])]
        elif category:
            return [x for x in results if x[0] == category]
        else:
            return results

    security.declarePublic('getCourseForEvent')
    
    def getCourseForEvent(self, event_brain, skip_if_exists=True):

        abbr = {
            'BKC' : 'Better Kid Care',
            'Technology Tuesdays' : 'Technology Tuesday Series',
            'StrongWomen' : 'Strong Women/Growing Stronger',
            'Strong Women' : 'Strong Women/Growing Stronger',
            'Cooking for Crowds' : 'Cooking for Crowds-Volunteer Food Safety',
            'Land Use Webinar Series' : 'Land Use Planning',
            'Master Well Owner' : 'Master Well Owner Network (MWON) Volunteer Training',
            'MWON' : 'Master Well Owner Network (MWON) Volunteer Training',
            'Pesticide Testing' : 'Pennsylvania Pesticide Applicator Certification Training',
            'Pesticide Update Meeting' : 'Pennsylvania Pesticide Applicator Certification Training',
            'Pesticide Core Credit Recertification' : 'Pennsylvania Pesticide Applicator Certification Training',
            'Agricultural Rescue Training' : 'PAgricultural Rescue Training',
            'Fundamentals of HACCP' : 'Fundamentals of Hazard Analysis Critical Control Point (HACCP)',
            'Principles of HACCP for Meat and Poultry Processors' : 'Hazard Analysis Critical Control Point (HACCP) for Meat and Poultry Processors',
            'Shale' : 'Shale Gas 101',
            'Sheep Shearing Workshops' : 'Sheep Shearing Instruction',
            'Six Steps to a Highly Effective Organization' : 'Six Steps to an Effective Organization',
            'Tools for Equine Health & Soundness' : 'Tools for Equine Health and Soundness',
            
        }

        if skip_if_exists and hasattr(event_brain, 'extension_courses') and event_brain.extension_courses:
            return event_brain.extension_courses[0]

        title = event_brain.Title.decode('utf-8').lower().strip()
        
        char_regex = re.compile("[^a-zA-Z0-9]", re.I|re.M)
       
        def normalize(i):
            return char_regex.sub('', i).lower()
        
        courses = sorted([x.strip() for x in self.getCourses()], key=lambda x: len(x), reverse=True)
        
        # Check for exact title match
        for c in courses:
            if c.lower() in title:
                return c

        # Check for normalized title match
        for c in courses:
            if normalize(c) in normalize(title):
                return c

        # Check for abbreviated title match
        for c in courses:
            for a in sorted(abbr.keys(), key=lambda x: len(x), reverse=True):
                if a.lower() in title and abbr[a] == c:
                    return c

        # Check for abbreviated normalized title match
        for c in courses:
            for a in sorted(abbr.keys(), key=lambda x: len(x), reverse=True):
                if normalize(a) in normalize(title) and abbr[a] == c:
                    return c
        
        return ''

InitializeClass(ExtensionCourseTool)