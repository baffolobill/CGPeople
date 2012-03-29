yepnope([
    {
        load: [
            MEDIA_URL + 'js/libs/handlebars-0.9.0.pre.5.js',
            //MEDIA_URL + 'js/lib/jquery.history.js',
            MEDIA_URL + 'js/app.js',
            MEDIA_URL + 'js/libs/autoresize.jquery.min.js'
        ],
        complete: function() {
            yepnope(MEDIA_URL + 'js/messages.js');
        }
    }
]);
