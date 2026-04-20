import { renderKpiCards } from '../components/kpi_cards.js';
import { renderHeatmap } from '../components/heatmap.js';
import { renderPredictionsTable } from '../components/predictions_table.js';

const API_BASE = 'http://127.0.0.1:8000/api/v1';
const INITIAL_QUICK_ACTIONS = [
    { id: 'welcome', label: 'Launch Brief', prompt: 'Give me a concise launch brief for this portfolio.' },
    { id: 'executive-summary', label: 'Executive Summary', prompt: 'Summarize the portfolio for leadership and focus on business impact.' },
    { id: 'top-risk-assets', label: 'Top Risk Assets', prompt: 'Identify the top risk assets and what should happen next.' },
    { id: 'pm-opportunities', label: 'PM Opportunities', prompt: 'Recommend the best PM opportunities to prevent avoidable breakdowns.' },
];

const FOLLOW_UP_LIBRARY = {
    welcome: [
        { id: 'executive-summary', label: 'Leadership view', prompt: 'Summarize the portfolio for leadership and focus on business impact.' },
        { id: 'top-risk-assets', label: 'Top asset risks', prompt: 'Identify the top risk assets and what should happen next.' },
    ],
    'executive-summary': [
        { id: 'top-risk-assets', label: 'Drill into risks', prompt: 'Identify the top risk assets and what should happen next.' },
        { id: 'pm-opportunities', label: 'PM actions', prompt: 'Recommend the best PM opportunities to prevent avoidable breakdowns.' },
        { id: 'occupant-impact', label: 'Occupant impact', prompt: 'Explain where occupant experience is most exposed and what to do first.' },
    ],
    'top-risk-assets': [
        { id: 'pm-opportunities', label: 'Prevent the failures', prompt: 'Recommend the best PM opportunities to prevent avoidable breakdowns.' },
        { id: 'occupant-impact', label: 'Service impact', prompt: 'Explain where occupant experience is most exposed and what to do first.' },
        { id: 'executive-summary', label: 'Executive recap', prompt: 'Summarize the portfolio for leadership and focus on business impact.' },
    ],
    'pm-opportunities': [
        { id: 'top-risk-assets', label: 'Assets behind PMs', prompt: 'Identify the top risk assets and what should happen next.' },
        { id: 'executive-summary', label: 'Value story', prompt: 'Summarize the portfolio for leadership and focus on business impact.' },
    ],
    'occupant-impact': [
        { id: 'top-risk-assets', label: 'Assets causing impact', prompt: 'Identify the top risk assets and what should happen next.' },
        { id: 'pm-opportunities', label: 'Prevention plan', prompt: 'Recommend the best PM opportunities to prevent avoidable breakdowns.' },
    ],
    custom: [
        { id: 'executive-summary', label: 'Summarize for SLT', prompt: 'Summarize the portfolio for leadership and focus on business impact.' },
        { id: 'top-risk-assets', label: 'What is most at risk?', prompt: 'Identify the top risk assets and what should happen next.' },
    ],
};

let authToken = '';
let timelineChart;
let assistantBusy = false;
let loaderProgressTimer;

const elements = {
    kpiGrid: document.getElementById('kpi-grid'),
    portfolioBar: document.getElementById('portfolio-bar'),
    topPattern: document.getElementById('top-pattern'),
    timelineChart: document.getElementById('timeline-chart'),
    pmSchedules: document.getElementById('pm-schedules'),
    explainability: document.getElementById('explainability-panel'),
    liveFeed: document.getElementById('live-feed-list'),
    refreshButton: document.getElementById('refresh-button'),
    runPipelineButton: document.getElementById('run-pipeline-button'),
    generateButton: document.getElementById('generate-button'),
    statusMessage: document.getElementById('status-message'),
    statusBadge: document.getElementById('status-badge'),
    loader: document.getElementById('app-loader'),
    loaderTitle: document.getElementById('loader-title'),
    loaderMessage: document.getElementById('loader-message'),
    loaderProgressBar: document.getElementById('loader-progress-bar'),
    loaderStepIngest: document.getElementById('loader-step-ingest'),
    loaderStepPatterns: document.getElementById('loader-step-patterns'),
    loaderStepPredictions: document.getElementById('loader-step-predictions'),
    loaderStepPm: document.getElementById('loader-step-pm'),
    assistantShell: document.getElementById('assistant-shell'),
    assistantToggle: document.getElementById('assistant-toggle'),
    assistantProvider: document.getElementById('assistant-provider'),
    assistantChiplets: document.getElementById('assistant-chiplets'),
    assistantPredictiveGroup: document.getElementById('assistant-predictive-group'),
    assistantPredictiveChiplets: document.getElementById('assistant-predictive-chiplets'),
    assistantMessages: document.getElementById('assistant-messages'),
    assistantForm: document.getElementById('assistant-form'),
    assistantInput: document.getElementById('assistant-input'),
    assistantSend: document.getElementById('assistant-send'),
};

