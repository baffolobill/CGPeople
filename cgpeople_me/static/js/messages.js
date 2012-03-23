$(function() {
    $('.message:not(.active)').live('click', function(e) {
        var message = $(this),
            full = $('.full', message),
            preview = $('.preview', message);

        message.siblings('article').find('.full').hide().end().find('.preview').show().end().removeClass('active').end().addClass('active');
        preview.hide();
        full.show();
        window.history.pushState('', 'Title', '/messages/#' + message.attr('id'));
    });

    $('.full form').live('click', function(e) {
        e.preventDefault();
    });

    $('.hide').live('click', function(e) {
        e.preventDefault();
        $('.message_form form', this).remove();
        $(this).closest('article').hide().siblings('.preview').show();
        $(this).closest('.message').removeClass('active');
        window.history.pushState('', 'Title', '/messages/');
    });

    $('button.archive').live('click', function(e) {
        if (!$(this).data('read')) {
            var $parent = $(this).parents('.message'),
                url = $(this).data('url'),
                read = $.ajax({
                    url: url,
                    type: 'GET',
                    dataType: 'json'
                }).success(function(data) {
                    if (data.success) {
                        var clone = $parent.clone();
                        clone.find('button.archive').remove();
                        clone.removeClass('active');
                        clone.find('.full').hide().end().find('.preview').show();
                        clone.prependTo('#read_messages');

                        $parent.fadeOut(200, function() {
                            $parent.remove();
                            update_unread_count();
                        });
                        window.history.pushState('', 'Title', '/messages/');
                    } else {
                        $.jGrowl(data.message, {life: 5000, header: 'Error'});
                    }
                });
        }

    });

    $('button.delete').live('click', function(event) {
        event.preventDefault();
        var link = $(this).data('url'),
            $parent = $(this).parent();
        $(this).remove();
        $parent.append(
            '<button class="cancel_delete right">Cancel</button> <button data-url="' + link + '" class="delete_confirmed negative"><span class="trash icon"></span>Destroy</button>');
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
            ajax_delete = $.ajax({
                url: link
            }).success(function(data) {
                if (data.success) {
                    $parent.fadeOut(200, function() {
                        $parent.remove();
                        update_unread_count();
                    });
                } else {
                    $.jGrowl(data.message, {life: 5000, header: 'Error'});
                }
            });
    });

    $('.message_form form button.negative').live('click', function(e) {
        e.preventDefault();

        var $form = $(this).parents('form');

        reset_form($form);
        $form.closest('article').find('.hide').trigger('click');
    });

    $('.message_form form button.positive').live('click', function(e) {
        e.preventDefault();
        var $form = $(this).parents('form'),
            url = $form.attr('action'),
            message = $.ajax({
                url: url,
                data: {
                    sender_name: $form.find('#id_name').val(),
                    sender_email: $form.find('#id_email').val(),
                    message: $form.find('#id_message').val(),
                    csrfmiddlewaretoken: $form.find('input[name=csrfmiddlewaretoken]').val(),
                    user_id: $form.find('#id_user_id').val(),
                    winnie_the_pooh: $form.find('input[name=winnie_the_pooh]').val()
                },
                type: 'POST'
            }).success(function(data) {
                if (data.success) {
                    $.jGrowl(data.message, {life: 5000, header: 'Success'});
                    reset_form($form);
                    $form.closest('article').find('.hide').trigger('click');
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
            });
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
