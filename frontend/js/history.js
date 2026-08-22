/**
 * Screening Audit History JavaScript Logic
 */
document.addEventListener('DOMContentLoaded', () => {
    loadScreeningHistory();
});

async function loadScreeningHistory() {
    try {
        const screenings = await API.getScreenings();
        renderHistoryTable(screenings);
    } catch (err) {
        console.error('Failed to load screening history:', err);
    }
}

function renderHistoryTable(screenings) {
    const tbody = document.getElementById('history-tbody');
    if (!tbody) return;

    if (!screenings || screenings.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; padding: 2rem; color: #64748b;">
                    No screening audit history found.
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = screenings.map(s => `
        <tr>
            <td>#${s.id}</td>
            <td><strong>${escapeHtml(s.candidate_name)}</strong></td>
            <td>${escapeHtml(s.job_title)}</td>
            <td>
                <span class="score-badge ${s.match_score >= 7.0 ? 'score-high' : 'score-low'}">${s.match_score}</span>
            </td>
            <td>
                <span class="badge ${s.shortlist_status === 'Shortlisted' ? 'badge-success' : 'badge-danger'}">${escapeHtml(s.shortlist_status)}</span>
            </td>
            <td>${new Date(s.created_at).toLocaleString()}</td>
            <td>
                <a href="candidate.html?id=${s.id}" class="btn btn-sm btn-primary">Details</a>
            </td>
        </tr>
    `).join('');
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>"']/g, m => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
    }[m]));
}
