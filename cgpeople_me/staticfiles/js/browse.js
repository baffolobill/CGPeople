var url = '/api/v1/profile/';
show_members(url);

function show_members(url) {
    var members = $.get(url, {
        format: 'json'
    }, function(data) {
        var source = $('#member_profile_template').html(),
            template = Handlebars.compile(source);
        $('#members').html(template(data));
        if (data.meta.next != null) {
            create_button('next', data.meta.next);
        } else {
            hide_button('.next');
        }
        if (data.meta.previous != null) {
            create_button('previous', data.meta.previous);
        } else {
            hide_button('.previous');
        }
    });
}

function create_button(text, url, attachment) {
    var button = $('#controls .' + text);

    button.addClass(text).text(text);
    button.attr('href', url);
    button.show();
}

function hide_button(selector) {
    $(selector).hide();
}

$('.next, .previous').live('click', function(e) {
    e.preventDefault();
    var url = $(this).attr('href');
    show_members(url);
    document.getElementById('members').scrollIntoView();
});

Handlebars.registerHelper('truncateString', function(string, maxlen) {
    var maxlen = parseInt(Handlebars.Utils.escapeExpression(maxlen)),
        retval = Handlebars.Utils.escapeExpression(string);

    if (retval.length > maxlen) {
        retval = retval.substring(0, maxlen) + '&hellip;';
    }

    return new Handlebars.SafeString(retval);
});
