from agsci.seo import getDisallowedPaths

disallow = getDisallowedPaths(context)

return "\n".join(["Disallow: %s" % x for x in disallow])