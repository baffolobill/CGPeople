var appMessage;

function show_map() {
    var map = new L.Map('geo_wrapper'),
        cloudmadeURL = 'http://{s}.tile.cloudmade.com/7480e4f340004f308c3dbe4db0806773/997/256/{z}/{x}/{y}.png',
        cloudmadeAttrib = 'Map data &copy; 2011 OpenStreetMap contributors, Imagery &copy; 2011 CloudMade',
        cloudmade = new L.TileLayer(cloudmadeURL, {maxZoom: 18, attribution: cloudmadeAttrib}),
        existing_lat = parseFloat($('#id_latitude').val()),
        existing_long = parseFloat($('#id_longitude').val()),
        marker_image = L.Icon.extend({
            iconUrl: MEDIA_URL + 'img/marker.png',
            shadowUrl: MEDIA_URL + 'img/shadow.png',
            iconSize: new L.Point(30,44),
            shadowSize: new L.Point(30,46),
            iconAnchor: new L.Point(15,44),
            popupAnchor: new L.Point(0,-32)
        }),
        icon = new marker_image();

    map.addLayer(cloudmade);

    if (existing_lat && existing_long && existing_lat != 0 && existing_long != 0) {
        var pos = new L.LatLng(existing_lat, existing_long),
            marker = new L.Marker(pos, {draggable: true, icon: icon});
        map.setView(pos, 13).addLayer(marker);

        marker.on('dragend', function(e) {
            update_location_form(e.target._latlng.lat, e.target._latlng.lng);
            update_profile_location();
        });
    } else {
        map.locateAndSetView();
    }

    map.on('locationfound', onLocationFound);

    function onLocationFound(e) {
        var marker = new L.Marker(e.latlng, {draggable: true, icon: icon});
        map.addLayer(marker);

        update_location_form(e.latlng.lat, e.latlng.lng);
        update_profile_location();

        marker.on('dragend', function(e) {
            update_location_form(e.target._latlng.lat, e.target._latlng.lng);
        });
    }

    map.on('locationerror', onLocationError);

    function onLocationError(e) {
        yepnope([
            {
                load: MEDIA_URL + 'js/libs/geofill.js',
                complete: function() {
                    geofill.find({
                        latitude: 'id_latitude',
                        longitude: 'id_longitude',
                        callback: function(o) {
                            show_map();
                        }
                    });
                }
            }
        ]);
    }
}

function update_location_form(lat, long) {
    $('#id_latitude').val(lat);
    $('#id_longitude').val(long);
}

function update_profile_location(position) {
    var $form = $('#id_latitude').closest('form'),
        update_location = $.ajax({
            url: $form.attr("action"),
            data: {
                csrfmiddlewaretoken: $form.find('input[name=csrfmiddlewaretoken]').val(),
                latitude: $form.find('#id_latitude').val(),
                longitude: $form.find('#id_longitude').val()
            },
            type: 'POST',
            success: function(data) {
                if (data.success) {
                    $.jGrowl(data.success, {life: 5000, header: 'Success'});
                } else {
                    $.jGrowl(data.errors, {life: 5000, header: 'Error'});
                }
            }
        });
}

