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
    const requestsTable = document.getElementById('requests-table');
    let requestsTableInstance = new simpleDatatables.DataTable(requestsTable);

    $(".ban-checkbox, .requestban-checkbox").change(function () {
        var userId = $(this).data("user-id");
        var isBan = $(this).hasClass("ban-checkbox");

        var updateData = {
            ban: isBan ? this.checked : $(".ban-checkbox[data-user-id='" + userId + "']").prop("checked"),
            notesban: !isBan ? this.checked : $(".requestban-checkbox[data-user-id='" + userId + "']").prop("checked")
        };

        updateData.ban = updateData.ban === true || updateData.ban === "true";
        updateData.notesban = updateData.notesban === true || updateData.notesban === "true";

        $.ajax({
            url: "/admin/update_user/" + userId,
            type: "PUT",
            contentType: "application/json",
            data: JSON.stringify(updateData),
            success: function(response) {
                alert(response.message);
            },
            error: function(xhr, status, error) {
                console.error("Failed to update user details:", error);
            }
        });
    });
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

function fillMissingHours(data) {
    var counts = data.map(entry => entry.count);
    var hours = data.map(entry => entry.hour);

    var allHours = Array.from({ length: 24 }, (_, i) => i)
        .map(hour => hour.toString().padStart(2, '0') + ':00:00');

    var resultCounts = [];
    var resultHours = [];
    allHours.forEach(function (hour) {
        var index = hours.findIndex(entryHour => entryHour.endsWith(hour));
        resultCounts.push(index !== -1 ? counts[index] : 0);
        resultHours.push(hour);
    });
    return { counts: resultCounts, hours: resultHours };
}

function hourschart(){
    var getrequestperhourdata = $.get('/admin/requests_per_hour_data')
    var ctxreqPerHour = document.getElementById("requestsPerHour").getContext('2d');
    getrequestperhourdata.done(function (data) {
        var processedData = fillMissingHours(data);
        var count = processedData["counts"]
        var hour = processedData["hours"]

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
                },
                scales: {
                    y: {
                        min: 0,
                        ticks: {
                            stepSize: 1
                        }
                    }
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