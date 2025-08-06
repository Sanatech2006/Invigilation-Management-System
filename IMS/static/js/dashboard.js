document.addEventListener('DOMContentLoaded', function () {
    console.log('Dashboard loaded');
    
    const canvas = document.getElementById('staffChart');
    if (!canvas) return;

    const categories = JSON.parse(canvas.dataset.categories);
    const counts = JSON.parse(canvas.dataset.counts);

    // Define distinct colors for each category
    const backgroundColors = [
    'rgba(255, 99, 132, 0.8)',    // Bright Red
    'rgba(54, 162, 235, 0.8)',    // Bright Blue
    'rgba(34, 197, 94, 0.7)'     // Bright Yellow
];
const borderColors = [
    'rgba(255, 99, 132, 1)',
    'rgba(54, 162, 235, 1)',
    'rgba(34, 197, 94, 1)'
];
    
    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: categories,
            datasets: [{
                label: 'Staff Count',
                data: counts,
                backgroundColor: backgroundColors,
                borderColor: borderColors,
                borderWidth: 1,
                barThickness: 30,
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false, // Allows custom sizing
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    // text: 'Staff Count by Department',
                    font: {
                        size: 14
                    },
                    padding: {
                        bottom: 10
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    },
                    grid: {
                        display: false
                    }
                },
                y: {
                    grid: {
                        display: false
                    }
                }
            },
            // Reduce overall chart padding
            layout: {
                padding: {
                    left: 10,
                    right: 10,
                    top: 10,
                    bottom: 10
                }
            }
        }
    });

    // Set a smaller size for the canvas container
   const container = canvas.parentElement;
    if (container) {
        container.style.maxWidth = '600px';  // About half of typical screen width
        container.style.margin = '0 auto';  // Center the chart
        container.style.height = '300px';   // Reasonable height
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const sessionCanvas = document.getElementById('sessionChart');
    if (!sessionCanvas) return;

    const sessionCategories = JSON.parse(sessionCanvas.dataset.categories);
    const sessionValues = JSON.parse(sessionCanvas.dataset.values);

    const ctx2 = sessionCanvas.getContext('2d');
    new Chart(ctx2, {
        type: 'bar',
        data: {
    labels: sessionCategories,
    datasets: [{
        label: 'Total Required Sessions',
        data: sessionValues,
        backgroundColor: [
            'rgba(255, 99, 132, 0.7)',   // Rose Pink
            'rgba(75, 192, 192, 0.7)',   // Teal
            'rgba(34, 197, 94, 0.7)'    // Mustard Yellow
        ],
        borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(75, 192, 192, 1)',
           'rgba(34, 197, 94, 1)'
        ],
        borderWidth: 1,
        barThickness: 30,
    }]
},

        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    // text: 'Required Sessions by Department',
                    font: {
                        size: 14
                    },
                    padding: {
                        bottom: 10
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    },
                    grid: {
                        display: false
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
});