const appState = {
    intelligenceGenerated: false,
    assistantPrimed: false,
    assistantHistory: [],
};

async function api(path, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
    };
    if (options.headers) {
        Object.assign(headers, options.headers);
    }
    const response = await fetch(`${API_BASE}${path}`, {
        ...options,
        headers,
    });
    if (!response.ok) {
        const text = await response.text();
        throw new Error(`${response.status}: ${text}`);
    }
    return response.json();
}

async function bootstrap() {
    const token = await api('/auth/token', { method: 'POST' });
    authToken = token.access_token;
    renderQuickActions(INITIAL_QUICK_ACTIONS);
    renderAssistantPlaceholder();
    await loadOverviewOnly();
}

async function loadOverviewOnly() {
    const [overview, workOrders] = await Promise.all([
        api('/portfolio/overview'),
        api('/work-orders'),
    ]);
    renderPortfolioBar(overview);
    renderLiveFeed(workOrders);
    renderPreGenerationState();
    elements.statusMessage.textContent = 'Portfolio reference data is ready. Click Generate Intelligence when you want to score patterns and create PM recommendations.';
    elements.statusBadge.textContent = 'Awaiting generation';
    elements.generateButton.disabled = true;
    appState.intelligenceGenerated = false;
}

async function loadDashboard() {
    const [kpis, patterns, predictions, schedules, workOrders, overview] = await Promise.all([
        api('/dashboard/kpis'),
        api('/patterns'),
        api('/predictions'),
        api('/pm/schedules'),
        api('/work-orders'),
        api('/portfolio/overview'),
    ]);
    renderPortfolioBar(overview);
    renderKpiCards(elements.kpiGrid, kpis);
    renderHeatmap(document.getElementById('heatmap-grid'), patterns);
    renderPredictionsTable(document.getElementById('predictions-table'), patterns, predictions);
    renderPmSchedules(schedules, patterns);
    renderExplainability(predictions, patterns);
    renderLiveFeed(workOrders);
    renderTimelineChart(patterns);
    elements.topPattern.textContent = kpis.top_pattern_key || 'No dominant pattern yet';
    elements.statusMessage.textContent = 'Intelligence has been generated. Refresh the view, ask the copilot targeted questions, or generate PM schedules from the scored patterns.';
    elements.statusBadge.textContent = 'Intelligence ready';
    elements.generateButton.disabled = false;
    appState.intelligenceGenerated = true;
}

async function generateIntelligence() {
    appState.assistantPrimed = false;
    setLoaderState({
        visible: true,
        title: 'Generating intelligence',
        message: 'Preparing work orders and analytics context.',
        progress: 8,
        activeStep: 'ingest',
    });
    startLoaderProgress();
    try {
        await advanceLoaderStep('patterns', 28, 'Detecting recurring maintenance patterns across the portfolio.');
        await api('/pipeline/run', { method: 'POST' });
        await advanceLoaderStep('predictions', 72, 'Scoring 30, 60, and 90 day recurrence risk.');
        await loadDashboard();
        await advanceLoaderStep('pm', 100, 'Dashboard refreshed with live intelligence outputs.');
        if (elements.assistantShell.classList.contains('assistant-open')) {
            await primeAssistant();
        }
    } finally {
        stopLoaderProgress();
        globalThis.setTimeout(() => setLoaderState({ visible: false }), 250);
    }
}

async function primeAssistant() {
    if (appState.assistantPrimed || !appState.intelligenceGenerated) {
        return;
    }
    appState.assistantPrimed = true;
    renderAssistantPlaceholder();
    renderPredictiveActions();
}

