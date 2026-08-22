/**
 * Candidate Deep-Dive Page JavaScript Logic
 */
document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const screeningId = urlParams.get('id');

    if (screeningId) {
        loadCandidateDetails(screeningId);
    } else {
        alert('No Candidate Screening ID provided.');
        window.location.href = 'index.html';
    }
});

async function loadCandidateDetails(screeningId) {
    try {
        const data = await API.getScreening(screeningId);
        renderCandidateProfile(data);
    } catch (err) {
        console.error('Failed to load candidate details:', err);
        alert('Failed to load candidate details: ' + err.message);
    }
}

function renderCandidateProfile(data) {
    // 1. Header Banner
    document.getElementById('cand-name').textContent = data.candidate_name || 'Candidate';
    document.getElementById('cand-email').textContent = data.candidate_email || 'Not provided';
    document.getElementById('cand-phone').textContent = data.candidate_phone || 'Not provided';
    document.getElementById('cand-location').textContent = data.candidate_location || 'Not provided';
    document.getElementById('job-title-label').textContent = data.job_title || 'Role';

    // Status Badge
    const badgeEl = document.getElementById('status-badge');
    if (badgeEl) {
        badgeEl.textContent = data.shortlist_status;
        badgeEl.className = `badge ${data.shortlist_status === 'Shortlisted' ? 'badge-success' : 'badge-danger'}`;
    }

    // Score Gauge
    document.getElementById('match-score-num').textContent = data.match_score;
    const fitLabel = data.match_score >= 8.0 ? 'Strong Fit' : (data.match_score >= 6.0 ? 'Moderate Fit' : 'Low Fit');
    document.getElementById('fit-level-label').textContent = fitLabel;

    // 2. "Why Shortlisted?" / Recommendation Highlight Card
    const whyCard = document.getElementById('why-shortlisted-box');
    if (whyCard) {
        const details = data.details || {};
        const matchingSkills = details.matching_skills || [];
        whyCard.innerHTML = `
            <h4><span style="font-size: 1.1rem;">💡</span> Shortlisting Justification & Key Evidence</h4>
            <p style="margin-bottom: 0.5rem; color: #1e293b;">${escapeHtml(data.justification)}</p>
            <ul style="padding-left: 1.25rem; font-size: 0.9rem; color: #334155;">
                ${matchingSkills.length ? `<li>Strong alignment with required skills: <strong>${matchingSkills.slice(0, 4).join(', ')}</strong></li>` : ''}
                ${details.education_match ? `<li>Education: ${escapeHtml(details.education_match)}</li>` : ''}
                <li>Match score (${data.match_score}/10) evaluated against threshold (${data.threshold_used}/10).</li>
            </ul>
        `;
    }

    // 3. Category Score Breakdown
    const details = data.details || {};
    if (details.skills_score) document.getElementById('skills-score-val').textContent = `${details.skills_score}%`;
    if (details.experience_score) document.getElementById('exp-score-val').textContent = `${details.experience_score}%`;
    if (details.education_score) document.getElementById('edu-score-val').textContent = `${details.education_score}%`;

    // 4. Matching & Missing Skills Tag Clouds
    const matchingContainer = document.getElementById('matching-skills-cloud');
    if (matchingContainer) {
        const matching = details.matching_skills || [];
        matchingContainer.innerHTML = matching.length ?
            matching.map(s => `<span class="tag tag-match">✓ ${escapeHtml(s)}</span>`).join(' ') :
            '<p style="color: #94a3b8; font-size: 0.85rem;">No matching skills detected.</p>';
    }

    const missingContainer = document.getElementById('missing-skills-cloud');
    if (missingContainer) {
        const missing = details.missing_skills || [];
        missingContainer.innerHTML = missing.length ?
            missing.map(s => `<span class="tag tag-missing">✗ ${escapeHtml(s)}</span>`).join(' ') :
            '<p style="color: #94a3b8; font-size: 0.85rem;">No critical skill gaps identified.</p>';
    }

    // 5. Strengths & Gaps
    const strengthsUl = document.getElementById('strengths-list');
    if (strengthsUl) {
        const strengths = details.strengths || [];
        strengthsUl.innerHTML = strengths.length ?
            strengths.map(st => `<li>${escapeHtml(st)}</li>`).join('') :
            '<li>General qualification alignment evaluated.</li>';
    }

    const gapsUl = document.getElementById('gaps-list');
    if (gapsUl) {
        const gaps = details.gaps || [];
        gapsUl.innerHTML = gaps.length ?
            gaps.map(g => `<li>${escapeHtml(g)}</li>`).join('') :
            '<li>No significant candidate gaps recorded.</li>';
    }

    // 6. Experience & Education History
    const expContainer = document.getElementById('experience-history-list');
    if (expContainer) {
        const expList = data.experience || [];
        expContainer.innerHTML = expList.length ?
            expList.map(exp => `
                <div style="margin-bottom: 1rem; padding-bottom: 0.75rem; border-bottom: 1px solid #e2e8f0;">
                    <div style="font-weight: 700; color: #0f172a;">${escapeHtml(exp.job_title || 'Position')}</div>
                    <div style="font-size: 0.85rem; color: #64748b;">${escapeHtml(exp.company || 'Company')} | ${escapeHtml(exp.duration || 'Dates')}</div>
                    <p style="font-size: 0.85rem; color: #334155; margin-top: 0.3rem;">${escapeHtml(exp.responsibilities || '')}</p>
                </div>
            `).join('') : '<p style="color: #94a3b8;">No detailed experience entries parsed.</p>';
    }

    const eduContainer = document.getElementById('education-history-list');
    if (eduContainer) {
        const eduList = data.education || [];
        eduContainer.innerHTML = eduList.length ?
            eduList.map(edu => `
                <div style="margin-bottom: 0.75rem;">
                    <div style="font-weight: 700; color: #0f172a;">${escapeHtml(edu.degree || 'Degree')}</div>
                    <div style="font-size: 0.85rem; color: #64748b;">${escapeHtml(edu.institution || 'University')} ${edu.graduation_year ? `(${escapeHtml(edu.graduation_year)})` : ''}</div>
                </div>
            `).join('') : '<p style="color: #94a3b8;">No education entries parsed.</p>';
    }

    // Toggle Raw Resume Text Modal
    const rawBtn = document.getElementById('view-raw-resume-btn');
    if (rawBtn) {
        rawBtn.addEventListener('click', async () => {
            const cand = await API.getCandidate(data.candidate_id);
            alert(`--- RAW RESUME TEXT FOR ${cand.name} ---\n\n` + cand.raw_text);
        });
    }
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>"']/g, m => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
    }[m]));
}
