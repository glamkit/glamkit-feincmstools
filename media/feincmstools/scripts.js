(function($) {
    $(document).ready(function() {
        contentblock_init_handlers.push(function(){
            for (var content_type in content_type_collapsed_fields) {
                var collapsed_fields = content_type_collapsed_fields[content_type];
                $(".inline-related.dynamic-" + content_type + "_set:not(.more-less-powered)").each(function() {
                    $(this).addClass("more-less-powered");
                    var more_less = $("<div>").addClass("more-less").appendTo($(this));
                    var more_less_link = $("<a>").appendTo(more_less);
                    var collapsible = $("<div>").appendTo($(this));
                    for (var i = 0; i < collapsed_fields.length; i++) {
                        $(this).find(".form-row." + collapsed_fields[i]).appendTo(collapsible);
                    }
                    
                    if (collapsible.find(".errors").length > 0) {
                        toggleLinkText('less');
                    }
                    else {
                        collapsible.hide();
                        toggleLinkText('more');
                    }
                    
                    function toggleLinkText(more_or_less) {
                        if (more_or_less == undefined) {
                            more_less.hasClass('more-less-more') ? more_or_less = 'less' : more_or_less = 'more';
                        }
                        
                        if (more_or_less == 'more') {
                            more_less.addClass('more-less-more');
                            more_less.removeClass('more-less-less');
                            more_less_link.text('More...'); //TODO: Translate.
                        }
                        else {
                            more_less.addClass('more-less-less');
                            more_less.removeClass('more-less-more');
                            more_less_link.text('Less...'); //TODO: Translate.
                        }
                    }
                    
                    more_less_link.click(function() {
                        collapsible.slideToggle(300);
                        toggleLinkText();
                    });
                });
            }
        });
    });
})(feincms.jQuery);