async function advanceLoaderStep(step, progress, message) {
    const titles = {
        patterns: 'Detecting patterns',
        predictions: 'Scoring recurrence risk',
        pm: 'Refreshing the dashboard',
    };
    setLoaderState({ title: titles[step], message, progress, activeStep: step, visible: true });
    await Promise.resolve();
}

function renderPortfolioBar(overview) {
    const items = [
        {
            label: 'Portfolio Footprint',
            value: `${overview.facilities} sites`,
            copy: `${overview.assets} assets and ${overview.technicians} technicians indexed for planning-ready context.`,
        },
        {
            label: 'Hotspot Facility',
            value: overview.top_facilities[0]?.facility_name || 'Awaiting load',
            copy: overview.top_facilities[0]
                ? `${overview.top_facilities[0].reactive_work_orders} reactive work orders and ${overview.top_facilities[0].high_risk_patterns} high-risk patterns.`
                : 'No portfolio hotspot available yet.',
        },
        {
            label: 'Most Exposed Asset',
            value: overview.at_risk_assets[0]?.asset_name || 'Awaiting scoring',
            copy: overview.at_risk_assets[0]
                ? `${Math.round(overview.at_risk_assets[0].recurrence_probability_90d * 100)}% 90-day recurrence risk. ${overview.at_risk_assets[0].recommended_action}.`
                : 'Run the analytics pipeline to score the portfolio.',
        },
    ];
    elements.portfolioBar.innerHTML = items.map((item) => `
        <article class="overview-card">
            <p class="panel-kicker">${escapeHtml(item.label)}</p>
            <h3 class="overview-value">${escapeHtml(item.value)}</h3>
            <p class="overview-copy">${escapeHtml(item.copy)}</p>
        </article>
    `).join('');
}

function renderPreGenerationState() {
    if (timelineChart) {
        timelineChart.destroy();
        timelineChart = null;
    }
    elements.kpiGrid.innerHTML = Array.from({ length: 5 }, (_, index) => `
        <article class="kpi-card kpi-card-muted">
            <p class="kpi-label">Metric ${index + 1}</p>
            <h3 class="kpi-value">--</h3>
            <p class="kpi-trend">Available after intelligence generation</p>
        </article>
    `).join('');
    document.getElementById('heatmap-grid').innerHTML = renderEmptyStateCard('Generate intelligence to map asset hotspots.');
    document.getElementById('predictions-table').innerHTML = renderEmptyStateCard('Predicted failure risks appear here after generation.');
    elements.pmSchedules.innerHTML = renderEmptyStateCard('Click Generate Intelligence first, then Generate PM Schedules.');
    elements.explainability.innerHTML = renderEmptyStateCard('Prediction drivers will appear once risk scoring completes.');
    elements.topPattern.textContent = 'Awaiting generation';
    const chartContext = elements.timelineChart.getContext('2d');
    chartContext.clearRect(0, 0, elements.timelineChart.width, elements.timelineChart.height);
}

function renderEmptyStateCard(message) {
    return `<div class="empty-state"><p>${escapeHtml(message)}</p></div>`;
}

function renderPmSchedules(schedules, patterns) {
    const patternMap = new Map(patterns.map((item) => [item.pattern_key, item]));
    if (!schedules.length) {
        elements.pmSchedules.innerHTML = renderEmptyStateCard('No PM schedules generated yet. Click Generate PM Schedules to create them from the current intelligence.');
        return;
    }
    elements.pmSchedules.innerHTML = schedules.slice(0, 8).map((schedule) => {
        const pattern = patternMap.get(schedule.pattern_key);
        return `
            <article class="pm-card">
                <div class="flex items-start justify-between gap-3">
                    <div>
                        <p class="font-semibold">${escapeHtml(schedule.pm_title)}</p>
                        <p class="text-sm text-slate-300">${escapeHtml(pattern?.location_id || '')} | ${escapeHtml(schedule.frequency)}</p>
                    </div>
                    <span class="signal-pill success">${escapeHtml(schedule.priority)}</span>
                </div>
                <div class="mt-3 text-sm text-slate-300">
                    <p>Next due: ${escapeHtml(schedule.next_due_date)}</p>
                    <p>Estimated duration: ${escapeHtml(schedule.estimated_duration)} hrs</p>
                    <p>Skill: ${escapeHtml(schedule.assigned_skill_set)}</p>
                </div>
            </article>
        `;
    }).join('');
}

