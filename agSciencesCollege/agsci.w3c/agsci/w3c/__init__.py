from zope.i18nmessageid import MessageFactory
w3cMessageFactory = MessageFactory('agsci.w3c')

def initialize(context):
    pass

class Report():

    def __init__(self, categories=[]):
        self.stats = {}
        for c in categories:
            self.stats[c] = []
        
    def add(self, category, o):
        if not category in self.stats.keys():
            self.stats[category] = []
        self.stats[category].append(o)
        
    def summary(self):
        return "\n".join(['%s : %d' % (x, len(self.stats[x])) for x in sorted(self.stats.keys())])
        
    def get(self, category):
        return self.stats.get(category, [])