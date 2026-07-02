/* =====================================================================
   PlaceMux AI — App Logic
   face-api.js for real face detection + adaptive CAT flow
   ===================================================================== */

// ── State ─────────────────────────────────────────────────────────────
const state = {
    candidateId: null,
    name: '', email: '',
    currentQuestion: null,
    selectedOption: null,
    questionNum: 1,
    difficulty: 'Easy',
    lastCorrect: null,
    history: [],
    isRunning: false,
    webcamStream: null,
    faceDetectionLoop: null,
    faceApiLoaded: false,
    noFaceFrames: 0,
    multiFaceFrames: 0,
    violationCount: 0,
    attentionScore: 100,
    tabSwitchesCount: 0,
    fullscreenExits: 0,
    audioContext: null,
    audioStream: null,
    audioLoop: null,
};

// ── DOM refs ──────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);

const views = {
    welcome:   $('view-welcome'),
    test:      $('view-test'),
    dashboard: $('view-dashboard'),
};

// ── Utility: show view ────────────────────────────────────────────────
function showView(name) {
    Object.entries(views).forEach(([k, el]) => {
        if (k === name) { el.classList.add('active'); }
        else { el.classList.remove('active'); }
    });
}

// ── Registration ──────────────────────────────────────────────────────
$('reg-form').addEventListener('submit', async e => {
    e.preventDefault();
    const name         = $('reg-name').value.trim();
    const email        = $('reg-email').value.trim();
    const branch       = $('reg-branch')?.value || '';
    const college      = $('reg-college')?.value.trim() || '';
    const year         = $('reg-year')?.value || '';
    const btn          = $('btn-start');

    btn.innerHTML = '<div class="spinner"></div><span>Registering…</span>';
    btn.disabled = true;

    try {
        const params = new URLSearchParams({ name, email });
        if (branch)  params.append('branch',        branch);
        if (college) params.append('college',       college);
        if (year)    params.append('year_of_study', year);

        const res  = await fetch(`/candidate?${params.toString()}`, { method: 'POST' });
        if (!res.ok) throw new Error('Registration failed');
        const data = await res.json();

        state.candidateId = data.id;
        state.name  = data.name;
        state.email = data.email;

        // Update topbar
        $('topbar-uname').textContent = state.name;
        $('s-name').textContent = state.name;
        $('topbar-status').classList.remove('hidden');

        await startAssessment();
    } catch (err) {
        alert('Error: ' + err.message);
    } finally {
        btn.innerHTML = '<span>Begin Assessment</span><i class="fa-solid fa-arrow-right"></i>';
        btn.disabled = false;
    }
});

// ── Start Assessment ─────────────────────────────────────────────────
async function startAssessment() {
    state.questionNum = 1;
    state.difficulty  = 'Easy';
    state.lastCorrect = null;
    state.history     = [];
    state.isRunning   = true;
    state.violationCount = 0;
    state.attentionScore = 100;
    state.noFaceFrames    = 0;
    state.multiFaceFrames = 0;
    state.fullscreenExits = 0;

    showView('test');

    // Request fullscreen mode — exam must run in full tab
    await enterFullscreen();

    await initProctoring();
    await fetchNextQuestion();
}

// ── Fetch Next Question ───────────────────────────────────────────────
async function fetchNextQuestion() {
    $('btn-submit').disabled = true;

    try {
        const res = await fetch('/api/next-question', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                candidate_id: state.candidateId,
                current_difficulty: state.difficulty,
                last_response_correct: state.lastCorrect,
            })
        });
        if (!res.ok) throw new Error('Failed to load question');
        const data = await res.json();

        // Update live theta/SEM in topbar & sidebar
        if (data.current_theta != null) {
            const t = data.current_theta.toFixed(2);
            $('ability-live').textContent = `θ = ${t}`;
            $('theta-live').textContent   = t;
            $('s-theta').textContent      = `θ = ${t} (SEM ±${(data.current_sem ?? 1).toFixed(2)})`;
        }
        if (data.current_sem != null) {
            $('sem-live').textContent = data.current_sem.toFixed(2);
        }

        if (data.finished) {
            await finishAssessment();
            return;
        }

        state.currentQuestion = data;
        state.difficulty      = data.difficulty;
        state.selectedOption  = null;

        // Progress
        const pct = Math.min(((state.questionNum - 1) / 10) * 100, 95);
        $('q-progress-bar').style.width = `${pct}%`;
        $('q-num').textContent = state.questionNum;

        // Difficulty pill
        const pill = $('diff-pill');
        pill.className = `diff-pill ${data.difficulty.toLowerCase()}`;
        pill.textContent = data.difficulty;

        // Question text
        $('q-text').textContent = data.question_text;

        // Render options
        const grid = $('opts-grid');
        grid.innerHTML = '';
        const labels = ['A','B','C','D'];

        data.options.forEach((txt, i) => {
            const card = document.createElement('div');
            card.className = 'opt-card';
            card.dataset.opt = labels[i];
            card.innerHTML = `
                <div class="opt-marker">${labels[i]}</div>
                <div class="opt-text">${txt}</div>
            `;
            card.addEventListener('click', () => {
                document.querySelectorAll('.opt-card').forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
                state.selectedOption = labels[i];
                $('btn-submit').disabled = false;
            });
            grid.appendChild(card);
        });

    } catch (err) {
        alert('Question error: ' + err.message);
    }
}