function renderExplainability(predictions, patterns) {
    const patternMap = new Map(patterns.map((item) => [item.pattern_key, item]));
    elements.explainability.innerHTML = predictions.slice(0, 4).map((prediction) => {
        const pattern = patternMap.get(prediction.pattern_key);
        const metrics = Object.entries(prediction.explanation)
            .filter(([key]) => key !== 'model_auc_roc')
            .slice(0, 5)
            .map(([key, value]) => `<div class="explain-metric"><span>${escapeHtml(key.replaceAll('_', ' '))}</span><span>${Number(value).toFixed(2)}</span></div>`)
            .join('');
        return `
            <article class="explain-card">
                <p class="font-semibold">${escapeHtml(pattern?.asset_id || prediction.pattern_key)}</p>
                <p class="text-sm text-slate-300">Predicted 90-day risk: ${Math.round(prediction.recurrence_probability_90d * 100)}%</p>
                ${metrics}
            </article>
        `;
    }).join('');
}

function renderLiveFeed(workOrders) {
    elements.liveFeed.innerHTML = workOrders.slice(0, 8).map((item) => `
        <div class="feed-row">
            <div class="flex items-center justify-between gap-3">
                <p class="font-semibold">${escapeHtml(item.work_order_id)}</p>
                <span class="text-sm text-slate-300">${escapeHtml(item.priority)}</span>
            </div>
            <p class="text-sm text-slate-300 mt-2">${escapeHtml(item.asset_id)} | ${escapeHtml(item.problem_code)}</p>
            <p class="text-xs text-slate-400 mt-1">${new Date(item.created_date).toLocaleString()}</p>
        </div>
    `).join('');
}

function renderTimelineChart(patterns) {
    const topPatterns = patterns.slice(0, 3);
    if (!topPatterns.length) {
        return;
    }
    const labels = Array.from(new Set(topPatterns.flatMap((pattern) => pattern.timeline))).sort((left, right) => new Date(left) - new Date(right));
    const datasets = topPatterns.map((pattern, index) => ({
        label: `${pattern.asset_id} ${pattern.problem_code}`,
        data: labels.map((label) => (pattern.timeline.includes(label) ? pattern.regularity_score : null)),
        borderColor: ['#17e88f', '#ffd166', '#ff7a8a'][index],
        backgroundColor: 'transparent',
        tension: 0.3,
    }));
    if (timelineChart) {
        timelineChart.destroy();
    }
    timelineChart = new Chart(elements.timelineChart, {
        type: 'line',
        data: { labels: labels.map((label) => new Date(label).toLocaleDateString()), datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: '#d8ebe4' } } },
            scales: {
                x: { ticks: { color: '#8fb0a5' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                y: { ticks: { color: '#8fb0a5' }, grid: { color: 'rgba(255,255,255,0.05)' } },
            },
        },
    });
}

function renderQuickActions(actions) {
    elements.assistantChiplets.innerHTML = actions.map((item) => `
        <button class="assistant-chip" type="button" data-action="${escapeAttribute(item.id)}" data-prompt="${escapeAttribute(item.prompt)}">${escapeHtml(item.label)}</button>
    `).join('');
}

function renderPredictiveActions() {
    const suggestions = buildPredictiveActions();
    elements.assistantPredictiveGroup.classList.toggle('is-hidden', suggestions.length === 0);
    elements.assistantPredictiveChiplets.innerHTML = suggestions.map((item) => `
        <button class="assistant-chip assistant-chip-secondary" type="button" data-action="${escapeAttribute(item.id)}" data-prompt="${escapeAttribute(item.prompt)}">${escapeHtml(item.label)}</button>
    `).join('');
}

function renderAssistantPlaceholder() {
    elements.assistantMessages.innerHTML = `
        <section class="assistant-starter-card">
            <div class="assistant-starter-icon"><i class="fa-solid fa-wave-square"></i></div>
            <div>
                <p class="assistant-starter-title">Portfolio copilot is ready</p>
                <p class="assistant-starter-copy">Use a quick action or ask a targeted question. The best results come after intelligence generation.</p>
            </div>
        </section>
    `;
    elements.assistantProvider.textContent = 'mock';
}

