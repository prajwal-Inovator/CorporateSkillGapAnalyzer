// static/js/dashboard.js
document.addEventListener('DOMContentLoaded', function() {
    // ========================
    // DARK MODE TOGGLE
    // ========================
    // Create toggle button and add to navbar
    const darkModeToggle = document.createElement('button');
    darkModeToggle.innerHTML = '<i class="fas fa-moon"></i>';
    darkModeToggle.className = 'btn btn-sm btn-outline-light ms-3';
    darkModeToggle.setAttribute('aria-label', 'Toggle Dark Mode');
    darkModeToggle.title = 'Dark Mode';
    
    darkModeToggle.addEventListener('click', function() {
        document.body.classList.toggle('dark-mode');
        // Save preference to localStorage
        if (document.body.classList.contains('dark-mode')) {
            localStorage.setItem('darkMode', 'true');
            darkModeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        } else {
            localStorage.setItem('darkMode', 'false');
            darkModeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        }
    });
    
    // Find navbar collapse area and append button
    const navbarNav = document.querySelector('#navbarNav .ms-auto');
    if (navbarNav) {
        navbarNav.appendChild(darkModeToggle);
    }
    
    // Load saved dark mode preference
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-mode');
        darkModeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    }
    
    // ========================
    // CHART INITIALIZATION
    // ========================
    // Only run if we are on a page with chart canvases
    
    const chartErrorMessage = (container, message) => {
        const parent = container.parentElement;
        if (!parent) return;
        parent.innerHTML = `<div class="text-center text-muted p-4">${message}</div>`;
    };

    const validateChartData = (data, labelKey, valueKey) => {
        if (!data || !Array.isArray(data[labelKey]) || !Array.isArray(data[valueKey])) {
            return false;
        }
        return data[labelKey].length > 0 && data[valueKey].length > 0;
    };

    const renderDepartmentGapChart = (data) => {
        if (!validateChartData(data, 'labels', 'values')) {
            chartErrorMessage(deptGapCanvas, 'No department gap data available.');
            return;
        }
        new Chart(deptGapCanvas, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Average Gap Score',
                    data: data.values,
                    backgroundColor: '#0d6efd',
                    borderRadius: 6,
                    barPercentage: 0.7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { position: 'top' },
                    tooltip: { callbacks: { label: (ctx) => `Gap: ${parseFloat(ctx.raw).toFixed(1)}` } }
                },
                scales: {
                    y: { beginAtZero: true, title: { display: true, text: 'Gap Score' } },
                    x: { title: { display: true, text: 'Departments' } }
                }
            }
        });
    };

    const renderMissingSkillsChart = (data) => {
        if (!validateChartData(data, 'labels', 'counts')) {
            chartErrorMessage(missingSkillsCanvas, 'No missing skills data available.');
            return;
        }
        new Chart(missingSkillsCanvas, {
            type: 'pie',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.counts,
                    backgroundColor: ['#ff6384', '#36a2eb', '#ffce56', '#4bc0c0', '#9966ff'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'right' },
                    tooltip: { callbacks: { label: (ctx) => `${ctx.label}: ${ctx.raw} employees missing` } }
                }
            }
        });
    };

    const renderReadinessChart = (data) => {
        if (!validateChartData(data, 'labels', 'counts')) {
            chartErrorMessage(readinessCanvas, 'No readiness data available.');
            return;
        }
        new Chart(readinessCanvas, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.counts,
                    backgroundColor: ['#dc3545', '#ffc107', '#0d6efd', '#198754'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' },
                    tooltip: { callbacks: { label: (ctx) => `${ctx.label}: ${ctx.raw} employees` } }
                }
            }
        });
    };

    const deptGapCanvas = document.getElementById('deptGapChart');
    if (deptGapCanvas) {
        fetch('/analytics/data/department_gaps', { credentials: 'same-origin' })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    console.error('Department gaps error:', data.error);
                }
                renderDepartmentGapChart(data);
            })
            .catch(error => {
                console.error('Error loading department gaps:', error);
                chartErrorMessage(deptGapCanvas, 'Unable to load department gap data.');
            });
    }

    const missingSkillsCanvas = document.getElementById('missingSkillsChart');
    if (missingSkillsCanvas) {
        fetch('/analytics/data/top_missing_skills', { credentials: 'same-origin' })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    console.error('Missing skills error:', data.error);
                }
                renderMissingSkillsChart(data);
            })
            .catch(error => {
                console.error('Error loading missing skills:', error);
                chartErrorMessage(missingSkillsCanvas, 'Unable to load missing skills data.');
            });
    }

    const readinessCanvas = document.getElementById('readinessChart');
    if (readinessCanvas) {
        fetch('/analytics/data/readiness_distribution', { credentials: 'same-origin' })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    console.error('Readiness distribution error:', data.error);
                }
                renderReadinessChart(data);
            })
            .catch(error => {
                console.error('Error loading readiness distribution:', error);
                chartErrorMessage(readinessCanvas, 'Unable to load readiness distribution data.');
            });
    }
    
    // ========================
    // ADDITIONAL UI ENHANCEMENTS
    // ========================
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Add tooltips to any element with title attribute
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[title]'));
    tooltipTriggerList.map(el => new bootstrap.Tooltip(el));
    
    // Confirmation for delete buttons (already using onclick, but add as fallback)
    const deleteBtns = document.querySelectorAll('.btn-danger');
    deleteBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
});