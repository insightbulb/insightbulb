$(function () {
    $('#help-modal').on('click', function () {
        $('#welcome-modal').modal('show');
    });
});


$(function () {
    $('#myModal').on('click', function () {
        $('#welcome-modal').hide();
    });
});

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

// Tide extrema
$(function () {
    $('a#show-times').on('click', function () {
        $.getJSON('/show-tide-extrema',
            function (data) {
                //do nothing
            });
        window.location.reload();
        return false;
    });
});

// Display arrows next to tide data
$(function(){
    $('.tide-extrema-data').each(function(index) {
        if ($(this).text().indexOf('high') >= 0) {
            $(this).next().children().addClass('fas fa-chevron-circle-up');
        }
        else {
            $(this).next().children().addClass('fas fa-chevron-circle-down');
        }
    })
})

// Get region location from dropdown and append it to tidal information
$(function () {
    $('.region').on('click', function (e) {
        var name = e.currentTarget;

        var station_data = [];
        station_data.push(name.getAttribute("data-name").replace(/ .*/, ''));
        station_data.push(name.getAttribute("data-name"));

        var $region = $('.current_region');

        $region.html('');
        $region.append(name.getAttribute("data-name"));
        $(".graph-title").html(name.getAttribute("data-name"));

        $.ajax({
            type: "POST",
            contentType: "application/json;charset=utf-8",
            url: "/",
            traditional: "true",
            data: JSON.stringify({station_data: station_data}),
            dataType: "json"
        });
        $('#station-loader').show();
        setTimeout(function () {
            $('#station-loader').hide();
            $('#station-success').show();
            window.location.reload();
        }, 8000);
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
        var data = [];
        $("#tide-table tr").each(function () {
            data.push($(this).find(".tide-extrema-data").html());
        });

        // This loop is a little strange as the data we pull from the html is a string
        // What we do then is map all digits from the string into an array
        // The n and n-1 indices contain the sig-figs of the height, so the third
        // line of the loop gives our value after a division of 100
        var count = 0;
        var height_points = [];
        var time_points = [];
        for (let i = 0; i < 4; i++) {
            var tide_height = data[i];
            var parsed_values = tide_height.match(/\d+/g).map(Number);
            height_points.push(((parsed_values[2] * 100) + parsed_values[3]) / 100.0);

            // Here we simply add the times to an array, we splice in a zero
            // to keep proper format
            var min = "";
            parsed_values[1] < 10 ? min = "0" + parsed_values[1].toString() : min = parsed_values[1].toString();
            if (count < 2) {
                time_points.push(parsed_values[0].toString() + ":" + min + " AM")
            } else {
                time_points.push(parsed_values[0].toString() + ":" + min + " PM")
            }
            count++;
        }
        console.log(time_points);

        var ctxL = document.getElementById("lineChart").getContext('2d');
        var myLineChart = new Chart(ctxL, {
            type: 'line',
            data: {
                labels: [time_points[0], time_points[1], time_points[2], time_points[3]],
                datasets: [{
                    label: "Predicted tide heights",
                    data: [height_points[0], height_points[1], height_points[2], height_points[3]],
                    backgroundColor: [
                        'rgba(105, 0, 132, .2)',
                    ],
                    borderColor: [
                        'rgba(200, 99, 132, .7)',
                    ],
                    borderWidth: 2
                },
                    // {
                    //     label: "Actual",
                    //     data: [0.87, 1.15, 1.08, 0.71],
                    //     backgroundColor: [
                    //         'rgba(0, 137, 132, .2)',
                    //     ],
                    //     borderColor: [
                    //         'rgba(0, 10, 130, .7)',
                    //     ],
                    //     borderWidth: 2
                    // }
                ]
            },
            options: {
                responsive: true
            }
        });
    });
});
