/* semicolon-delimited.js */

/*
   if body custom css class includes 'semicolon-delimited', then split the description into separate lines delimited by semicolon
*/
   
function splitDescription()
{
    
    jq('body.custom-semicolon-delimited #content .description, body.custom-semicolon-delimited #content .documentDescription #parent-fieldname-description').each(
    
        function()
        {
            var lines = this.innerHTML.split(";");

            var new_html =  "<ul>";

            for (var i=0; i<lines.length; i++)
            {
                var line_text = lines[i];
                
                if (line_text.match(":"))
                {
                    list = line_text.split(":");
                    line_text = "<strong>" + list[0] + ":</strong>" + list[1];
                }
                
                new_html = new_html + "<li>" + line_text + "</li>";
            }

            new_html = new_html + "</ul>";
            
            this.innerHTML = new_html
        }
    );

}


jq(document).ready(
	function () {
        splitDescription();
	}
)
