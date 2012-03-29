$(function() {
    $('#unreadTab .message__body, #archiveTab .message__body').live('click', function(e) {
        var url = $(this).parents('.message').data('url'),
            $tabs = $('ul.tabs'),
            view_msgs = $.ajax({
                url: url,
                type: 'GET',
                dataType: 'json'
            }).success(function(data) {
                if (data.success) {
                    $('#view_messages').html(data.html);
                    $tabs.find('#view-tab-item').show().find('a').trigger('click');

                    $('#id_message').autoResize();
                    $('#id_message').keydown();

                    update_unread_count();
                } else {
                    $.jGrowl(data.error, {life: 5000, header: 'Error'});
                }
            });
    });

    $('button.archive').live('click', function(event){
        event.preventDefault();
        var $parent = $(this).parents('.message'),
            url = $(this).data('url'),
            archive = $.ajax({
                url: url,
                type: 'GET',
                dataType: 'json'
            }).success(function(data) {
                if (data.success) {
                    var clone = $parent.clone();
                    clone.find('button.archive').remove();
                    clone.prependTo('#archived_messages');

                    $parent.fadeOut(200, function() {
                        $parent.remove();
                        if (!$('#unread_messages>.message').length){
                            $('#unread_messages>.no-messages').show();
                        }
                        if ($('#archived_messages>.message').length){
                            $('#archived_messages>.no-messages').hide();
                        }
                        update_unread_count();
                    });
                    //window.history.pushState('', 'Title', '/messages/');
                } else {
                    $.jGrowl(data.error, {life: 5000, header: 'Error'});
                }
            });
        return false;
    });

    $('button.delete').live('click', function(event) {
        event.preventDefault();
        var link = $(this).data('url'),
            $parent = $(this).parent();
        $(this).remove();
        $parent.append('<button class="cancel_delete right">Cancel</button> <button data-url="' + link + '" class="delete_confirmed negative"><span class="trash icon"></span>Destroy</button>');
    });

    $('button.cancel_delete').live('click', function(event) {
        event.preventDefault();
        var link = $(this).next('button').data('url'),
            $parent = $(this).parent();
        $parent.find('button.cancel_delete, button.delete_confirmed').remove();
        $parent.append(
		    '<button data-url="' + link + '" class="delete button negative right"><span class="icon trash" title="Delete message"></span>Delete</button>');
    });

    $('button.delete_confirmed').live('click', function(event) {
        event.preventDefault();
        var link = $(this).data('url'),
            $parent = $(this).parents('article'),
            btn = ajax_start($(this)),
            ajax_delete = $.ajax({
                url: link
            }).success(function(data) {
                if (data.success) {
                    $parent.fadeOut(200, function() {
                        $parent.remove();
                        if (!$('#unread_messages>.message').length){
                            $('#unread_messages>.no-messages').show();
                        }
                        if (!$('#archived_messages>.message').length){
                            $('#archived_messages>.no-messages').show();
                        }
                        update_unread_count();
                    });
                } else {
                    $.jGrowl(data.message, {life: 5000, header: 'Error'});
                }
            }).complete(function(){ ajax_complete(btn); });
    });



    $('.message_form form button.positive').live('click', function(e) {
        e.preventDefault();
        var $form = $(this).parents('form'),
            url = $form.attr('action'),
            btn = ajax_start($form),
            message = $.ajax({
                url: url,
                data: {
                    message: $form.find('#id_message').val(),
                    csrfmiddlewaretoken: $form.find('input[name=csrfmiddlewaretoken]').val(),
                    winnie_the_pooh: $form.find('input[name=winnie_the_pooh]').val()
                },
                type: 'POST'
            }).success(function(data) {
                if (data.success) {
                    $.jGrowl(data.message, {life: 5000, header: 'Success'});
                    reset_form($form);
                    $('#message_list').append(data.html);
                    $('#id_message').keydown();
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
                            error.addClass('error non_field_error').prependTo(self).text(value);
                        });
                    }
                }
            }).error(function(data) {
                $.jGrowl("There was a problem sending your message. Please try again.", {life: 5000, header: 'Error'});
                return false;
            }).complete(function(){ ajax_complete(btn); });
    });

    /*$.history.init(function(hash) {
        if (hash == '') {
        } else {
            var message = $('#' + hash),
                read = $('a[href=#read]'),
                unread = $('a[href=#unread]');

            if (message.parent().attr('id') == 'read_messages') {
                read.trigger('click');
            } else {
                unread.trigger('click');
            }

            $('#' + hash).find('.preview').trigger('click');
        }
    });*/
});
