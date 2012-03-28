var map;
var layers = [];
function show_map() {
    map = new L.Map('geo_wrapper'),
        cloudmadeURL = 'http://{s}.tile.cloudmade.com/7480e4f340004f308c3dbe4db0806773/997/256/{z}/{x}/{y}.png',
        cloudmadeAttrib = 'Map data &copy; 2012 OpenStreetMap contributors, Imagery &copy; 2012 CloudMade',
        cloudmade = new L.TileLayer(cloudmadeURL, {maxZoom: 10, attribution: cloudmadeAttrib}),
        world = new L.LatLng(12, 25),
        marker_image = L.Icon.extend({
            iconUrl: MEDIA_URL + 'img/marker.png',
            shadowUrl: MEDIA_URL + 'img/shadow.png',
            iconSize: new L.Point(30,44),
            shadowSize: new L.Point(30,46),
            iconAnchor: new L.Point(15,44),
            popupAnchor: new L.Point(0,-32)
        }),
        icon = new marker_image();

    map.addLayer(cloudmade).setView(world, 2);
    //map.locateAndSetView();
    add_users();

    map.on('locationfound', function(e) {
        add_users();
    });
    map.on('locationerror', function(e) {
        add_users();
    });

    function add_users() {
        var users = $.get('/api/v1/profile/', {
            format: 'json',
            limit: 500
        }).success(function(data) {
            $.each(data.objects, function(i, user) {
                var markerLocation = new L.LatLng(user['lat'], user['long']),
                    marker = new L.Marker(markerLocation, {icon: icon});

                marker.bindPopup('<a href="' + user['url'] + '">' + user['user']['name'] + '</a>');
                map.addLayer(marker);
                layers.push(marker);
            });
        });
    }
}

function remove_layers(){
    for(var i=0, l=layers.length; i<l; i++){
        map.removeLayer(layers.pop());
    }
}


$(function() {
    show_map();

    $("#search_form form").live('submit', function(e) {
        e.preventDefault();
        /*var btn = $(this).find('button');
        btn.attr('disabled', 'disabled');
        btn.wrapInner('<span/>');
        btn.append($('<img/>').attr('src', MEDIA_URL+'img/loaders/upload.gif'));*/
        var self = $(this),
            btn = ajax_start($(this)),
            url = self.attr('action'),
            search = $.ajax({
                url: url,
                type: 'POST',
                data: {
                    available_for: self.find('#id_available_for').val(),
                    location: self.find('#id_location').val(),
                    distance: self.find('#id_distance').val(),
                    skills: self.find('#id_skills').val(),
                    csrfmiddlewaretoken: self.find('input[name=csrfmiddlewaretoken]').val()
                },
                dataType: 'json',
            }).success(function(data) {
                var source = $('#search_template').html(),
                    template = Handlebars.compile(source);
                $('#results').html(template(data));

                remove_layers();

                $.each(data.objects, function(i, user) {
                    var markerLocation = new L.LatLng(user['lat'], user['long']),
                        marker = new L.Marker(markerLocation, {icon: icon});

                    marker.bindPopup('<a href="' + user['url'] + '">' + user['user']['name'] + '</a>');
                    map.addLayer(marker);
                    layers.push(marker);
                });
            }).complete(function(){
                /*btn.find('img').remove();
                btn.find('span').contents().unwrap();
                btn.removeAttr('disabled');*/
                ajax_complete(btn);
            });
    });
});