$(function() {
    $('#id_skills').tagsInput({
        defaultText: 'add a skill',
        autocomplete_url: '/profile/skills/',
        autocomplete:{
            selectFirst: true,
            width: '100px',
            autoFill: true
        }
    });

    $('#id_update_location').live('click', function(e) {
        e.preventDefault();

        $(this).attr('disabled', 'disabled').removeClass('positive').addClass('negative');
        update_profile_location();
        $(this).removeAttr('disabled').removeClass('negative').addClass('positive');

        return false;
    });

    $('button.delete_site').live('click', function(event) {
        event.preventDefault();
        var link = $(this).data('url'),
            $parent = $(this).parent();
        $(this).remove();
        $parent.html(
            '<button data-url="' + link + '" class="delete_confirmed">Destroy</button> <button href="" class="cancel_delete right">Cancel</button>');
    });

    $('button.cancel_delete').live('click', function(event) {
        event.preventDefault();
        var link = $(this).siblings('a')[0],
            $parent = $(this).parent();
        $(this).remove();
        $parent.html('<button data-url="' + link + '" class="delete_site right">Delete</button>');
    });

    $('button.delete_confirmed').live('click', function(event) {
        event.preventDefault();
        var link = $(this).data('url'),
            self = $(this),
            ajax_delete = $.ajax({
                url: link
            }).success(function() {
               self.closest('article').remove();
            });
    });

    /* Adding and editing new sites */
    $('#add_site').click(function(e) {
        e.preventDefault();
        var form = $('#add_site_template form').clone();
        form.insertBefore($(this));
        $('textarea').autoResize();
        $(this).hide();
    });

    $('.add_site_form').live('submit', function(e) {
        e.preventDefault();
        var url = $(this).attr('action'),
            $form = $(this),
            site = $.ajax({
                url: url,
                data: {
                    title: $form.find('#id_site_title').val(),
                    url: $form.find('#id_site_url').val(),
                    description: $form.find('#id_site_description').val(),
                    csrfmiddlewaretoken: $form.find('input[name=csrfmiddlewaretoken]').val()
                },
                type: 'POST',
                dataType: 'json'
            }).success(function(data) {
                if (data.success) {
                    $(data.response).insertBefore($form);
                    $form.remove();
                    $('#add_site').show();
                    $.jGrowl(data.message, {life: 5000, header: 'Success'});
                } else {
                    $.jGrowl(data.message, {life: 5000, header: 'Error'});

                    if (data.field_errors || data.non_field_errors) {
                        $form.find('.field_error').remove();
                        $form.find('.error').removeClass('error');

                        $.each(data.field_errors, function(index, value) {
                            var label = $('label[for=id_site_' + index + ']'),
                                error = $('<span>' + value + '</span>'),
                                fieldset = $('#' + index + '_fieldset');
                            fieldset.addClass('error');
                            error.addClass('error field_error').appendTo(label).text(value);
                        });

                        $.each(data.non_field_errors, function(index, value) {
                            var error = $('<p>' + value + '</p>');
                            error.addClass('error non_field_error').prependTo($form).text(value);
                        });
                    }
                }
            });
    });
    $('.add_site_form .negative').live('click', function(e) {
        e.preventDefault();
        $(this).closest('form').remove();
        $('#add_site').show();
    });
    $('.edit_site').live('click', function(e) {
        e.preventDefault();
        var form = $('#edit_site_template form').clone(),
            site = $(this).closest('article');
        form.find('#id_site_id').val(site.data('id'));
        form.find('#id_site_title').val(site.data('name'));
        form.find('#id_site_url').val(site.data('url'));
        form.find('#id_site_description').val(site.data('description'));
        form.insertAfter(site);
        site.hide();
        $('textarea').autoResize();

    });
    $('.edit_site_form .negative').live('click', function(e) {
        e.preventDefault();
        $(this).parents('form').prev('article:hidden').show().end().remove();
    });
    $('.edit_site_form').live('submit', function(e) {
        e.preventDefault();
        var url = $(this).attr('action'),
            $form = $(this),
        site = $.ajax({
            url: url,
            data: {
                id: $form.find('#id_site_id').val(),
                title: $form.find('#id_site_title').val(),
                url: $form.find('#id_site_url').val(),
                description: $form.find('#id_site_description').val(),
                csrfmiddlewaretoken: $form.find('input[name=csrfmiddlewaretoken]').val()
            },
            type: 'POST',
            dataType: 'json'
        }).success(function(data) {
            if (data.success) {
                $(data.response).insertBefore($form);
                $form.remove();
                $.jGrowl(data.message, {life: 5000, header: 'Success'});
            } else {
                $.jGrowl(data.message, {life: 5000, header: 'Error'});

                if (data.field_errors || data.non_field_errors) {
                    $form.find('.field_error').remove();
                    $form.find('.error').removeClass('error');

                    $.each(data.field_errors, function(index, value) {
                        var label = $('label[for=id_site_' + index + ']'),
                            error = $('<span>' + value + '</span>'),
                            fieldset = $('#' + index + '_fieldset');
                        fieldset.addClass('error');
                        error.addClass('error field_error').appendTo(label).text(value);
                    });

                    $.each(data.non_field_errors, function(index, value) {
                        var error = $('<p>' + value + '</p>');
                        error.addClass('error non_field_error').prependTo($form).text(value);
                    });
                }
            }
        });
    });

    $('#live_geolocation').next('form').live('submit', function(e) {
        e.preventDefault();
        e.stopPropogation();
        return false;
    });

    $('.location_search_form').live('submit', function(e) {
        e.preventDefault();
        var url = $(this).attr('action'),
            $form = $(this);
        var coords = $.ajax({
            url: url,
            data: {
                search: $form.find('#id_search').val(),
                csrfmiddlewaretoken: $form.find('input[name=csrfmiddlewaretoken]').val()
            },
            type: 'POST',
            dataType: 'json'
        }).success(function(data) {
            if (data.err) {
                $form.parent().before('<p>' + data.err + '</p>');
            } else {
                $('#id_latitude').val(data.lat);
                $('#id_longitude').val(data.lng);
                show_map();
            }
        });
    });

    $('.location_search_form .negative').live('click', function(e) {
        e.preventDefault();
        var $form = $(this).parent();
        $('#location_search').show();
        $form.remove();
    });

    $('#location_search').live('click', function(e) {
        e.preventDefault();
        var form = $('#geocode_search_template form').clone(),
            self = $(this),
            target = $(this).closest('form');
        target.parent().css('position', 'relative');
        form.insertAfter(target);
        form.css({
            position: 'absolute',
            bottom: '-1.75em',
            right: 0
        });
        self.hide();
        return false;
    });

    show_map();

    // Tweet It
    $('#tweet_it').live('click', function(e) {
        var url = $('#hide_tweet').attr('href'),
            $self = $(this);
        $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json'
        }).success(function(data) {
            if (data.success) {
                $self.parent().remove();
            }
        });
    });
    $('#hide_tweet').live('click', function(e) {
        e.preventDefault();
        var url = $(this).attr('href'),
            $self = $(this);
        $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json'
        }).success(function(data) {
            if (data.success) {
                $self.parent().remove();
            }
        });
    });

    // Profile Form
    $('#profile_form').live('submit', function(e) {
        e.preventDefault();
        clear_form_errors($(this));
        var $form = $(this),
            url = $(this).attr('action'),
            profile = $.ajax({
                url: url,
                data: {
                    csrfmiddlewaretoken: $form.find('input[name=csrfmiddlewaretoken]').val(),
                    name: $form.find('#id_name').val(),
                    bio: $form.find('#id_bio').val(),
                    email: $form.find('#id_email').val(),
                    skills: $form.find('#id_skills').val(),
                    location_description: $form.find('#id_location_description').val(),
                    available_for: $form.find('#id_available_for').val(),
                    service_facebook: $form.find('#id_service_facebook').val(),
                    service_linkedin: $form.find('#id_linkedin_username').val()
                },
                type: 'POST',
                dataType: 'json'
            }).success(function(data) {
                if (data.success) {
                    $.jGrowl(data.success, {life: 5000, header: 'Success'});
                } else {
                    if (data.field_errors || data.non_field_errors) {
                        $form.find('.field_error').remove();
                        $form.find('.error').removeClass('error');

                        $.each(data.field_errors, function(index, value) {
                            var label = $('label[for=id_' + index + ']'),
                                error = $('<span>' + value + '</span>'),
                                fieldset = $('#' + index + '_fieldset');
                            fieldset.addClass('error');
                            error.addClass('error field_error').appendTo(label).text(value);
                        });

                        $.each(data.non_field_errors, function(index, value) {
                            var error = $('<p>' + value + '</p>');
                            error.addClass('error non_field_error').prependTo($form).text(value);
                        });
                    }
                }
            });
    });
});