// ── Submit Answer ─────────────────────────────────────────────────────
$('btn-submit').addEventListener('click', async () => {
    if (!state.selectedOption) return;
    $('btn-submit').disabled = true;

    try {
        const res = await fetch('/api/submit-answer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                candidate_id: state.candidateId,
                question_id:  state.currentQuestion.next_question_id,
                selected_option: state.selectedOption,
            })
        });
        if (!res.ok) throw new Error('Submit failed');
        const data = await res.json();

        state.history.push({
            question_text:   state.currentQuestion.question_text,
            difficulty:      state.difficulty,
            selected_option: state.selectedOption,
            is_correct:      data.is_correct,
        });

        state.lastCorrect = data.is_correct;
        state.questionNum++;
        await fetchNextQuestion();
    } catch (err) {
        alert('Submission error: ' + err.message);
        $('btn-submit').disabled = false;
    }
});

// ── Finish Assessment ─────────────────────────────────────────────────
async function finishAssessment() {
    state.isRunning = false;
    stopProctoring();
    showView('dashboard');
    await renderDashboard();
}

// ── Dashboard ─────────────────────────────────────────────────────────
async function renderDashboard() {
    $('dash-name').textContent = state.name;
    $('dash-sub').querySelector('strong').textContent = state.name;

    try {
        // 1. Final score
        const scoreRes  = await fetch('/api/final-score', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ candidate_id: state.candidateId })
        });
        const score = await scoreRes.json();

        drawGauge(score.scaled_score ?? 0);
        $('dash-theta').textContent       = score.ability_estimate?.toFixed(2) ?? '—';
        $('dash-confidence').textContent  = `${Math.round((1 - (score.sem ?? 1)) * 100)}%`;
        $('dash-percentile').textContent  = score.percentile ? `${score.percentile}th` : '—';

        // 2. Competencies
        const compRes  = await fetch(`/api/competency-analysis/${state.candidateId}`);
        const compData = await compRes.json();
        const compList = $('comp-list');
        compList.innerHTML = '';

        if (Object.keys(compData).length === 0) {
            compList.innerHTML = '<div class="empty-msg">No competencies evaluated.</div>';
        } else {
            Object.entries(compData).forEach(([compId, d]) => {
                const displayName = d.skill || compId;  // skill name from ontology, fallback to ID
                const el = document.createElement('div');
                el.className = 'comp-item';
                el.innerHTML = `
                    <div class="comp-header">
                        <span class="comp-name">${displayName}</span>
                        <span class="comp-pct">${d.score?.toFixed(0) ?? 0}%</span>
                    </div>
                    <div class="comp-track"><div class="comp-fill" style="width:0%"></div></div>
                    <div class="comp-detail">${d.correct_answers} / ${d.total_questions} correct</div>
                `;
                compList.appendChild(el);
                setTimeout(() => {
                    el.querySelector('.comp-fill').style.width = `${d.score ?? 0}%`;
                }, 100);
            });
        }

        // 3. Recommendations
        const recRes  = await fetch(`/api/recommendations/${state.candidateId}`);
        const recData = await recRes.json();
        const recList = $('rec-list');
        recList.innerHTML = '';

        (recData ?? []).forEach(m => {
            const el = document.createElement('div');
            el.className = 'rec-item';
            const tags = (m.required_skills ?? []).map(s =>
                `<span class="skill-tag">${s}</span>`).join('');
            el.innerHTML = `
                <div class="rec-top">
                    <div class="rec-role"><i class="${m.icon ?? 'fa-solid fa-briefcase'}"></i>${m.role}</div>
                    <div class="rec-match">${m.match_percentage}% Fit</div>
                </div>
                <div class="rec-why">${m.explainer}</div>
                <div class="rec-skills">${tags}</div>
            `;
            recList.appendChild(el);
        });

        // 4. Proctoring report
        const reportRes  = await fetch(`/api/proctoring-report/${state.candidateId}`);
        const report     = await reportRes.json();

        const riskScore = report.risk_score ?? 0;
        $('int-violations').textContent = report.violations_count ?? 0;
        $('int-high').textContent = report.severity_breakdown?.HIGH ?? 0;
        $('int-med').textContent  = report.severity_breakdown?.MEDIUM ?? 0;
        $('risk-fill').style.width = `${riskScore}%`;
        $('risk-pct').textContent  = `${riskScore}%`;

        const banner = $('verdict-banner');
        if (report.is_disqualified) {
            banner.textContent = 'DISQUALIFIED';
            banner.className = 'verdict-banner danger';
        } else {
            banner.textContent = report.verdict?.replace('_', ' ') ?? 'LOW RISK';
            banner.className   = 'verdict-banner';
            if (riskScore >= 60) banner.classList.add('danger');
            else if (riskScore >= 30) banner.classList.add('warning');
            else banner.classList.add('safe');
        }

        const flagList = $('flag-list');
        flagList.innerHTML = '';
        if ((report.flag_report ?? []).length === 0) {
            flagList.innerHTML = '<div class="empty-msg">No integrity violations recorded.</div>';
        } else {
            report.flag_report.forEach(f => {
                const item = document.createElement('div');
                item.className = 'flag-item';
                item.innerHTML = `
                    <span class="event-type">${f.event_type.replace('_', ' ')}</span>
                    <span class="sev-badge ${f.severity}">${f.severity}</span>
                    <span class="flag-time">${f.timestamp ? new Date(f.timestamp).toLocaleTimeString() : ''}</span>
                `;
                flagList.appendChild(item);
            });
        }

        // 5. Question review
        const reviewList = $('review-list');
        reviewList.innerHTML = '';
        state.history.forEach((ans, i) => {
            const el = document.createElement('div');
            el.className = 'review-item';
            el.innerHTML = `
                <div class="review-header">
                    <div class="review-q">Q${i + 1}. ${ans.question_text}</div>
                    <div class="review-badges">
                        <span class="ans-badge ${ans.is_correct ? 'correct' : 'incorrect'}">
                            ${ans.is_correct ? 'Correct' : 'Incorrect'}
                        </span>
                        <div class="diff-pill ${ans.difficulty.toLowerCase()}">${ans.difficulty}</div>
                    </div>
                </div>
                <div class="review-ans">
                    Your answer: <strong class="${ans.is_correct ? 'correct' : 'incorrect'}">${ans.selected_option}</strong>
                </div>
            `;
            reviewList.appendChild(el);
        });

    } catch (err) {
        console.error('Dashboard error:', err);
    }
}

