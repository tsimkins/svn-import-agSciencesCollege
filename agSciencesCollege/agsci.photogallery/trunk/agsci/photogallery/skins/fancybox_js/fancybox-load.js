jq(document).ready(function() {
    jq(".contentLeadImageContainer a#parent-fieldname-leadImage, .contentLeadImageContainerLeft a#parent-fieldname-leadImage, .contentLeadImageContainerFullWidth a#parent-fieldname-leadImage").each(
        function () {
            var href = jq(this).attr('href');
            if (href.indexOf('leadImage/image_view_fullscreen') >= 0)
            {
                href = href.replace('leadImage/image_view_fullscreen', 'leadImage_galleryzoom');
                jq(this).attr('href', href);
                jq(this).addClass('fancybox');
            }
            else if (href.indexOf('image_view_fullscreen') >= 0)
            {
                href = href.replace('image_view_fullscreen', 'image_galleryzoom');
                jq(this).attr('href', href);
                jq(this).addClass('fancybox');
            }
        }
    );

    if (window.innerWidth > 520)
    {
        jq(".fancybox").fancybox({'type' : 'image', 'hideOnContentClick' : true , 'closeClick' : true});
    }
    else
    {
        jq(".fancybox").fancybox({'type' : 'image', 'hideOnContentClick' : true , 'closeClick' : true, 'padding' : 0, 'margin' : 2});
    }

});


    