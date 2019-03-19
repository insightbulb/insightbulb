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

$(function () {
    $('a.dropdown-item').on('click', function (e) {
        var name = e.currentTarget;
        console.log(name.getAttribute("data-name"));
    });
});

$(function () {
    $(document).ready(function () {
        $('.dropdown-submenu a.station').on("click", function (e) {
            $(this).next('ul').toggle();
            e.stopPropagation();
            e.preventDefault();
        });
    });
});