// ── Gauge Canvas ──────────────────────────────────────────────────────
function drawGauge(score) {
    const canvas = $('gauge-canvas');
    const ctx    = canvas.getContext('2d');
    const cx = canvas.width / 2, cy = canvas.height / 2, r = 90;
    let cur = 0;

    function frame() {
        if (cur < score) { cur = Math.min(cur + 2, score); }
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Track
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, 2 * Math.PI);
        ctx.strokeStyle = 'rgba(255,255,255,0.05)';
        ctx.lineWidth = 14; ctx.stroke();

        // Fill
        const start = -Math.PI / 2;
        const end   = start + (2 * Math.PI * cur / 100);
        ctx.beginPath(); ctx.arc(cx, cy, r, start, end);
        const g = ctx.createLinearGradient(0, 0, canvas.width, 0);
        g.addColorStop(0, '#F43F5E');
        g.addColorStop(1, '#D946EF');
        ctx.strokeStyle = g; ctx.lineWidth = 14; ctx.lineCap = 'round';
        ctx.shadowColor = 'rgba(244,63,94,0.5)'; ctx.shadowBlur = 20;
        ctx.stroke(); ctx.shadowBlur = 0;

        $('dash-score').textContent = Math.round(cur);
        if (cur < score) requestAnimationFrame(frame);
    }
    frame();
}

