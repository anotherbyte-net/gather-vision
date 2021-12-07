
function createGraphChangeOverTime(data) {
    console.log(data);

    let TESTER = document.getElementById('tester');

    Plotly.newPlot( TESTER, [{

        x: [1, 2, 3, 4, 5],

        y: [1, 2, 4, 8, 16] }], {

        margin: { t: 0 } } );
}

const graphChangeOverTimeData = JSON.parse(document.getElementById('graph-change-over-time-data').textContent);
createGraphChangeOverTime(graphChangeOverTimeData);

