function colorForScore(value, max) {
    const ratio = max ? value / max : 0;
    const opacity = 0.18 + ratio * 0.72;
    return `linear-gradient(180deg, rgba(23, 232, 143, ${opacity}), rgba(10, 34, 28, 0.95))`;
}

export function renderHeatmap(container, patterns) {
    const topPatterns = patterns.slice(0, 10);
    const maxCount = Math.max(...topPatterns.map((item) => item.occurrence_count), 1);
    container.innerHTML = topPatterns.map((item) => `
        <div class="heatmap-cell" style="background:${colorForScore(item.occurrence_count, maxCount)}">
            <div class="heatmap-meta">
                <span class="heatmap-label">${item.asset_id}</span>
                <span class="heatmap-label">${item.problem_code}</span>
            </div>
            <span class="heatmap-value">${item.occurrence_count}</span>
            <div class="heatmap-footer">
                <span class="heatmap-label">Regularity ${item.regularity_score.toFixed(2)}</span>
            </div>
        </div>
    `).join('');
}