const element = 'graph-change-over-time-container';
const data = JSON.parse(document.getElementById('graph-change-over-time-data').textContent);
const layout = JSON.parse(document.getElementById('graph-change-over-time-layout').textContent);
const config = JSON.parse(document.getElementById('graph-change-over-time-config').textContent);
Plotly.newPlot(element, data, layout, config);
