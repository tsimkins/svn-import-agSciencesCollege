backgrounds = []
backgroundAlignments = []
backgroundHeights = []

for myImage in context.listFolderContents(contentFilter={"portal_type" : "Image"}):
    backgrounds.append(myImage.absolute_url())

    if myImage.hasProperty("align"):
        backgroundAlignments.append(myImage.align)
    else:
        backgroundAlignments.append("center")

    backgroundHeights.append(str(myImage.getHeight()))
    
print """
var bodyClass = document.body.className;

if(bodyClass.match(/template-document_homepage_view/))
{
	var homepageImage = document.getElementById("homepageimage");

	if (homepageImage)
	{
		var backgrounds = "%s".split(";");
		var backgroundAlignments = "%s".split(";");
		var backgroundHeights = "%s".split(";");
		var randomnumber = Math.floor(Math.random()*backgrounds.length) ;
		homepageImage.style.backgroundImage = "url(" + backgrounds[randomnumber] + ")";
		homepageImage.style.backgroundPosition = backgroundAlignments[randomnumber];
		homepageImage.style.height = backgroundHeights[randomnumber] + 'px';
	}

}

""" % (";".join(backgrounds), ";".join(backgroundAlignments), ";".join(backgroundHeights))

return printed

