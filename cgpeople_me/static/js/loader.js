function ajax_start(sender){
    var btn = sender.is('button') || sender.is('input[type="button"]') || sender.hasClass('button') ? sender : sender.find('button');
    btn.attr('disabled', 'disabled');
    btn.addClass('disabled');
    btn.wrapInner('<span class="no-display" />');
    btn.append($('<img/>').attr('src', MEDIA_URL+'img/loaders/upload.gif'));

    return btn;
}

function ajax_complete(sender){
    sender.find('img').remove();
    sender.find('span').contents().unwrap();
    sender.removeAttr('disabled');
    sender.removeClass('disabled');
}

yepnope([
    {
        load: 'http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js',
        callback: function(url, result, key) {
            if (!window.jQuery) {
                yepnope(MEDIA_URL + 'js/libs/jquery-1.7.1.min.js');
            }
        }
    },{
        load: [
            MEDIA_URL + 'js/libs/jquery.jgrowl_minimized.js',
            MEDIA_URL + 'js/master.js'
            //MEDIA_URL + 'js/message_counter.js'
        ],
    },{
        test: Modernizr.input.placeholder,
        nope: {
            'placeholder': MEDIA_URL + 'js/libs/jquery.placeholder.min.js',
            'placeholdercss': MEDIA_URL + 'css/fixies.css'
        },
        callback: {
            'placeholder': function(url, result, key) {
                $('input, textarea').placeholder();
            }
        }
    }
]);

