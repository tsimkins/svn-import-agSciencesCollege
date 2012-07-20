// Check to verify that the provided subtopic is valid for the selected topics

function isValidSubtopic(v) {

    var isok = false;

    jq('#extension_topics').find("option").each(
        
        function(index) {
            var item_text = jq(this).val();


            if (getL2Topic(v.val()) == item_text)
            {
                isok = true;
            }

        }
        
    )

    return isok;

}

function getL1Topic(t) {
    var delimiter = ': ';
    return t.substr(0, t.indexOf(delimiter));
}

function getL1SubTopic(t) {
    var delimiter = ': ';
    return t.substr(t.indexOf(delimiter) + delimiter.length, t.length);
}

function getL2Topic(t) {
    var delimiter = ': ';
    return t.substr(0, t.lastIndexOf(delimiter));
}

function getL2SubTopic(t) {
    var delimiter = ': ';
    return t.substr(t.lastIndexOf(delimiter) + delimiter.length, t.length);
}


function hideInvalidSubtopics(v) {
    
    var isSelectedSubtopics = (v.attr('id') == 'extension_subtopics');
    
    v.find("option").each(
        function(index) {
            if (isValidSubtopic(jq(this)))
            {
                jq(this).show();
                jq(this).attr('available', 'true');

                if (isSelectedSubtopics)
                {
                    jq(this).attr('selected', '');
                }
            }
            else
            {
                jq(this).hide();
                jq(this).attr('available', 'false');
                
                if (isSelectedSubtopics)
                {
                    jq(this).attr('selected', 'selected');
                }

            }

        }
    ) 

    if (isSelectedSubtopics)
    {
        inout_moveKeywords('extension_subtopics','extension_subtopics_options','extension_subtopics')
        v.children("option").each(
            function () {
                jq(this).attr('selected', 'selected');
            }
        );
    }
}



function fiddleExtensionTopics() {
    
    var extension_topics = jq('#extension_topics');
    var extension_subtopics = jq('#extension_subtopics');
    var extension_topics_options = jq('#extension_topics_options');
    var extension_subtopics_options = jq('#extension_subtopics_options');
    
    if (extension_topics && extension_subtopics && extension_topics_options && extension_subtopics_options)
    {
        hideInvalidSubtopics(extension_subtopics)
        hideInvalidSubtopics(extension_subtopics_options)

        createOptGroup(extension_topics_options);
        createOptGroup(extension_topics);
        createOptGroup(extension_subtopics_options);
        createOptGroup(extension_subtopics);
    }

}

function getOptGroup(s, t) {
    return s.children("optgroup[label='" + t + "']");
}

function isSubTopic(o) {
    return (o.parent("select").attr('id').indexOf('subtopics') > 0);
}

function createOptGroup(box) {

    box.children("option").each (
        function () {
            var topic = "";
            var subtopic = "";
                        
            if (isSubTopic(jq(this)))
            {
                topic = getL2Topic(jq(this).val());
                subtopic = getL2SubTopic(jq(this).val());
            }
            else
            {
                topic = getL1Topic(jq(this).val());
                subtopic = getL1SubTopic(jq(this).val());
            }

            jq(this).text( subtopic );
            var select_box = jq(this).parent("select");
            var optgroup = getOptGroup(select_box, topic);
            

            if (!optgroup.size()) {
                select_box.append("<optgroup label=\"" + topic + "\"></optgroup>");
                optgroup = getOptGroup(select_box, topic);
            }

            optgroup.append(this);

        }
    );

    box.children("optgroup").each (
        function () {

            if (! jq(this).children("option").size())
            {
                jq(this).remove();
            }
            else 
            {
                if( ! isSubTopic(jq(this)) || jq(this).children("option[available='true']").size())
                {
                    jq(this).show();
                    jq(this).attr('available', 'true');       
                    jq(this).children("option").sortElements(
                        function(a, b){
                            return $(a).val() > $(b).val() ? 1 : -1;
                        });

                }
                else
                {
                    jq(this).hide();
                    jq(this).attr('available', 'false');       
                }
            }
        }
    );
    
    box.children("optgroup").sortElements(
        function(a, b){
            return $(a).attr('label') > $(b).attr('label') ? 1 : -1;
    });
    
    setSize(box);

}

function setSize(o) {
    var count = o.children("optgroup[available='true']").size() + o.find("option[available='true']").size();
    count = count > 6 ? count : 6;
    o.attr('size', count);
    o.css('padding', '5px 8px 5px 8px');
}

jq(document).ready(
    function() {
        
        fiddleExtensionTopics();

        jq('#extension_topics_options').dblclick(
            function() {
                fiddleExtensionTopics();
            }
        );

        jq('#extension_topics').dblclick(
            function() {
                fiddleExtensionTopics();
            }
        );

        jq('#extension_subtopics_options').dblclick(
            function() {
                fiddleExtensionTopics();
            }
        );

        jq('#extension_subtopics').dblclick(
            function() {
                fiddleExtensionTopics();
            }
        );
    
        // Handle the buttons

        // button >>        
        jq('#archetypes-fieldname-extension_topics input:button').click(
            function() {
                fiddleExtensionTopics();
            }
        );

        jq('#archetypes-fieldname-extension_subtopics input:button').click(
            function() {
                fiddleExtensionTopics();
            }
        );


    }
);

