/**
 * Smart Resume Screener API Client
 */
const API_BASE = '/api';

async function apiRequest(endpoint, method = 'GET', body = null, isFormData = false) {
    const options = { method };
    
    if (body) {
        if (isFormData) {
            options.body = body;
        } else {
            options.headers = { 'Content-Type': 'application/json' };
            options.body = JSON.stringify(body);
        }
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        
        if (!response.ok) {
            let errorMsg = `Server error (${response.status})`;
            try {
                const errData = await response.json();
                errorMsg = errData.detail || errData.message || errorMsg;
            } catch (e) {}
            throw new Error(errorMsg);
        }

        // Handle CSV blob response
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('text/csv')) {
            return await response.blob();
        }

        return await response.json();
    } catch (err) {
        console.error(`API Error [${method} ${endpoint}]:`, err);
        throw err;
    }
}

const API = {
    getHealth: () => apiRequest('/health'),
    getDashboardStats: () => apiRequest('/dashboard'),
    
    // Jobs
    createJob: (jobData) => apiRequest('/jobs', 'POST', jobData),
    getJobs: () => apiRequest('/jobs'),
    getJob: (id) => apiRequest(`/jobs/${id}`),

    // Resumes
    uploadResumes: (formData) => apiRequest('/resumes/upload', 'POST', formData, true),
    getCandidates: () => apiRequest('/candidates'),
    getCandidate: (id) => apiRequest(`/candidates/${id}`),

    // Screenings
    screenCandidates: (data) => apiRequest('/screen', 'POST', data),
    getScreenings: (jobId = null, shortlistOnly = null) => {
        let query = [];
        if (jobId) query.push(`job_id=${jobId}`);
        if (shortlistOnly !== null) query.push(`shortlist_only=${shortlistOnly}`);
        const qStr = query.length ? `?${query.join('&')}` : '';
        return apiRequest(`/screenings${qStr}`);
    },
    getScreening: (id) => apiRequest(`/screenings/${id}`),
    exportCSV: (jobId = null) => apiRequest(`/screenings/export/csv${jobId ? `?job_id=${jobId}` : ''}`)
};