// ═════════════════════════════════════════════════════════════════════
//   FULLSCREEN ENFORCEMENT
// ═════════════════════════════════════════════════════════════════════

async function enterFullscreen() {
    const el = document.documentElement;
    try {
        if (el.requestFullscreen) await el.requestFullscreen();
        else if (el.webkitRequestFullscreen) await el.webkitRequestFullscreen();
        else if (el.mozRequestFullScreen) await el.mozRequestFullScreen();
        else if (el.msRequestFullscreen) await el.msRequestFullscreen();
    } catch (e) {
        console.warn('Fullscreen request failed:', e);
    }
}

function isFullscreen() {
    return !!(document.fullscreenElement ||
        document.webkitFullscreenElement ||
        document.mozFullScreenElement ||
        document.msFullscreenElement);
}

function onFullscreenChange() {
    if (!state.isRunning) return;

    const fsStatus = $('fullscreen-status');
    if (!isFullscreen()) {
        // Update sidebar metric
        if (fsStatus) { fsStatus.textContent = 'EXITED'; fsStatus.className = 'metric-val danger'; }

        state.fullscreenExits++;
        const remaining = 3 - state.fullscreenExits;

        if (state.fullscreenExits >= 3) {
            // Show final termination overlay then disqualify
            const overlay = $('fullscreen-exit-overlay');
            if (overlay) {
                const msg = $('fs-warning-count');
                if (msg) msg.textContent = 'You have been disqualified. Assessment terminated.';
                overlay.style.display = 'flex';
            }
            showWarnToast('Exam Terminated', 'You exited fullscreen 3 times. Assessment auto-terminated.');
            logViolation('FULLSCREEN_EXIT').then(() => triggerDisqualification());
        } else {
            // Show blocking overlay with warning count
            const overlay = $('fullscreen-exit-overlay');
            if (overlay) {
                const msg = $('fs-warning-count');
                if (msg) msg.textContent = `Warning ${state.fullscreenExits}/3 — Returning to fullscreen automatically…`;
                overlay.style.display = 'flex';
            }
            showWarnToast(
                `⛶ Fullscreen Exited — Warning ${state.fullscreenExits}/3`,
                `The exam must remain in fullscreen. ${remaining} warning(s) left before termination.`
            );
            logViolation('FULLSCREEN_EXIT');
            // Auto re-enter fullscreen after short delay
            setTimeout(() => {
                if (state.isRunning) {
                    enterFullscreen();
                    // Hide overlay after re-entering
                    setTimeout(() => {
                        const ov = $('fullscreen-exit-overlay');
                        if (ov) ov.style.display = 'none';
                    }, 400);
                }
            }, 1500);
        }
    } else {
        // Back in fullscreen — update sidebar metric to safe
        if (fsStatus) { fsStatus.textContent = 'ACTIVE'; fsStatus.className = 'metric-val safe'; }
    }
}

// ═════════════════════════════════════════════════════════════════════
//   PROCTORING — face-api.js real face detection
// ═════════════════════════════════════════════════════════════════════

async function initProctoring() {
    state.tabSwitchesCount = 0;

    // Tab / window blur events
    document.addEventListener('visibilitychange', onVisibilityChange);
    window.addEventListener('blur', onWindowBlur);

    // Fullscreen change detection (minimize / exit fullscreen)
    document.addEventListener('fullscreenchange', onFullscreenChange);
    document.addEventListener('webkitfullscreenchange', onFullscreenChange);
    document.addEventListener('mozfullscreenchange', onFullscreenChange);
    document.addEventListener('MSFullscreenChange', onFullscreenChange);

    // Reset counters UI
    $('violation-count').textContent = '0';
    $('integrity-status').textContent = 'SECURE';
    $('integrity-status').className = 'metric-val safe';
    if ($('audio-status')) {
        $('audio-status').textContent = 'Waiting…';
        $('audio-status').className = 'metric-val';
    }

    // Camera & Audio
    await initCamera();
    await initAudioProctoring();
}

