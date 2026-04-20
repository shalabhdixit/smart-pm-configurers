export function renderPredictionsTable(container, patterns, predictions) {
    const predictionMap = new Map(predictions.map((item) => [item.pattern_key, item]));
    const rows = patterns.slice(0, 10).map((pattern) => {
        const prediction = predictionMap.get(pattern.pattern_key);
        const score = prediction ? prediction.recurrence_probability_90d : 0;
        return `
            <div class="prediction-row">
                <div class="flex items-center justify-between gap-3">
                    <div>
                        <p class="font-semibold">${pattern.asset_id}</p>
                        <p class="text-sm text-slate-300">${pattern.problem_code} | ${pattern.location_id}</p>
                    </div>
                    <span class="text-lg font-bold">${Math.round(score * 100)}%</span>
                </div>
                <div class="probability-bar"><span style="width:${score * 100}%"></span></div>
            </div>
        `;
    });
    container.innerHTML = rows.join('');
}