function show_map(latitude, longitude) {
    var map = new L.Map('geo_wrapper'),
        cloudmadeURL = 'http://{s}.tile.cloudmade.com/7480e4f340004f308c3dbe4db0806773/997/256/{z}/{x}/{y}.png',
        cloudmadeAttrib = 'Map data &copy; 2012 OpenStreetMap contributors, Imagery &copy; 2012 CloudMade',
        cloudmade = new L.TileLayer(cloudmadeURL, {maxZoom: 10, attribution: cloudmadeAttrib}),
        pos = new L.LatLng(parseFloat(latitude), parseFloat(longitude)),
        marker_image = L.Icon.extend({
            iconUrl: MEDIA_URL + 'img/marker.png',
            shadowUrl: MEDIA_URL + 'img/shadow.png',
            iconSize: new L.Point(30,44),
            shadowSize: new L.Point(30,46),
            iconAnchor: new L.Point(15,44),
            popupAnchor: new L.Point(0,-32)
        }),
        icon = new marker_image(),
        marker = new L.Marker(pos, {icon: icon});

    map.addLayer(cloudmade).setView(pos, 10).addLayer(marker);
}

$(function() {
    var $geo = $('#geo_wrapper');
    show_map($geo.data('latitude'), $geo.data('longitude'));
    $("textarea").autoResize();

    $('#available a').live('click', function(e) {
        e.preventDefault();
        $('#message').prev('button').trigger('click');
        return false;
    });

    $('.show_message_form').click(function() {
        $('#message').show();
        document.getElementById('id_message').scrollIntoView();
        $("#message form input:not(:hidden):first").focus();
    });

    $('#message .negative').live('click', function(e){
        //console.log('negative');
        e.preventDefault();
        reset_form('#message');
        $("#message").hide().prev('button').show();
    });

    $('#message form').live('submit', function(e) {
        e.preventDefault();
        var url = $(this).attr('action'),
            self = $(this),
            btn = ajax_start(self),
            message = $.ajax({
                url: url,
                data: {
                    sender_name: self.find('#id_name').val(),
                    sender_email: self.find('#id_email').val(),
                    message: self.find('#id_message').val(),
                    csrfmiddlewaretoken: self.find('input[name=csrfmiddlewaretoken]').val(),
                    user_id: self.find('#id_user_id').val(),
                    winnie_the_pooh: self.find('input[name=winnie_the_pooh]').val()
                },
                type: 'POST'
            }).error(function(data) {
                $.jGrowl("There was a problem sending your message. Please try again.", {life: 5000, header: 'Error'});
                return false;
            }).success(function(data) {
                if (data.success) {
                    $.jGrowl(data.message, {header: 'Success', life: 5000});
                    //self.find('.negative').trigger('click');
                    reset_form('#message');
                    $("#message").hide().prev('button').show();
                } else {
                    try {
                        if (data.field_errors || data.non_field_errors) {
                            self.find('.field_error').remove();
                            self.find('.error').removeClass('error');

                            $.each(data.field_errors, function(index, value) {
                                var label = $('label[for=id_' + index + ']'),
                                    error = $('<span>' + value + '</span>'),
                                    fieldset = $('#' + index + '_fieldset');
                                fieldset.addClass('error');
                                error.addClass('error field_error').appendTo(label).text(value);
                            });

                            $.each(data.non_field_errors, function(index, value) {
                                var error = $('<p>' + value + '</p>');
                                error.addClass('error non_field_error').prependTo(self).text(value);
                            });
                        }
                    } catch (e) { ajax_complete(btn); }
                }
            }).complete(function(){ ajax_complete(btn); });
    });

    $('.site .controls').live('click', function(e) {
        e.preventDefault();

        $(this).siblings('div').find('.description').toggle();
        $(this).toggleClass('minus');
    });

});
