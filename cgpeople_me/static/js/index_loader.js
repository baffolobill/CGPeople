yepnope([
    {
        load: [
            MEDIA_URL + 'js/libs/handlebars-0.9.0.pre.5.js',
            MEDIA_URL + 'js/libs/leaflet.js'
        ],
        complete: function() {
            yepnope(MEDIA_URL + 'js/index.js');
        }
    }
]);
