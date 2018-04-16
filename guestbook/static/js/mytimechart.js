var ctx = document.getElementById('myChart').getContext('2d');
alert("mytimechart.js just got called with " + finInst);
var myChart = new Chart(ctx, {
    type: 'line',
    data : {
    labels: {{ labels }},
    datasets: [{
        fill: false,
        label: 'Page Views',
        data: {{ values }},
        borderColor: '#fe8b36',
        backgroundColor: '#fe8b36',
        lineTension: 0,
    }]
    },
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
});
