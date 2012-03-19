function reset_form(selector) {
    $(':input', selector)
     .not(':button, :submit, :reset, :hidden')
     .val('')
     .removeAttr('checked')
     .removeAttr('selected');
    $('.field_error, .non_field_error', selector).remove();
    $('.error', selector).removeClass('error');
}

function clear_form_errors(selector) {
    $('.field_error, .non_field_error', selector).remove();
    $('.error', selector).removeClass('error');
}

