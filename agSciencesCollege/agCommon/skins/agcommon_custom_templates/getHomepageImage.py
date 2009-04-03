backgrounds = []
backgroundAlignments = []
mySWF = ""

for myImage in context.listFolderContents(contentFilter={"portal_type" : "Image"}):
    backgrounds.append(myImage.absolute_url())

    if myImage.hasProperty("align"):
        backgroundAlignments.append(myImage.align)
    else:
        backgroundAlignments.append("center")


for myFile in context.listFolderContents():

    if myFile.absolute_url().endswith(".swf"):

        mySWF = myFile.absolute_url()


print """
var bodyClass = document.body.className;

if(bodyClass.match(/template-document_homepage_view/))
{
	var homepageImage = document.getElementById("homepageimage");

	if (homepageImage)
	{
		var backgrounds = "%s".split(";");
		var backgroundAlignments = "%s".split(";");
		var randomnumber = Math.floor(Math.random()*backgrounds.length) ;
		homepageImage.style.backgroundImage = "url(" + backgrounds[randomnumber] + ")";
		homepageImage.style.backgroundPosition = backgroundAlignments[randomnumber];

		var so = new SWFObject("%s", "thinkAgain", "585", "265", "8", "transparent");
		so.addParam("wmode","transparent");
		so.write("homepageimage");
	}

}

""" % (";".join(backgrounds), ";".join(backgroundAlignments), mySWF)

return printed