function stopProctoring() {
    document.removeEventListener('visibilitychange', onVisibilityChange);
    window.removeEventListener('blur', onWindowBlur);
    document.removeEventListener('fullscreenchange', onFullscreenChange);
    document.removeEventListener('webkitfullscreenchange', onFullscreenChange);
    document.removeEventListener('mozfullscreenchange', onFullscreenChange);
    document.removeEventListener('MSFullscreenChange', onFullscreenChange);

    if (state.webcamStream) {
        state.webcamStream.getTracks().forEach(t => t.stop());
        state.webcamStream = null;
    }
    if (state.faceDetectionLoop) {
        cancelAnimationFrame(state.faceDetectionLoop);
        state.faceDetectionLoop = null;
    }

    // Stop Audio Proctoring
    if (state.audioLoop) {
        clearInterval(state.audioLoop);
        state.audioLoop = null;
    }
    if (state.audioStream) {
        state.audioStream.getTracks().forEach(t => t.stop());
        state.audioStream = null;
    }
    if (state.audioContext) {
        if (state.audioContext.state !== 'closed') {
            state.audioContext.close();
        }
        state.audioContext = null;
    }

    // Exit fullscreen on exam end
    try {
        if (isFullscreen()) {
            if (document.exitFullscreen) document.exitFullscreen();
            else if (document.webkitExitFullscreen) document.webkitExitFullscreen();
            else if (document.mozCancelFullScreen) document.mozCancelFullScreen();
            else if (document.msExitFullscreen) document.msExitFullscreen();
        }
    } catch(e) {}
}

async function initAudioProctoring() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        state.audioStream = stream;

        const AudioContextClass = window.AudioContext || window.webkitAudioContext;
        state.audioContext = new AudioContextClass();
        const source = state.audioContext.createMediaStreamSource(stream);
        const analyser = state.audioContext.createAnalyser();
        analyser.fftSize = 512;
        source.connect(analyser);

        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        let consecutiveSpikes = 0;
        state.audioLoop = setInterval(async () => {
            if (!state.isRunning) return;

            analyser.getByteFrequencyData(dataArray);

            let sum = 0;
            for (let i = 0; i < bufferLength; i++) {
                sum += dataArray[i];
            }
            const average = sum / bufferLength;
            const amplitude = average / 255;
            const AUDIO_THRESHOLD = 0.12;

            if (amplitude > AUDIO_THRESHOLD) {
                consecutiveSpikes++;
                if (consecutiveSpikes === 4) {
                    await logViolation('AUDIO_SPIKE');
                    showWarnToast('Loud Noise Detected', 'Please maintain a quiet environment.');

                    if ($('audio-status')) {
                        $('audio-status').textContent = 'Loud Noise!';
                        $('audio-status').className = 'metric-val danger';
                    }
                } else if (consecutiveSpikes > 4) {
                    if ($('audio-status')) {
                        $('audio-status').textContent = 'Loud Noise!';
                        $('audio-status').className = 'metric-val danger';
                    }
                }
            } else {
                consecutiveSpikes = 0;
                if ($('audio-status')) {
                    $('audio-status').textContent = 'Normal';
                    $('audio-status').className = 'metric-val safe';
                }
            }
        }, 200);

    } catch (err) {
        console.warn('Microphone access denied for audio proctoring:', err);
        if ($('audio-status')) {
            $('audio-status').textContent = 'Permission Denied';
            $('audio-status').className = 'metric-val danger';
        }
    }
}

function showDisqualifiedOverlay() {
    const overlay = document.createElement('div');
    overlay.id = 'disqualified-overlay';
    overlay.style.position = 'fixed';
    overlay.style.top = '0';
    overlay.style.left = '0';
    overlay.style.width = '100vw';
    overlay.style.height = '100vh';
    overlay.style.backgroundColor = 'rgba(1, 2, 8, 0.9)';
    overlay.style.backdropFilter = 'blur(12px)';
    overlay.style.display = 'flex';
    overlay.style.flexDirection = 'column';
    overlay.style.justifyContent = 'center';
    overlay.style.alignItems = 'center';
    overlay.style.zIndex = '9999';
    overlay.style.color = '#FFFFFF';
    overlay.style.fontFamily = "'Inter', sans-serif";
    overlay.style.animation = 'fadeIn 0.5s ease-out';

    overlay.innerHTML = `
        <div style="text-align: center; max-width: 500px; padding: 40px; border-radius: 16px; background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(239, 68, 68, 0.2); box-shadow: 0 8px 32px 0 rgba(239, 68, 68, 0.1);">
            <div style="width: 80px; height: 80px; border-radius: 50%; background: rgba(239, 68, 68, 0.1); display: flex; justify-content: center; align-items: center; margin: 0 auto 24px auto;">
                <i class="fa-solid fa-ban" style="color: #EF4444; font-size: 40px;"></i>
            </div>
            <h2 style="font-size: 28px; font-weight: 800; margin-bottom: 12px; color: #EF4444; letter-spacing: -0.5px;">Assessment Terminated</h2>
            <p style="font-size: 16px; color: #94A3B8; line-height: 1.6; margin-bottom: 24px;">You have exceeded the maximum limit of 3 tab switches. This assessment has been flagged and auto-terminated.</p>
            <div style="font-size: 14px; color: #64748B;">Redirecting to results dashboard...</div>
        </div>
    `;
    document.body.appendChild(overlay);
}

