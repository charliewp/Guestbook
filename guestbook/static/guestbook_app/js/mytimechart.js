var data = {
    // Labels should be Date objects
    labels: {{ labels }},
    datasets: [{
        fill: false,
        label: 'Page Views',
        data: {{ values }},
        borderColor: '#fe8b36',
        backgroundColor: '#fe8b36',
        lineTension: 0,
    }]
};
var options = {
    type: 'line',
    data: data,
    options: {
        fill: false,
        responsive: true,
        scales: {
            xAxes: [{
                type: 'time',
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: "Date",
                }
            }],
            yAxes: [{
                ticks: {
                    beginAtZero: true,
                },
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: "Page Views",
                }
            }]
        }
    }
};
var ctx = document.getElementById('myChart').getContext('2d');
var chart = new Chart(ctx, options);
