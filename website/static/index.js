// (async function() {
//     const data = [
//       { year: 2010, count: 10 },
//       { year: 2011, count: 20 },
//       { year: 2012, count: 15 },
//       { year: 2013, count: 25 },
//       { year: 2014, count: 22 },
//       { year: 2015, count: 30 },
//       { year: 2016, count: 28 },
//     ];
  
//     new Chart(
//       document.getElementById('acquisitions'),
//       {
//         type: 'bar',
//         data: {
//           labels: data.map(row => row.year),
//           datasets: [
//             {
//               label: 'Acquisitions by year',
//               data: data.map(row => row.count)
//             }
//           ]
//         }
//       }
//     );
//   })();

$(document).ready(function() {
    const requestTable = document.getElementById('requests-table');
    let requesttable = new simpleDatatables.DataTable(requestTable);
})


var getrequestperdaydata = $.get('/admin/requests_per_day_data')
var ctxreqPerDay = document.getElementById("requestsPerDay").getContext('2d');
var count = []
var dates = []
getrequestperdaydata.done(function (data) {
    data.forEach(element => {
        count.push(element["count"])
        dates.push(element["date"])
    });
    window.myreqdayChart = new Chart(ctxreqPerDay, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: "Requests Per Day",
                lineTension: 0.3,
                backgroundColor: "rgba(78, 115, 223, 0.05)",
                borderColor: "rgba(78, 115, 223, 1)",
                pointRadius: 3,
                pointBackgroundColor: "rgba(78, 115, 223, 1)",
                pointBorderColor: "rgba(78, 115, 223, 1)",
                pointHoverRadius: 3,
                pointHoverBackgroundColor: "rgba(78, 115, 223, 1)",
                pointHoverBorderColor: "rgba(78, 115, 223, 1)",
                pointHitRadius: 10,
                pointBorderWidth: 2,
                data: count,
            }],
        },
        options : {
            responsive: true, 
            maintainAspectRatio: false,
            legend: {
                position: 'bottom',
                labels : {
                    padding: 10,
                    fontColor: '#1d7af3',
                }
            },
            tooltips: {
                bodySpacing: 4,
                mode:"nearest",
                intersect: 0,
                position:"nearest",
                xPadding:10,
                yPadding:10,
                caretPadding:10
            },
            layout:{
                padding:{left:15,right:15,top:15,bottom:15}
            }
        }
    });

})

function hourschart(){
    var getrequestperhourdata = $.get('/admin/requests_per_hour_data')
    var ctxreqPerHour = document.getElementById("requestsPerHour").getContext('2d');
    var count = []
    var hour = []
    getrequestperhourdata.done(function (data) {
        data.forEach(element => {
            count.push(element["count"])
            hour.push(element["hour"])
        });
        window.myreqhourChart = new Chart(ctxreqPerHour, {
            type: 'line',
            data: {
                labels: hour,
                datasets: [{
                    label: "Requests Per Hour",
                    lineTension: 0.3,
                    backgroundColor: "rgba(78, 115, 223, 0.05)",
                    borderColor: "rgba(78, 115, 223, 1)",
                    pointRadius: 3,
                    pointBackgroundColor: "rgba(78, 115, 223, 1)",
                    pointBorderColor: "rgba(78, 115, 223, 1)",
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: "rgba(78, 115, 223, 1)",
                    pointHoverBorderColor: "rgba(78, 115, 223, 1)",
                    pointHitRadius: 10,
                    pointBorderWidth: 2,
                    data: count,
                }],
            },
            options : {
				responsive: true, 
				maintainAspectRatio: false,
				legend: {
					position: 'bottom',
					labels : {
						padding: 10,
						fontColor: '#1d7af3',
					}
				},
				tooltips: {
					bodySpacing: 4,
					mode:"nearest",
					intersect: 0,
					position:"nearest",
					xPadding:10,
					yPadding:10,
					caretPadding:10
				},
				layout:{
					padding:{left:15,right:15,top:15,bottom:15}
				}
			}
        });
    
    })
}

function getStatistics(){
    var getsitestatistics = $.get('/admin/site_statistics_data')
    getsitestatistics.done(function (data) {
       
        console.log(data["total_requests"])
        $("#customers").text(data["total_requests"])
    })
}
setTimeout(hourschart,500)
setTimeout(getStatistics,1000)