async function triggerDisqualification() {
    state.isRunning = false;
    stopProctoring();
    showDisqualifiedOverlay();
    try {
        await fetch('/api/final-score', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ candidate_id: state.candidateId })
        });
    } catch (e) {
        console.warn('Error finalizing score during disqualification:', e);
    }
    setTimeout(async () => {
        showView('dashboard');
        await renderDashboard();
    }, 3000);
}

// ── Camera + face-api.js ──────────────────────────────────────────────
async function initCamera() {
    const video  = $('cam-video');
    const canvas = $('cam-canvas');
    const ctx    = canvas.getContext('2d');

    setCamStatus('REQUESTING CAMERA…', 'amber');

    try {
        // Get webcam stream
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' },
            audio: false,
        });
        state.webcamStream = stream;
        video.srcObject   = stream;

        await new Promise(resolve => { video.addEventListener('loadedmetadata', resolve, { once: true }); });
        await video.play();

        canvas.width  = video.videoWidth  || 320;
        canvas.height = video.videoHeight || 240;

        setCamStatus('LOADING AI MODEL…', 'amber');

        // Load face-api.js tiny model from CDN
        try {
            const MODEL_URL = 'https://cdn.jsdelivr.net/npm/@vladmandic/face-api@latest/model';
            await faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL);
            state.faceApiLoaded = true;
            setCamStatus('FACE DETECTION ACTIVE', 'safe');
            startFaceDetectionLoop(video, canvas, ctx);
        } catch (modelErr) {
            console.warn('face-api model load failed, using fallback:', modelErr);
            setCamStatus('CAMERA ACTIVE — NO AI MODEL', 'amber');
            startFallbackDraw(video, canvas, ctx);
        }

    } catch (camErr) {
        console.warn('Camera access denied:', camErr);
        setCamStatus('CAMERA DENIED — BEHAVIORAL ONLY', 'danger');
        startOfflineAnimation(canvas, ctx);
        await logViolation('NO_FACE');
    }
}

// ── Real face detection loop ──────────────────────────────────────────
function startFaceDetectionLoop(video, canvas, ctx) {
    const options = new faceapi.TinyFaceDetectorOptions({ inputSize: 224, scoreThreshold: 0.5 });
    let lastDetectTime = 0;

    async function detect(now) {
        state.faceDetectionLoop = requestAnimationFrame(detect);
        if (!state.isRunning) return;

        // Draw video frame to canvas
        ctx.save();
        ctx.scale(-1, 1);
        ctx.drawImage(video, -canvas.width, 0, canvas.width, canvas.height);
        ctx.restore();
        drawHUDCorners(ctx, canvas);

        // Run detection at most 8 fps
        if (now - lastDetectTime < 125) return;
        lastDetectTime = now;

        try {
            const detections = await faceapi.detectAllFaces(video, options);

            if (detections.length === 0) {
                // No face
                state.noFaceFrames++;
                if (state.noFaceFrames === 6) {    // ~0.75s
                    await logViolation('NO_FACE');
                    showWarnToast('No Face Detected', 'Please stay in camera frame!');
                }
                drawNoFaceOverlay(ctx, canvas);
                setCamStatus('NO FACE DETECTED', 'danger');
                $('face-status').textContent  = 'Not Detected';
                $('face-status').className    = 'metric-val danger';
                $('attention-fill').style.width      = '15%';
                $('attention-fill').style.background = 'var(--red)';
                $('face-count-badge').style.display  = 'none';
                state.multiFaceFrames = 0;
                decayAttention(25);

            } else if (detections.length >= 2) {
                // Multiple faces
                state.multiFaceFrames++;
                if (state.multiFaceFrames === 4) {
                    await logViolation('MULTIPLE_FACES');
                    showWarnToast('Multiple Faces', 'Only the candidate should be visible!');
                }
                drawFaceBoxes(ctx, canvas, detections, '#EF4444');
                setCamStatus('MULTIPLE FACES DETECTED', 'danger');
                $('face-status').textContent  = `${detections.length} Faces!`;
                $('face-status').className    = 'metric-val danger';
                $('face-count-badge').style.display = 'flex';
                $('face-count-num').textContent     = detections.length;
                state.noFaceFrames = 0;
                decayAttention(15);

            } else {
                // Exactly one face — GOOD
                state.noFaceFrames    = 0;
                state.multiFaceFrames = 0;
                drawFaceBoxes(ctx, canvas, detections, '#10B981');
                setCamStatus('FACE VERIFIED', 'safe');
                $('face-status').textContent = 'Detected';
                $('face-status').className   = 'metric-val safe';
                $('face-count-badge').style.display = 'none';

                // Restore attention
                state.attentionScore = Math.min(100, state.attentionScore + 3);
                const pct = state.attentionScore;
                $('attention-fill').style.width = `${pct}%`;
                const clr = pct > 70 ? 'linear-gradient(90deg, var(--green), var(--cyan))' : 'linear-gradient(90deg, var(--amber), var(--red))';
                $('attention-fill').style.background = clr;
            }
        } catch (e) {
            // Silently ignore per-frame errors
        }
    }

    requestAnimationFrame(detect);
}

