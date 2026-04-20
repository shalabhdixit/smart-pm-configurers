export function renderKpiCards(container, kpis) {
    const items = [
        { label: 'Reactive WOs Analyzed', value: kpis.total_work_orders, trend: '2-year work-order history mined' },
        { label: 'Recurring Patterns Detected', value: kpis.recurring_patterns, trend: 'Top 20% cost drivers surfaced' },
        { label: 'PM Schedules Auto-Generated', value: kpis.generated_pm_schedules, trend: 'Zero-click PM conversion' },
        { label: 'Estimated Cost Savings', value: `$${Number(kpis.estimated_cost_savings).toLocaleString()}`, trend: 'Based on 35% savings target' },
        { label: 'Predictions In Next 30 Days', value: kpis.predictions_next_30_days, trend: 'Assets likely to fail soon' },
    ];

    container.innerHTML = items.map((item) => `
        <article class="kpi-card">
            <p class="kpi-label">${item.label}</p>
            <h3 class="kpi-value">${item.value}</h3>
            <p class="kpi-trend">${item.trend}</p>
        </article>
    `).join('');
}