// donations/static/donations/donations.js

document.addEventListener('DOMContentLoaded', () => {
    console.log("✅ Donations & Finances JS loaded.");

    // === Chart: Donations by Category ===
    const chartElement = document.getElementById('donationCategoryChart');
    if (chartElement) {
        const categoryLabels = JSON.parse(chartElement.dataset.labels || '[]');
        const categoryValues = JSON.parse(chartElement.dataset.values || '[]');

        const ctx = chartElement.getContext('2d');
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: categoryLabels,
                datasets: [{
                    label: 'Donations by Category',
                    data: categoryValues,
                    backgroundColor: [
                        '#4CAF50',
                        '#2196F3',
                        '#FFC107',
                        '#FF5722',
                        '#9C27B0',
                    ],
                    borderColor: '#fff',
                    borderWidth: 2,
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    title: {
                        display: true,
                        text: 'Donations Breakdown by Category'
                    }
                }
            }
        });
    }

    // === Filter Form Handling ===
    const filterForm = document.getElementById('filterForm');
    if (filterForm) {
        filterForm.addEventListener('submit', (e) => {
            e.preventDefault();

            const start = document.getElementById('start').value;
            const end = document.getElementById('end').value;
            const method = document.getElementById('method').value;
            const category = document.getElementById('category').value;

            const params = new URLSearchParams({
                ...(start && { start }),
                ...(end && { end }),
                ...(method && { method }),
                ...(category && { category }),
            });

            window.location.href = `${window.location.pathname}?${params.toString()}`;
        });
    }

    // === Smooth Card Animation on Page Load ===
    const summaryCards = document.querySelectorAll('.summary-card');
    summaryCards.forEach((card, i) => {
        setTimeout(() => {
            card.classList.add('visible');
        }, i * 150);
    });
});
