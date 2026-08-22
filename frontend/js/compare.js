/**
 * Candidate Comparison JavaScript Logic
 */
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const screenings = await API.getScreenings();
        renderComparisonGrid(screenings.slice(0, 3));
    } catch (err) {
        console.error('Failed to load candidate comparison data:', err);
    }
});

function renderComparisonGrid(screenings) {
    const container = document.getElementById('comparison-grid');
    if (!container) return;

    if (!screenings || screenings.length === 0) {
        container.innerHTML = `<p style="color: #64748b;">No candidates available to compare.</p>`;
        return;
    }

    container.innerHTML = screenings.map(s => {
        const details = s.details || {};
        const matching = details.matching_skills || [];
        const missing = details.missing_skills || [];

        return `
            <div class="card" style="flex: 1; min-width: 280px;">
                <div style="border-bottom: 2px solid #e2e8f0; padding-bottom: 1rem; margin-bottom: 1rem;">
                    <h3 style="font-size: 1.2rem; color: #0f172a;">${escapeHtml(s.candidate_name)}</h3>
                    <div style="color: #64748b; font-size: 0.85rem;">${escapeHtml(s.job_title)}</div>
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1rem;">
                        <span class="score-badge ${s.match_score >= 7.0 ? 'score-high' : 'score-low'}">${s.match_score} / 10</span>
                        <span class="badge ${s.shortlist_status === 'Shortlisted' ? 'badge-success' : 'badge-danger'}">${s.shortlist_status}</span>
                    </div>
                </div>

                <div style="margin-bottom: 1rem;">
                    <strong style="font-size: 0.85rem; color: #64748b; text-transform: uppercase;">Matching Skills (${matching.length})</strong>
                    <div class="tag-cloud" style="margin-top: 0.4rem;">
                        ${matching.map(sk => `<span class="tag tag-match">${escapeHtml(sk)}</span>`).join(' ') || '<span style="color:#94a3b8; font-size:0.8rem;">None</span>'}
                    </div>
                </div>

                <div style="margin-bottom: 1rem;">
                    <strong style="font-size: 0.85rem; color: #64748b; text-transform: uppercase;">Missing Skills (${missing.length})</strong>
                    <div class="tag-cloud" style="margin-top: 0.4rem;">
                        ${missing.map(sk => `<span class="tag tag-missing">${escapeHtml(sk)}</span>`).join(' ') || '<span style="color:#94a3b8; font-size:0.8rem;">None</span>'}
                    </div>
                </div>

                <div style="margin-bottom: 1rem;">
                    <strong style="font-size: 0.85rem; color: #64748b; text-transform: uppercase;">Education Alignment</strong>
                    <p style="font-size: 0.85rem; color: #334155; margin-top: 0.3rem;">${escapeHtml(details.education_match || 'Reviewed')}</p>
                </div>

                <div style="margin-top: 1.5rem;">
                    <a href="candidate.html?id=${s.id}" class="btn btn-primary btn-sm" style="width: 100%;">Full Candidate Profile</a>
                </div>
            </div>
        `;
    }).join('');
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>"']/g, m => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
    }[m]));
}
