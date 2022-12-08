$(function() {

    const url = window.location.href
    const button = $("#question-submit");

    $("#question-form").submit(function() {
        $(this).find(':input[type=submit]').prop('disabled', true);
    });

});