$(function() {
    update_unread_count();
});

function update_unread_count() {
    //console.log('update_unread_count');
    var messages = $.ajax({
        url: '/messages/count/'
    }).success(function(data) {
        if (data.unread > 0) {
            $('span', '#messages_button').remove();
            $('<span/>').attr('title', 'unread').text(data.unread).appendTo('#messages_button');
        } else {
            $('span', '#messages_button').remove();
        }
    }).complete(function(){ setTimeout(update_unread_count, 1000*30); });
}

