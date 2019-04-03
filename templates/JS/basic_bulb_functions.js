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

// Get region location from dropdown and append it to tidal information
$(function () {
    $('.region').on('click', function (e) {
        var name = e.currentTarget;
        var test_val = name.getAttribute("data-name").replace(/ .*/,'');
        var $region = $('.current_region');

        $region.html('');
        $region.append(name.getAttribute("data-name"));

        $.ajax({
            type: "POST",
            contentType: "application/json;charset=utf-8",
            url: "/",
            traditional: "true",
            data: JSON.stringify({test_val}),
            dataType: "json"
        });
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

// TODO: Probably use ajax requests to get the data for the graphs
// A dummy template for how the tide data will be graphed
$(function () {
    $(document).ready(function () {
        //line
        var ctxL = document.getElementById("lineChart").getContext('2d');
        var myLineChart = new Chart(ctxL, {
            type: 'line',
            data: {
                labels: ["January", "February", "March", "April", "May", "June", "July"],
                datasets: [{
                    label: "My First dataset",
                    data: [65, 59, 80, 81, 56, 55, 40],
                    backgroundColor: [
                        'rgba(105, 0, 132, .2)',
                    ],
                    borderColor: [
                        'rgba(200, 99, 132, .7)',
                    ],
                    borderWidth: 2
                },
                    {
                        label: "My Second dataset",
                        data: [28, 48, 40, 19, 86, 27, 90],
                        backgroundColor: [
                            'rgba(0, 137, 132, .2)',
                        ],
                        borderColor: [
                            'rgba(0, 10, 130, .7)',
                        ],
                        borderWidth: 2
                    }
                ]
            },
            options: {
                responsive: true
            }
        });
    });
});