function addAssistantMessage(role, message, meta = '') {
    const wrapper = document.createElement('article');
    wrapper.className = `assistant-message ${role}`;
    const metaHtml = meta ? `<small>${escapeHtml(meta)}</small>` : '';
    wrapper.innerHTML = formatAssistantText(message) + metaHtml;
    elements.assistantMessages.appendChild(wrapper);
    elements.assistantMessages.scrollTop = elements.assistantMessages.scrollHeight;
}

function setAssistantBusy(isBusy) {
    assistantBusy = isBusy;
    elements.assistantSend.disabled = isBusy;
    if (!isBusy) {
        return;
    }
    const loader = document.createElement('article');
    loader.className = 'assistant-message bot';
    loader.id = 'assistant-loading';
    loader.innerHTML = '<div class="assistant-loading">Thinking with live portfolio context</div>';
    elements.assistantMessages.appendChild(loader);
    elements.assistantMessages.scrollTop = elements.assistantMessages.scrollHeight;
}

function clearAssistantBusy() {
    assistantBusy = false;
    elements.assistantSend.disabled = false;
    document.getElementById('assistant-loading')?.remove();
}

async function requestAssistant(payload, addUserBubble = true) {
    if (assistantBusy) {
        return;
    }
    if (!appState.intelligenceGenerated) {
        elements.assistantMessages.innerHTML = `
            <section class="assistant-starter-card assistant-starter-warning">
                <div class="assistant-starter-icon"><i class="fa-solid fa-bolt"></i></div>
                <div>
                    <p class="assistant-starter-title">Generate intelligence first</p>
                    <p class="assistant-starter-copy">The copilot answers against live patterns, risk scores, and PM recommendations only after generation.</p>
                </div>
            </section>
        `;
        return;
    }
    if (addUserBubble && payload.message) {
        addAssistantMessage('user', payload.message);
    }
    rememberAssistantInteraction(payload);
    setAssistantBusy(true);
    try {
        const response = await api('/assistant/chat', {
            method: 'POST',
            body: JSON.stringify(payload),
        });
        clearAssistantBusy();
        elements.assistantProvider.textContent = `${response.provider} • ${response.model}`;
        renderQuickActions(INITIAL_QUICK_ACTIONS);
        renderPredictiveActions();
        addAssistantMessage('bot', response.message, 'Grounded in live portfolio data');
    } catch (error) {
        clearAssistantBusy();
        addAssistantMessage('bot', `Assistant unavailable: ${error.message}`);
    }
}

function rememberAssistantInteraction(payload) {
    const action = inferAssistantIntent(payload);
    appState.assistantHistory.push({
        action,
        message: payload.message || '',
    });
    if (appState.assistantHistory.length > 6) {
        appState.assistantHistory = appState.assistantHistory.slice(-6);
    }
}

function inferAssistantIntent(payload) {
    if (payload.action && payload.action !== 'custom') {
        return payload.action;
    }
    const message = String(payload.message || '').toLowerCase();
    if (message.includes('executive') || message.includes('leadership') || message.includes('slt')) {
        return 'executive-summary';
    }
    if (message.includes('risk') || message.includes('asset')) {
        return 'top-risk-assets';
    }
    if (message.includes('pm') || message.includes('preventive') || message.includes('schedule')) {
        return 'pm-opportunities';
    }
    if (message.includes('occupant') || message.includes('tenant') || message.includes('comfort')) {
        return 'occupant-impact';
    }
    return 'custom';
}

function buildPredictiveActions() {
    if (!appState.intelligenceGenerated) {
        return [];
    }
    const latest = appState.assistantHistory.at(-1)?.action || 'welcome';
    const candidates = FOLLOW_UP_LIBRARY[latest] || FOLLOW_UP_LIBRARY.custom;
    const recentIds = new Set(appState.assistantHistory.slice(-3).map((item) => item.action));
    const filtered = candidates.filter((item) => !recentIds.has(item.id));
    const fallbackPool = [...(FOLLOW_UP_LIBRARY.custom || []), ...INITIAL_QUICK_ACTIONS];
    const result = [...filtered];
    for (const item of fallbackPool) {
        if (result.length >= 3) {
            break;
        }
        if (recentIds.has(item.id) || result.some((existing) => existing.id === item.id)) {
            continue;
        }
        result.push(item);
    }
    return result.slice(0, 3);
}

