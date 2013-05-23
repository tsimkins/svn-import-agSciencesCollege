# This is a mapping for the surrounding counties, when given a county

data = {   'Adams': ['Adams', 'Cumberland', 'Franklin', 'York'],
    'Allegheny': [   'Allegheny',
                     'Armstrong',
                     'Beaver',
                     'Butler',
                     'Washington',
                     'Westmoreland'],
    'Armstrong': [   'Allegheny',
                     'Armstrong',
                     'Butler',
                     'Clarion',
                     'Indiana',
                     'Jefferson',
                     'Venango',
                     'Westmoreland'],
    'Beaver': ['Allegheny', 'Beaver', 'Butler', 'Lawrence', 'Washington'],
    'Bedford': [   'Bedford',
                   'Blair',
                   'Cambria',
                   'Fulton',
                   'Huntingdon',
                   'Somerset'],
    'Berks': [   'Berks',
                 'Bucks',
                 'Chester',
                 'Lancaster',
                 'Lebanon',
                 'Lehigh',
                 'Montgomery',
                 'Schuylkill',
                 'Northampton'],
    'Blair': [   'Bedford',
                 'Blair',
                 'Cambria',
                 'Centre',
                 'Clearfield',
                 'Huntingdon',
                 'Fulton',
                 'Somerset'],
    'Bradford': [   'Bradford',
                    'Lycoming',
                    'Sullivan',
                    'Susquehanna',
                    'Tioga',
                    'Wyoming'],
    'Bucks': ['Bucks', 'Lehigh', 'Montgomery', 'Northampton', 'Philadelphia', 'Berks'],
    'Butler': [   'Allegheny',
                  'Armstrong',
                  'Beaver',
                  'Butler',
                  'Clarion',
                  'Lawrence',
                  'Mercer',
                  'Venango',
                  'Westmoreland'],
    'Cambria': [   'Bedford',
                   'Blair',
                   'Cambria',
                   'Centre',
                   'Clearfield',
                   'Indiana',
                   'Somerset',
                   'Westmoreland',
                   'Fulton',
                   'Huntingdon'],
    'Cameron': ['Cameron', 'Clearfield', 'Clinton', 'Elk', 'McKean', 'Potter'],
    'Carbon': [   'Carbon',
                  'Lehigh',
                  'Luzerne',
                  'Monroe',
                  'Northampton',
                  'Schuylkill'],
    'Centre': [   'Blair',
                  'Cambria',
                  'Centre',
                  'Clearfield',
                  'Clinton',
                  'Huntingdon',
                  'Mifflin',
                  'Union',
                  'Lycoming'],
    'Chester': ['Berks', 'Chester', 'Delaware', 'Lancaster', 'Montgomery'],
    'Clarion': [   'Armstrong',
                   'Butler',
                   'Clarion',
                   'Forest',
                   'Jefferson',
                   'Venango'],
    'Clearfield': [   'Blair',
                      'Cambria',
                      'Cameron',
                      'Centre',
                      'Clearfield',
                      'Clinton',
                      'Elk',
                      'Indiana',
                      'Jefferson'],
    'Clinton': [   'Cameron',
                   'Centre',
                   'Clearfield',
                   'Clinton',
                   'Lycoming',
                   'Potter',
                   'Union'],
    'Columbia': [   'Columbia',
                    'Luzerne',
                    'Lycoming',
                    'Montour',
                    'Northumberland',
                    'Schuylkill',
                    'Sullivan',
                    'Snyder',
                    'Union',],
    'Crawford': ['Crawford', 'Erie', 'Mercer', 'Venango', 'Warren'],
    'Cumberland': [   'Adams',
                      'Cumberland',
                      'Dauphin',
                      'Franklin',
                      'Perry',
                      'York'],
    'Dauphin': [   'Cumberland',
                   'Dauphin',
                   'Juniata',
                   'Lancaster',
                   'Lebanon',
                   'Northumberland',
                   'Perry',
                   'Schuylkill',
                   'Snyder',
                   'York'],
    'Delaware': ['Chester', 'Delaware', 'Montgomery', 'Philadelphia'],
    'Elk': [   'Cameron',
               'Clearfield',
               'Elk',
               'Forest',
               'Jefferson',
               'McKean',
               'Warren'],
    'Erie': ['Crawford', 'Erie', 'Warren'],
    'Fayette': ['Fayette', 'Greene', 'Somerset', 'Washington', 'Westmoreland'],
    'Forest': [   'Clarion',
                  'Elk',
                  'Forest',
                  'Jefferson',
                  'McKean',
                  'Venango',
                  'Warren'],
    'Franklin': [   'Adams',
                    'Cumberland',
                    'Franklin',
                    'Fulton',
                    'Huntingdon',
                    'Juniata',
                    'Perry'],
    'Fulton': ['Bedford', 'Franklin', 'Fulton', 'Huntingdon', 'Somerset', 'Blair', 'Cambria'],
    'Greene': ['Fayette', 'Greene', 'Washington'],
    'Huntingdon': [   'Bedford',
                      'Blair',
                      'Centre',
                      'Franklin',
                      'Fulton',
                      'Huntingdon',
                      'Juniata',
                      'Mifflin',
                      'Somerset',
                      'Cambria'],
    'Indiana': [   'Armstrong',
                   'Cambria',
                   'Clearfield',
                   'Indiana',
                   'Jefferson',
                   'Westmoreland'],
    'Jefferson': [   'Armstrong',
                     'Clarion',
                     'Clearfield',
                     'Elk',
                     'Forest',
                     'Indiana',
                     'Jefferson'],
    'Juniata': [   'Dauphin',
                   'Franklin',
                   'Huntingdon',
                   'Juniata',
                   'Mifflin',
                   'Northumberland',
                   'Perry',
                   'Snyder'],
    'Lackawanna': [   'Lackawanna',
                      'Luzerne',
                      'Monroe',
                      'Susquehanna',
                      'Wayne',
                      'Wyoming',
                      'Pike'],
    'Lancaster': [   'Berks',
                     'Chester',
                     'Dauphin',
                     'Lancaster',
                     'Lebanon',
                     'York'],
    'Lawrence': ['Beaver', 'Butler', 'Lawrence', 'Mercer'],
    'Lebanon': ['Berks', 'Dauphin', 'Lancaster', 'Lebanon', 'Schuylkill'],
    'Lehigh': [   'Berks',
                  'Bucks',
                  'Carbon',
                  'Lehigh',
                  'Montgomery',
                  'Northampton',
                  'Schuylkill'],
    'Luzerne': [   'Carbon',
                   'Columbia',
                   'Lackawanna',
                   'Luzerne',
                   'Monroe',
                   'Schuylkill',
                   'Sullivan',
                   'Wyoming'],
    'Lycoming': [   'Bradford',
                    'Clinton',
                    'Columbia',
                    'Lycoming',
                    'Montour',
                    'Northumberland',
                    'Potter',
                    'Tioga',
                    'Sullivan',
                    'Union',
                    'Centre'],
    'McKean': ['Cameron', 'Elk', 'Forest', 'McKean', 'Potter', 'Warren'],
    'Mercer': ['Butler', 'Crawford', 'Lawrence', 'Mercer', 'Venango'],
    'Mifflin': [   'Centre',
                   'Huntingdon',
                   'Juniata',
                   'Mifflin',
                   'Snyder',
                   'Union'],
    'Monroe': [   'Carbon',
                  'Lackawanna',
                  'Luzerne',
                  'Monroe',
                  'Northampton',
                  'Pike',
                  'Wayne'],
    'Montgomery': [   'Bucks',
                      'Chester',
                      'Delaware',
                      'Lehigh',
                      'Philadelphia',
                      'Northampton', 
                      'Schuylkill', 
                      'Montgomery', 
                      'Berks'],
    'Montour': [   'Columbia', 
                   'Lycoming', 
                   'Montour', 
                   'Northumberland', 
                   'Snyder', 
                   'Union',
                   'Schuylkill'],
    'Northampton': ['Bucks', 'Carbon', 'Lehigh', 'Monroe', 'Northampton', 'Schuylkill', 'Montgomery', 'Berks'],
    'Northumberland': [   'Columbia',
                          'Dauphin',
                          'Juniata',
                          'Lycoming',
                          'Montour',
                          'Northumberland',
                          'Perry',
                          'Schuylkill',
                          'Snyder',
                          'Union'],
    'Perry': [   'Cumberland',
                 'Dauphin',
                 'Franklin',
                 'Juniata',
                 'Northumberland',
                 'Perry',
                 'Schuylkill'],
    'Philadelphia': ['Bucks', 'Delaware', 'Montgomery', 'Philadelphia'],
    'Pike': ['Monroe', 'Pike', 'Wayne', 'Lackawanna'],
    'Potter': ['Cameron', 'Clinton', 'Lycoming', 'McKean', 'Potter', 'Tioga'],
    'Schuylkill': [   'Berks',
                      'Carbon',
                      'Columbia',
                      'Dauphin',
                      'Lebanon',
                      'Lehigh',
                      'Luzerne',
                      'Northumberland',
                      'Northampton', 
                      'Schuylkill', 
                      'Montgomery', 
                      'Montour',
                      'Perry'],
    'Snyder': [   'Dauphin',
                  'Juniata',
                  'Mifflin',
                  'Northumberland',
                  'Snyder',
                  'Union',
                  'Montour',
                  'Columbia'],
    'Somerset': ['Bedford', 'Cambria', 'Fayette', 'Somerset', 'Westmoreland', 'Blair', 'Huntingdon', 'Fulton'],
    'Sullivan': [   'Bradford',
                    'Columbia',
                    'Luzerne',
                    'Lycoming',
                    'Sullivan',
                    'Tioga',
                    'Wyoming'],
    'Susquehanna': [   'Bradford',
                       'Lackawanna',
                       'Susquehanna',
                       'Wayne',
                       'Wyoming'],
    'Tioga': ['Bradford', 'Lycoming', 'Potter', 'Sullivan', 'Tioga'],
    'Union': [   'Centre',
                 'Clinton',
                 'Lycoming',
                 'Mifflin',
                 'Northumberland',
                 'Snyder',
                 'Union',
                 'Montour',
                 'Columbia'],
    'Venango': [   'Armstrong',
                   'Butler',
                   'Clarion',
                   'Crawford',
                   'Forest',
                   'Mercer',
                   'Venango',
                   'Warren'],
    'Warren': [   'Crawford',
                  'Elk',
                  'Erie',
                  'Forest',
                  'McKean',
                  'Venango',
                  'Warren'],
    'Washington': [   'Allegheny',
                      'Beaver',
                      'Fayette',
                      'Greene',
                      'Washington',
                      'Westmoreland'],
    'Wayne': ['Lackawanna', 'Monroe', 'Pike', 'Susquehanna', 'Wayne'],
    'Westmoreland': [   'Allegheny',
                        'Armstrong',
                        'Butler',
                        'Cambria',
                        'Fayette',
                        'Indiana',
                        'Somerset',
                        'Washington',
                        'Westmoreland'],
    'Wyoming': [   'Bradford',
                   'Lackawanna',
                   'Luzerne',
                   'Sullivan',
                   'Susquehanna',
                   'Wyoming'],
    'York': ['Adams', 'Cumberland', 'Dauphin', 'Lancaster', 'York']}

def getSurroundingCounties(county):
    #sanitize
    county = county.title().replace('Mckean', 'McKean')
    if county not in data.keys():
        return []
    else:
        return data[county]

# Run this to validate relationships and ensure valid county names
def reconcileCounties():
    for county in data.keys():
        counties = data.get(county)
        if len(counties) > len(set(counties)):
            print "Duplicate Counties %s" % county
        if county not in counties:
            print "Missing self %s" % county
        for c in counties:
            if not data.get(c):
                print "Invalid county %s in %s" % (c, county)
            elif not county in data.get(c):
                print "%s not in %s" % (county, c)

#reconcileCounties()