function drawFaceBoxes(ctx, canvas, detections, color) {
    detections.forEach(d => {
        const box = d.box;
        // Mirror the x coordinate to match the mirrored video
        const mirroredX = canvas.width - box.x - box.width;
        ctx.strokeStyle = color;
        ctx.lineWidth   = 2;
        ctx.shadowColor = color; ctx.shadowBlur = 12;
        ctx.strokeRect(mirroredX, box.y, box.width, box.height);
        ctx.shadowBlur = 0;

        // Label
        ctx.fillStyle = color;
        ctx.font = 'bold 11px JetBrains Mono, monospace';
        ctx.fillText(detections.length === 1 ? 'FACE VERIFIED' : 'FACE', mirroredX, box.y > 14 ? box.y - 4 : box.y + 14);
    });
    drawHUDCorners(ctx, canvas);
}

function drawNoFaceOverlay(ctx, canvas) {
    ctx.fillStyle = 'rgba(239,68,68,0.07)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = 'rgba(239,68,68,0.5)';
    ctx.lineWidth = 2;
    ctx.strokeRect(4, 4, canvas.width - 8, canvas.height - 8);
}

function drawHUDCorners(ctx, canvas) {
    const c = 'rgba(79,127,255,0.6)', len = 20;
    ctx.strokeStyle = c; ctx.lineWidth = 2; ctx.shadowColor = 'rgba(79,127,255,0.4)'; ctx.shadowBlur = 6;
    [[0, 0, 1, 0, 0, 1], [canvas.width, 0, -1, 0, 0, 1],
     [0, canvas.height, 1, 0, 0, -1], [canvas.width, canvas.height, -1, 0, 0, -1]]
    .forEach(([x, y, dx1, dy1, dx2, dy2]) => {
        ctx.beginPath(); ctx.moveTo(x + dx1 * 8, y + dy1 * 8);
        ctx.lineTo(x + dx1 * (8 + len), y + dy1 * (8 + len)); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(x + dx2 * 8, y + dy2 * 8);
        ctx.lineTo(x + dx2 * (8 + len), y + dy2 * (8 + len)); ctx.stroke();
    });
    ctx.shadowBlur = 0;
}

// ── Fallback: draw live video without AI detection ─────────────────────
function startFallbackDraw(video, canvas, ctx) {
    function frame() {
        if (!state.isRunning) return;
        state.faceDetectionLoop = requestAnimationFrame(frame);
        ctx.save(); ctx.scale(-1, 1);
        ctx.drawImage(video, -canvas.width, 0, canvas.width, canvas.height);
        ctx.restore();
        drawHUDCorners(ctx, canvas);
    }
    requestAnimationFrame(frame);
}