function startLoaderProgress() {
    stopLoaderProgress();
    loaderProgressTimer = globalThis.setInterval(() => {
        const current = Number(elements.loaderProgressBar.dataset.progress || '0');
        if (current >= 88) {
            return;
        }
        setLoaderState({ progress: current + 2 });
    }, 220);
}

function stopLoaderProgress() {
    if (loaderProgressTimer) {
        globalThis.clearInterval(loaderProgressTimer);
        loaderProgressTimer = undefined;
    }
}

function setLoaderState({ title, message, progress, activeStep, visible }) {
    if (typeof visible === 'boolean') {
        elements.loader.classList.toggle('hidden', !visible);
        elements.loader.setAttribute('aria-hidden', String(!visible));
    }
    if (title) {
        elements.loaderTitle.textContent = title;
    }
    if (message) {
        elements.loaderMessage.textContent = message;
    }
    if (typeof progress === 'number') {
        const safeProgress = Math.max(0, Math.min(100, progress));
        elements.loaderProgressBar.style.width = `${safeProgress}%`;
        elements.loaderProgressBar.dataset.progress = String(safeProgress);
    }
    if (activeStep) {
        const order = ['ingest', 'patterns', 'predictions', 'pm'];
        const nodes = {
            ingest: elements.loaderStepIngest,
            patterns: elements.loaderStepPatterns,
            predictions: elements.loaderStepPredictions,
            pm: elements.loaderStepPm,
        };
        const activeIndex = order.indexOf(activeStep);
        order.forEach((key, index) => {
            nodes[key].classList.toggle('active', key === activeStep);
            nodes[key].classList.toggle('complete', index < activeIndex);
        });
    }
}

function escapeHtml(value) {
    return String(value)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
}

function escapeAttribute(value) {
    return escapeHtml(value).replaceAll('`', '&#96;');
}

function formatAssistantText(message) {
    return escapeHtml(message)
        .split('\n')
        .map((line) => (line.startsWith('- ') ? `• ${line.slice(2)}` : line))
        .join('<br>');
}

elements.refreshButton.addEventListener('click', async () => {
    if (appState.intelligenceGenerated) {
        await loadDashboard();
        return;
    }
    await loadOverviewOnly();
});

elements.runPipelineButton.addEventListener('click', async () => {
    await generateIntelligence();
});

elements.generateButton.addEventListener('click', async () => {
    if (!appState.intelligenceGenerated) {
        elements.statusMessage.textContent = 'Generate Intelligence first. PM schedules depend on scored recurring patterns.';
        elements.statusBadge.textContent = 'Action required';
        return;
    }
    await api('/pm/generate', { method: 'POST' });
    await loadDashboard();
    await requestAssistant({ action: 'pm-opportunities', message: 'Refresh PM opportunities after the latest schedule generation.' });
});

elements.assistantToggle.addEventListener('click', () => {
    elements.assistantShell.classList.toggle('assistant-open');
    if (elements.assistantShell.classList.contains('assistant-open')) {
        void primeAssistant();
    }
});

elements.assistantChiplets.addEventListener('click', async (event) => {
    const button = event.target.closest('[data-action]');
    if (!button) {
        return;
    }
    await requestAssistant({
        action: button.dataset.action,
        message: button.dataset.prompt || 'Share the latest insight.',
    });
});

elements.assistantPredictiveChiplets.addEventListener('click', async (event) => {
    const button = event.target.closest('[data-action]');
    if (!button) {
        return;
    }
    await requestAssistant({
        action: button.dataset.action,
        message: button.dataset.prompt || 'Share the next recommended insight.',
    });
});

elements.assistantInput.addEventListener('keydown', async (event) => {
    if (event.key !== 'Enter' || event.shiftKey) {
        return;
    }
    event.preventDefault();
    if (assistantBusy) {
        return;
    }
    elements.assistantForm.requestSubmit();
});

elements.assistantForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const message = elements.assistantInput.value.trim();
    if (!message) {
        return;
    }
    elements.assistantInput.value = '';
    await requestAssistant({ message, action: 'custom' });
});

try {
    await bootstrap();
} catch (error) {
    console.error(error);
    elements.kpiGrid.innerHTML = `<div class="kpi-card"><p class="kpi-label">Connection issue</p><h3 class="kpi-value">API offline</h3><p class="kpi-trend">${escapeHtml(error.message)}</p></div>`;
    addAssistantMessage('bot', `Dashboard bootstrap failed: ${error.message}`);
}