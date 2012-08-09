jq(document).ready(function() {
    jq(".contentLeadImageContainer a#parent-fieldname-leadImage").each(
        function () {
            var href = jq(this).attr('href');
            if (href.indexOf('image_view_fullscreen') >= 0)
            {
                href = href.replace('image_view_fullscreen', 'image_galleryzoom');
                jq(this).attr('href', href);
                jq(this).addClass('fancybox');
            }
        }
    );

    jq(".fancybox").fancybox({'type' : 'image'});
});