// ── Offline: animated wireframe when camera not available ──────────────
function startOfflineAnimation(canvas, ctx) {
    let angle = 0;
    function frame() {
        if (!state.isRunning) return;
        state.faceDetectionLoop = requestAnimationFrame(frame);
        angle += 0.04;

        ctx.fillStyle = '#010208'; ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.strokeStyle = 'rgba(79,127,255,0.06)'; ctx.lineWidth = 1;
        for (let x = 0; x < canvas.width; x += 22) { ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x, canvas.height); ctx.stroke(); }
        for (let y = 0; y < canvas.height; y += 22) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(canvas.width, y); ctx.stroke(); }

        const cx = canvas.width / 2, cy = canvas.height / 2 + 5;
        ctx.strokeStyle = '#4F7FFF'; ctx.shadowColor = '#4F7FFF'; ctx.shadowBlur = 6; ctx.lineWidth = 1.5;
        ctx.beginPath(); ctx.ellipse(cx, cy, 60 + Math.sin(angle) * 2, 78, 0, 0, 2 * Math.PI); ctx.stroke();
        ctx.beginPath(); ctx.ellipse(cx - 20, cy - 22, 9, 5, 0, 0, 2 * Math.PI); ctx.stroke();
        ctx.beginPath(); ctx.ellipse(cx + 20, cy - 22, 9, 5, 0, 0, 2 * Math.PI); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(cx, cy - 20); ctx.lineTo(cx - 5, cy + 10); ctx.lineTo(cx + 5, cy + 10); ctx.closePath(); ctx.stroke();
        ctx.beginPath(); ctx.ellipse(cx, cy + 34, 14 + Math.cos(angle) * 2, 5, 0, 0, 2 * Math.PI); ctx.stroke();
        ctx.shadowBlur = 0;
        drawHUDCorners(ctx, canvas);
    }
    requestAnimationFrame(frame);
}

// ── Helpers ────────────────────────────────────────────────────────────
function setCamStatus(text, type) {
    $('cam-status-text').textContent = text;
    const dot = $('cam-status-dot');
    dot.className = 'cam-status-dot';
    if (type) dot.classList.add(type);
}

function decayAttention(amount) {
    state.attentionScore = Math.max(0, state.attentionScore - amount);
    $('attention-fill').style.width = `${state.attentionScore}%`;
    $('attention-fill').style.background = 'var(--red)';
}

function showWarnToast(title, msg) {
    $('warn-title').textContent = title;
    $('warn-msg').textContent   = msg;
    const t = $('warn-toast');
    t.classList.remove('hidden');
    setTimeout(() => t.classList.add('hidden'), 4500);
}

// ── Tab / window violations ────────────────────────────────────────────
async function onVisibilityChange() {
    if (document.visibilityState === 'hidden' && state.isRunning) {
        state.tabSwitchesCount = (state.tabSwitchesCount || 0) + 1;
        await logViolation('TAB_SWITCH');
        if (state.tabSwitchesCount >= 3) {
            showWarnToast('Assessment Terminated', 'Exceeded maximum tab switch limit.');
            await triggerDisqualification();
        } else {
            showWarnToast('Tab Switch Detected', `Switching tabs is a proctoring violation! Warning ${state.tabSwitchesCount}/3.`);
        }
    }
}
async function onWindowBlur() {
    if (state.isRunning) {
        await logViolation('WINDOW_DEFOCUS');
    }
}

async function logViolation(type) {
    try {
        const res  = await fetch('/api/proctoring-verdict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ candidate_id: state.candidateId, event_type: type })
        });
        if (!res.ok) return;
        const data = await res.json();

        state.violationCount = data.violations_count ?? (state.violationCount + 1);
        $('violation-count').textContent = state.violationCount;

        const intEl = $('integrity-status');
        if (data.risk_score >= 60) {
            intEl.textContent = 'HIGH RISK'; intEl.className = 'metric-val danger';
        } else if (data.risk_score >= 30) {
            intEl.textContent = 'WARNING'; intEl.className = 'metric-val';
            intEl.style.color = 'var(--amber)';
        } else {
            intEl.textContent = 'SECURE'; intEl.className = 'metric-val safe';
        }
    } catch (err) {
        console.warn('Proctoring log error:', err);
    }
}

// ── Restart ────────────────────────────────────────────────────────────
$('btn-restart').addEventListener('click', () => {
    stopProctoring();
    state.candidateId = null;
    const overlay = document.getElementById('disqualified-overlay');
    if (overlay) overlay.remove();
    $('reg-form').reset();
    $('topbar-status').classList.add('hidden');
    showView('welcome');
});
