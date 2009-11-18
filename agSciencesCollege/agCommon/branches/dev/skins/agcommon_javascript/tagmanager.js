/* tagmanager.js */

    function manageTags(prefix, label)
    {
        
        full_prefix = prefix + "-";
        
        existingTags = jq('#subject_existing_keywords option');

        for (var i=0; i<existingTags.size(); i++)
        {
            tag = existingTags.eq(i);
            
            if (tag.val().substring(0,full_prefix.length) == full_prefix)
            {
                tag.hide();
            }
        }

        mainTagLink = jq('<a href="#" id="edit_' + prefix + '_tags">' + label + '</a>');

        mainTagLink.click(
            function() 
            { 
                modalTags = jq('<div id="modal_tags"><h1>Choose the tags for this item:</h1></div>');
                
                existingTags = jq('#subject_existing_keywords option');

                for (var i=0; i<existingTags.size(); i++)
                {
                    tag = existingTags.eq(i);
                    
                    if (tag.val().substring(0,full_prefix.length) == full_prefix)
                    {
                        tagLabel = tag.val().substring(5,tag.val().length)
                        checkbox = jq('<input name="extension_tag" type="checkbox" value="' + tag.val() + '" /> <span>' + tagLabel + '</span><br />')
    
                        if (tag.attr("selected"))
                        {
                            checkbox.attr("checked", "checked");
                        }

                        checkbox.appendTo(modalTags);
                    }
                }
                
                buttons = jq('<div id="modal_buttons"></div>');
                jq('<input type="button" value="Cancel" class="simplemodal-close" /> ').appendTo(buttons);
                submit = jq('<input type="button" value="Submit" class="simplemodal-close" />');
                submit.click(
                    function () {
//                        debug = jq('#modal_tags');
                        newTags = jq('#modal_tags input');
                        existingTags = jq('#subject_existing_keywords option');
                        for (var i=0; i<=newTags.size(); i++)
                        {
                            newTag = newTags.eq(i);

                            if (newTag.attr("type") == "checkbox")
                            {
                                for (var j=0; j<existingTags.size(); j++)
                                {
                                    oldTag = existingTags.eq(j);
//                                    /jq('<div>' + oldTag.val() + ' ? ' + newTag.val() + '</div>').appendTo(debug);

                                    if (oldTag.val() == newTag.val())
                                    {
                                        oldTag.attr("selected", newTag.attr("checked"));
                                    }
                                }
                            }

                        }
                        //alert("pause");
                    }

                );
                submit.appendTo(buttons);
                buttons.appendTo(modalTags);
                
                modalTags.modal(); 
                return false;
            }
        )
        
        mainTagLink.appendTo('#archetypes-fieldname-subject');

    }


jq(document).ready(
	function () {
        manageTags("county", "Edit County Tags");
    	manageTags("main", "Edit Topic Tags");
	}
)
