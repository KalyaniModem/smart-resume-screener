/**
 * Screen Candidates Page JavaScript Logic
 */
let selectedFiles = [];

document.addEventListener('DOMContentLoaded', () => {
    setupDropzone();
    setupFormListeners();
});

function setupDropzone() {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('resume-file-input');

    if (!dropzone || !fileInput) return;

    dropzone.addEventListener('click', () => fileInput.click());

    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFiles(e.dataTransfer.files);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFiles(e.target.files);
        }
    });
}

function handleFiles(files) {
    const allowed = ['.pdf', '.txt'];
    for (let file of files) {
        const parts = file.name.split('.');
        const ext = parts.length > 1 ? '.' + parts.pop().toLowerCase() : '';
        if (!allowed.includes(ext)) {
            alert(`Unsupported file type: ${file.name}. Please upload PDF (.pdf) or Text (.txt) files.`);
            continue;
        }
        if (file.size === 0) {
            alert(`File ${file.name} is empty (0 bytes).`);
            continue;
        }
        // Avoid duplicate files
        if (!selectedFiles.some(f => f.name === file.name && f.size === file.size)) {
            selectedFiles.push(file);
        }
    }
    renderFileList();
    
    // Reset file input value so re-selecting the same file triggers change event
    const fileInput = document.getElementById('resume-file-input');
    if (fileInput) fileInput.value = '';
}

function renderFileList() {
    const container = document.getElementById('selected-files-list');
    if (!container) return;

    if (selectedFiles.length === 0) {
        container.innerHTML = `<p style="color: #64748b; font-size: 0.85rem;">No files selected yet.</p>`;
        return;
    }

    container.innerHTML = selectedFiles.map((file, idx) => `
        <div class="file-item">
            <div>
                <strong>${escapeHtml(file.name)}</strong>
                <span style="color: #64748b; margin-left: 0.5rem;">(${(file.size / 1024).toFixed(1)} KB)</span>
            </div>
            <button type="button" class="btn btn-sm btn-danger" onclick="removeFile(${idx})">Remove</button>
        </div>
    `).join('');
}

function removeFile(index) {
    selectedFiles.splice(index, 1);
    renderFileList();
}

function setupFormListeners() {
    const screenBtn = document.getElementById('run-screen-btn');
    const jobFileInput = document.getElementById('job-file-input');
    const loadSampleBtn = document.getElementById('load-sample-btn');

    if (jobFileInput) {
        jobFileInput.addEventListener('change', async (e) => {
            if (e.target.files.length) {
                const file = e.target.files[0];
                const ext = '.' + file.name.split('.').pop().toLowerCase();
                if (ext !== '.txt') {
                    alert(`Job file must be a .txt file. Please paste your job description text into the Job Description box directly, or upload a .txt file.`);
                    jobFileInput.value = '';
                    return;
                }
                const text = await file.text();
                document.getElementById('job-description').value = text;
                if (!document.getElementById('job-title').value) {
                    document.getElementById('job-title').value = file.name.replace(/\.[^/.]+$/, "").replace(/_/g, " ");
                }
            }
        });
    }

    if (loadSampleBtn) {
        loadSampleBtn.addEventListener('click', async () => {
            try {
                // Fetch sample job description
                const resp = await fetch('/sample_data/job_description.txt');
                if (resp.ok) {
                    const text = await resp.text();
                    document.getElementById('job-title').value = 'Senior Full-Stack Python Engineer';
                    document.getElementById('job-description').value = text;
                }

                // Fetch sample files and attach
                const filesToLoad = [
                    { name: 'candidate_1_alex_chen.txt', path: '/sample_data/candidate_1_alex_chen.txt' },
                    { name: 'candidate_2_sarah_jenkins.txt', path: '/sample_data/candidate_2_sarah_jenkins.txt' },
                    { name: 'candidate_3_michael_brown.txt', path: '/sample_data/candidate_3_michael_brown.txt' }
                ];

                selectedFiles = [];
                for (let item of filesToLoad) {
                    const fResp = await fetch(item.path);
                    if (fResp.ok) {
                        const blob = await fResp.blob();
                        const file = new File([blob], item.name, { type: 'text/plain' });
                        selectedFiles.push(file);
                    }
                }
                renderFileList();
                alert('Loaded sample job description and 3 sample resumes! Click "Screen Candidates" to execute demo.');
            } catch (err) {
                alert('Error loading sample data: ' + err.message);
            }
        });
    }

    if (screenBtn) {
        screenBtn.addEventListener('click', startBatchScreening);
    }
}

async function startBatchScreening() {
    const jobTitle = document.getElementById('job-title')?.value.trim();
    const jobDescription = document.getElementById('job-description')?.value.trim();
    const threshold = parseFloat(document.getElementById('shortlist-threshold')?.value || 7.0);

    if (!jobTitle) {
        alert('Please enter a Job Title.');
        return;
    }
    if (!jobDescription || jobDescription.length < 10) {
        alert('Please enter a valid Job Description (at least 10 characters).');
        return;
    }
    if (selectedFiles.length === 0) {
        alert('Please upload or select at least one resume file to screen.');
        return;
    }

    // UI state loading
    const progressCard = document.getElementById('progress-card');
    const progressBar = document.getElementById('progress-bar-fill');
    const statusText = document.getElementById('progress-status-text');
    const percentText = document.getElementById('progress-percent');
    const screenBtn = document.getElementById('run-screen-btn');

    if (progressCard) progressCard.style.display = 'block';
    if (screenBtn) screenBtn.disabled = true;

    try {
        // Step 1: Create Job
        updateProgress(10, 'Creating Job Description in Database...', progressBar, statusText, percentText);
        const job = await API.createJob({ title: jobTitle, description: jobDescription });

        // Step 2: Upload Resumes
        updateProgress(30, `Uploading and extracting text from ${selectedFiles.length} resumes...`, progressBar, statusText, percentText);
        const formData = new FormData();
        selectedFiles.forEach(file => formData.append('files', file));
        
        const uploadResult = await API.uploadResumes(formData);
        const candidates = uploadResult.candidates || [];

        if (candidates.length === 0) {
            throw new Error('No candidate files could be processed successfully.');
        }

        // Step 3: Run LLM Semantic Screening
        updateProgress(60, `Performing AI semantic matching against Job Description (Threshold: ${threshold})...`, progressBar, statusText, percentText);
        const candidateIds = candidates.map(c => c.candidate_id);
        
        const screeningResult = await API.screenCandidates({
            job_id: job.id,
            candidate_ids: candidateIds,
            threshold: threshold
        });

        // Step 4: Complete
        updateProgress(100, 'Screening completed successfully! Redirecting to Recruiter Dashboard...', progressBar, statusText, percentText);

        setTimeout(() => {
            window.location.href = 'index.html';
        }, 1200);

    } catch (err) {
        console.error('Screening execution error:', err);
        alert('Screening execution failed: ' + err.message);
        if (screenBtn) screenBtn.disabled = false;
        if (progressCard) progressCard.style.display = 'none';
    }
}

function updateProgress(percent, message, barEl, msgEl, percentEl) {
    if (barEl) barEl.style.width = `${percent}%`;
    if (msgEl) msgEl.textContent = message;
    if (percentEl) percentEl.textContent = `${percent}%`;
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>"']/g, m => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
    }[m]));
}
