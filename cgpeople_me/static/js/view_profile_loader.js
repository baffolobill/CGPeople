yepnope([
    {
        load: [
            MEDIA_URL + 'js/libs/autoresize.jquery.min.js',
            MEDIA_URL + 'js/libs/leaflet.js',
        ],
        complete: function() {
            yepnope(MEDIA_URL + 'js/view_profile.js?5');
        }
    }
]);
