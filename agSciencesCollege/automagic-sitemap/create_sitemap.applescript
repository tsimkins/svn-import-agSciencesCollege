-- Originally found at:
-- http://forums.omnigroup.com/archive/index.php/t-112.html
-- Modified for use in Plone sitemap generator

on makeShape(aTitle, aURL)
	tell application "OmniGraffle"
		tell canvas of front window
			return make new shape with properties {text:aTitle, url:aURL, vertical padding:5, autosizing:full, side padding:10, magnets:{{1, 0}, {-1, 0}, {-1, 1}, {-1, -1}}, origin:{(x of canvasSize) / 2.0, (y of canvasSize) / 2.0}}
		end tell
	end tell
end makeShape

on makeConnection(aSource, aDestination)
	tell application "OmniGraffle"
		tell aSource
			set aLine to connect to aDestination with properties {line type:straight}
		end tell
		set tail magnet of aLine to 1
	end tell
end makeConnection

on siteDiagram(aFile)
	tell application "OmniGraffle"
		make new document
		tell layout info of canvas of front window
			set type to left to right
			set children to back to front ordering
		end tell
		
		set fileID to open for access aFile
		set isDone to false
		set siteLength to 0
		set urlsRead to 0
		repeat until isDone
			try
				-- read up to a tag, and see what the tag is
				read fileID before "<"
				set theTag to read fileID before ">"
				
				-- if it is a <loc> tag, then read the contents
				if theTag is "loc" then
					set theURL to read fileID before "<"
					
					-- added to handle URL with trailing /
					if last character of theURL is "/" then
						set theURL to (texts 1 thru ((length of theURL) - 1) of theURL)
					end if
					
					-- figure out the site and make a shape for it
					if siteLength is 0 then
						set siteLength to (length of theURL) + 1
						set rootURL to theURL
						set rootShape to my makeShape(rootURL, rootURL)
						set remainingURL to ""
						set moreToDo to false
					else
						set remainingURL to texts (siteLength + 1) thru -1 of theURL
						set moreToDo to true
					end if
					
					-- now walk along the URL looking for more slashes and creating a folder shape for each one it finds, and connecting each to the previous folder 
					
					
					
					
					set doneLength to siteLength
					set lastShape to rootShape
					
					repeat while moreToDo
						set nextOffset to (offset of "/" in remainingURL)
						if nextOffset is 0 then
							set moreToDo to false
						else
							set doneLength to doneLength + nextOffset
							set folderName to texts 1 thru (nextOffset - 1) of remainingURL
							set folderURL to texts 1 thru doneLength of theURL
							
							if last character of folderURL is "/" then
								set folderURL to (texts 1 thru ((length of folderURL) - 1) of folderURL)
							end if
							
							set matchingShapes to shapes of canvas of front window whose url is folderURL
							if (count of matchingShapes) is 0 then
								set folderShape to my makeShape(folderName, folderURL)
							else
								set folderShape to item 1 of matchingShapes
							end if
							my makeConnection(lastShape, folderShape)
							set lastShape to folderShape
							set remainingURL to texts (nextOffset + 1) thru -1 of remainingURL
						end if
					end repeat
					
					-- finally, it this URL wasn't a folder (or site root) itself, create another shape for it and connect it to the last folder
					if length of remainingURL is greater than 0 then
						set urlShape to my makeShape(remainingURL, theURL)
						my makeConnection(lastShape, urlShape)
					end if
					
					-- layout again for every 10 URLs we read 
					set urlsRead to urlsRead + 1
					if (urlsRead mod 10) is 0 then
						tell canvas of front window
							layout
							page adjust
						end tell
					end if
				end if
			on error errStr number errorNumber
				-- you'll want the next line if you want to see error messages
				--display dialog errStr
				set isDone to true
			end try
		end repeat
		
		close access fileID
		
		tell canvas of front window
			layout
			page adjust
		end tell
	end tell
end siteDiagram

on open of target_files
	repeat with aFile in target_files
		siteDiagram(aFile)
	end repeat
end open
