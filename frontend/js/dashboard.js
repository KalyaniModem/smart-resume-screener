/**
 * Recruiter Dashboard JavaScript Logic
 */
let allScreenings = [];

document.addEventListener('DOMContentLoaded', () => {
    loadDashboardData();
    setupEventListeners();
});

async function loadDashboardData() {
    try {
        // Fetch dashboard stats
        const stats = await API.getDashboardStats();
        updateStatCards(stats);

        // Fetch screenings list
        allScreenings = await API.getScreenings();
        renderScreeningsTable(allScreenings);
    } catch (err) {
        console.error('Failed to load dashboard data:', err);
        showErrorToast('Failed to load dashboard data. Please check backend server status.');
    }
}

function updateStatCards(stats) {
    document.getElementById('stat-total-candidates').textContent = stats.total_candidates || 0;
    document.getElementById('stat-screened').textContent = stats.total_screenings || 0;
    document.getElementById('stat-shortlisted').textContent = stats.shortlisted || 0;
    document.getElementById('stat-not-shortlisted').textContent = stats.not_shortlisted || 0;
    document.getElementById('stat-avg-score').textContent = stats.average_match_score ? `${stats.average_match_score} / 10` : '0 / 10';
}

function renderScreeningsTable(screenings) {
    const tbody = document.getElementById('candidates-tbody');
    if (!tbody) return;

    if (!screenings || screenings.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; padding: 2rem; color: #64748b;">
                    No candidate screenings found. <a href="screen.html">Upload resumes</a> to begin screening.
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = screenings.map(item => {
        const scoreClass = item.match_score >= 8.0 ? 'score-high' : (item.match_score >= 6.0 ? 'score-med' : 'score-low');
        const badgeClass = item.shortlist_status === 'Shortlisted' ? 'badge-success' : 'badge-danger';
        
        const matchingSkills = item.details?.matching_skills || [];
        const skillsTags = matchingSkills.slice(0, 4).map(s => `<span class="tag tag-match">${escapeHtml(s)}</span>`).join(' ');

        return `
            <tr>
                <td>
                    <div style="font-weight: 600;">${escapeHtml(item.candidate_name)}</div>
                    <div style="font-size: 0.8rem; color: #64748b;">${escapeHtml(item.candidate_email || 'No email')}</div>
                </td>
                <td>
                    <div style="font-size: 0.85rem; font-weight: 500;">${escapeHtml(item.job_title)}</div>
                </td>
                <td>${skillsTags || '<span style="color:#94a3b8; font-size:0.8rem;">None detected</span>'}</td>
                <td>
                    <span class="score-badge ${scoreClass}">${item.match_score}</span>
                </td>
                <td>
                    <span class="badge ${badgeClass}">${escapeHtml(item.shortlist_status)}</span>
                </td>
                <td style="font-size: 0.8rem; color: #64748b;">
                    ${new Date(item.created_at).toLocaleDateString()}
                </td>
                <td>
                    <div style="display: flex; gap: 0.4rem;">
                        <a href="candidate.html?id=${item.id}" class="btn btn-sm btn-primary">View</a>
                        <a href="compare.html?ids=${item.candidate_id}" class="btn btn-sm btn-secondary">Compare</a>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

function setupEventListeners() {
    const searchInput = document.getElementById('search-input');
    const filterSelect = document.getElementById('filter-status');
    const sortSelect = document.getElementById('sort-by');
    const exportBtn = document.getElementById('export-csv-btn');

    if (searchInput) searchInput.addEventListener('input', applyFiltersAndSort);
    if (filterSelect) filterSelect.addEventListener('change', applyFiltersAndSort);
    if (sortSelect) sortSelect.addEventListener('change', applyFiltersAndSort);

    if (exportBtn) {
        exportBtn.addEventListener('click', async () => {
            try {
                const blob = await API.exportCSV();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'screening_results.csv';
                document.body.appendChild(a);
                a.click();
                a.remove();
            } catch (err) {
                alert('Export failed: ' + err.message);
            }
        });
    }
}

function applyFiltersAndSort() {
    const searchTerm = (document.getElementById('search-input')?.value || '').toLowerCase();
    const statusFilter = document.getElementById('filter-status')?.value || 'all';
    const sortBy = document.getElementById('sort-by')?.value || 'score_desc';

    let filtered = allScreenings.filter(item => {
        const matchesSearch = item.candidate_name.toLowerCase().includes(searchTerm) ||
                              item.job_title.toLowerCase().includes(searchTerm) ||
                              (item.candidate_email && item.candidate_email.toLowerCase().includes(searchTerm));

        let matchesStatus = true;
        if (statusFilter === 'shortlisted') matchesStatus = item.shortlist_status === 'Shortlisted';
        if (statusFilter === 'not_shortlisted') matchesStatus = item.shortlist_status !== 'Shortlisted';

        return matchesSearch && matchesStatus;
    });

    // Sorting
    filtered.sort((a, b) => {
        if (sortBy === 'score_desc') return b.match_score - a.match_score;
        if (sortBy === 'score_asc') return a.match_score - b.match_score;
        if (sortBy === 'name') return a.candidate_name.localeCompare(b.candidate_name);
        return new Date(b.created_at) - new Date(a.created_at);
    });

    renderScreeningsTable(filtered);
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>"']/g, m => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
    }[m]));
}

function showErrorToast(msg) {
    alert(msg);
}
