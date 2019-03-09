var script = document.createElement('script');
script.src = 'http://code.jquery.com/jquery-1.11.0.min.js';
script.type = 'text/javascript';
document.getElementsByTagName('head')[0].appendChild(script);

// Turn on
$(function () {
    $('a#turn-on').on('click', function () {
        $.getJSON('/turn-on',
            function (data) {
                //do nothing
            });
        return false;
    });
});

// Turn off
$(function () {
    $('a#turn-off').on('click', function () {
        $.getJSON('/turn-off',
            function (data) {
                //do nothing
            });
        return false;
    });
});

// Flow
$(function () {
    $('a#flow').on('click', function () {
        $.getJSON('/flow',
            function (data) {
                //do nothing
            });
        return false;
    });
});
