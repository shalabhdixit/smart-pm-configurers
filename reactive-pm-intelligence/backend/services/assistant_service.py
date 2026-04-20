from __future__ import annotations

from textwrap import dedent

import httpx
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.models.database import PatternRecord, PredictionRecord
from backend.models.schemas import AssistantRequest
from backend.services.portfolio_service import build_portfolio_overview


settings = get_settings()

QUICK_ACTIONS = [
    {
        "id": "welcome",
        "label": "Launch Brief",
        "prompt": "Give me a concise launch brief for this portfolio.",
    },
    {
        "id": "executive-summary",
        "label": "Executive Summary",
        "prompt": "Summarize the portfolio for leadership and focus on business impact.",
    },
    {
        "id": "top-risk-assets",
        "label": "Top Risk Assets",
        "prompt": "Identify the top risk assets and what should happen next.",
    },
    {
        "id": "pm-opportunities",
        "label": "PM Opportunities",
        "prompt": "Recommend the best PM opportunities to prevent avoidable breakdowns.",
    },
    {
        "id": "occupant-impact",
        "label": "Occupant Impact",
        "prompt": "Explain where occupant experience is most exposed and what to do first.",
    },
]

ACTION_GUIDANCE = {
    "welcome": "Start with a launch-ready summary. Keep it confident, specific, and grounded in the data.",
    "executive-summary": "Frame the answer for SLT. Mention business value, operating risk, and recommended focus areas.",
    "top-risk-assets": "Prioritize the top at-risk assets, why they are at risk, and the next maintenance move.",
    "pm-opportunities": "Focus on PM conversion opportunities, scheduling urgency, and savings impact.",
    "occupant-impact": "Focus on tenant comfort, service disruption, and the highest-visibility facility issues.",
}


async def generate_assistant_response(session: Session, payload: AssistantRequest) -> dict:
    """Generate an assistant response using a live LLM when configured, else use a deterministic fallback."""

    overview = build_portfolio_overview(session)
    top_patterns = session.query(PatternRecord).order_by(PatternRecord.regularity_score.desc()).limit(settings.assistant_top_patterns).all()
    top_predictions = session.query(PredictionRecord).order_by(PredictionRecord.recurrence_probability_90d.desc()).limit(settings.assistant_top_patterns).all()
    prompt = _build_prompt(overview, top_patterns, top_predictions, payload)

    provider = settings.llm_provider.lower()
    model = settings.llm_model
    message = ""
    if settings.llm_api_key and provider != "mock":
        try:
            message = await _call_llm(provider, model, prompt)
        except Exception:
            provider = f"{provider}-fallback"
            message = _build_fallback_response(overview, payload)
    else:
        provider = "mock"
        message = _build_fallback_response(overview, payload)

    return {
        "message": message.strip(),
        "provider": provider,
        "model": model,
        "quick_actions": QUICK_ACTIONS,
    }


def _build_prompt(overview: dict, top_patterns: list[PatternRecord], top_predictions: list[PredictionRecord], payload: AssistantRequest) -> str:
    top_facilities = "\n".join(
        f"- {item['facility_name']} ({item['city']}): {item['reactive_work_orders']} reactive WOs, {item['high_risk_patterns']} high-risk patterns, {item['open_pm_candidates']} PM candidates"
        for item in overview["top_facilities"]
    ) or "- No facility hotspots available yet"
    risky_assets = "\n".join(
        f"- {item['asset_name']} [{item['asset_id']}] at {item['location_id']}: {round(item['recurrence_probability_90d'] * 100)}% 90-day recurrence risk, health index {item['health_index']}, action {item['recommended_action']}"
        for item in overview["at_risk_assets"]
    ) or "- No at-risk assets available yet"
    recurring_patterns = "\n".join(
        f"- {pattern.pattern_key}: regularity {pattern.regularity_score}, average interval {pattern.avg_interval_days} days, priority {pattern.priority_mode}"
        for pattern in top_patterns
    ) or "- No recurring patterns available yet"
    prediction_summary = "\n".join(
        f"- {prediction.pattern_key}: 30d {round(prediction.recurrence_probability_30d * 100)}%, 60d {round(prediction.recurrence_probability_60d * 100)}%, 90d {round(prediction.recurrence_probability_90d * 100)}%"
        for prediction in top_predictions
    ) or "- No predictions available yet"
    guidance = ACTION_GUIDANCE.get(payload.action or "", "Answer as a proactive maintenance copilot. Use crisp bullets and recommended next actions.")
    return dedent(
        f"""
        You are the Reactive PM Copilot for a CBRE Smart FM portfolio. Provide polished but concrete answers with no hype, no generic AI talk, and no unsupported claims.

        Portfolio scale:
        - Facilities: {overview['facilities']}
        - Assets: {overview['assets']}
        - Technicians: {overview['technicians']}
        - Work orders: {overview['work_orders']}

        Facility hotspots:
        {top_facilities}

        At-risk assets:
        {risky_assets}

        Recurring patterns:
        {recurring_patterns}

        Prediction summary:
        {prediction_summary}

        User request:
        {payload.message or 'Provide the most useful insight for a leadership demo.'}

        Guidance:
        {guidance}
        """
    ).strip()


def _build_fallback_response(overview: dict, payload: AssistantRequest) -> str:
    action = payload.action or "welcome"
    top_facility = overview["top_facilities"][0] if overview["top_facilities"] else None
    top_asset = overview["at_risk_assets"][0] if overview["at_risk_assets"] else None
    builders = {
        "top-risk-assets": lambda: _risk_asset_response(overview),
        "pm-opportunities": lambda: _pm_opportunity_response(overview),
        "occupant-impact": lambda: _occupant_impact_response(top_facility),
        "executive-summary": lambda: _executive_summary_response(overview, top_facility, top_asset),
        "welcome": lambda: _welcome_response(overview, top_facility, top_asset),
    }
    return builders.get(action, builders["welcome"])()


async def _call_llm(provider: str, model: str, prompt: str) -> str:
    timeout = httpx.Timeout(settings.llm_timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout) as client:
        if provider == "gemini":
            url = settings.llm_base_url or f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            response = await client.post(
                url,
                params={"key": settings.llm_api_key},
                json={"contents": [{"parts": [{"text": prompt}]}]},
            )
            response.raise_for_status()
            payload = response.json()
            return payload["candidates"][0]["content"]["parts"][0]["text"]
        if provider == "mistral":
            url = settings.llm_base_url or "https://api.mistral.ai/v1/chat/completions"
            response = await client.post(
                url,
                headers={"Authorization": f"Bearer {settings.llm_api_key}"},
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are an operations copilot for predictive maintenance and FM leadership reviews."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.3,
                },
            )
            response.raise_for_status()
            payload = response.json()
            return payload["choices"][0]["message"]["content"]
        if provider == "openai":
            url = settings.llm_base_url or "https://api.openai.com/v1/chat/completions"
            response = await client.post(
                url,
                headers={"Authorization": f"Bearer {settings.llm_api_key}"},
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are an operations copilot for predictive maintenance and FM leadership reviews."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.3,
                },
            )
            response.raise_for_status()
            payload = response.json()
            return payload["choices"][0]["message"]["content"]
    raise ValueError(f"Unsupported LLM provider: {provider}")


def _risk_asset_response(overview: dict) -> str:
    if not overview["at_risk_assets"]:
        return "No scored assets are available yet. Run the analytics pipeline first, then I can rank the highest-risk equipment and recommend interventions."
    lines = ["Top risk assets in the current portfolio:"]
    for item in overview["at_risk_assets"][:4]:
        lines.append(
            f"- {item['asset_name']} at {item['location_id']} is tracking at {round(item['recurrence_probability_90d'] * 100)}% 90-day recurrence risk with health index {item['health_index']}. {item['recommended_action']}."
        )
    lines.append("Recommendation: convert the top two items into PM immediately and hold specialist capacity for the next two.")
    return "\n".join(lines)


def _pm_opportunity_response(overview: dict) -> str:
    leading_facility = overview["top_facilities"][0]["facility_name"] if overview["top_facilities"] else "The leading facility"
    pm_candidates = sum(item["open_pm_candidates"] for item in overview["top_facilities"])
    return dedent(
        f"""
        Best PM conversion opportunities right now:
        - {leading_facility} is carrying the densest concentration of high-risk reactive patterns.
        - The portfolio already has {pm_candidates} visible PM candidates across the top hotspots.
        - The fastest win is to batch recurring HVAC, plumbing, and electrical patterns into a technician-ready PM wave for the next 2 to 3 weeks.
        - Use the generated schedule list as the base plan, then lock parts and manpower against the top-risk assets first.
        """
    ).strip()


def _occupant_impact_response(top_facility: dict | None) -> str:
    facility_name = top_facility["facility_name"] if top_facility else "The top facility"
    return dedent(
        f"""
        Occupant experience exposure is highest where repeat reactive tickets cluster at high-traffic facilities.
        - {facility_name} is the main watchpoint because it combines frequent reactive demand with multiple high-risk recurring patterns.
        - Prioritize comfort-critical categories first: HVAC, lift, plumbing, and electrical faults that create visible service disruption.
        - Operational move: convert the top recurring faults into PM before the next occupant-heavy cycle and keep a rapid-response buffer for unplanned escalations.
        """
    ).strip()


def _executive_summary_response(overview: dict, top_facility: dict | None, top_asset: dict | None) -> str:
    facility_name = top_facility["facility_name"] if top_facility else "the top-ranked facility"
    asset_name = top_asset["asset_name"] if top_asset else "the top-ranked asset"
    return dedent(
        f"""
        Leadership summary:
        - The demo portfolio spans {overview['facilities']} facilities, {overview['assets']} assets, and {overview['work_orders']} reactive work orders, which is enough scale to demonstrate real operational patterns rather than isolated tickets.
        - The strongest hotspot is {facility_name}, where reactive volume and repeat-failure signatures are concentrated.
        - The most exposed asset currently is {asset_name}, which is a strong candidate for immediate PM conversion.
        - Business message: the platform is already turning historical breakdown data into prioritized PM actions, which reduces avoidable failures, protects tenant experience, and gives planners a defensible scheduling queue.
        """
    ).strip()


def _welcome_response(overview: dict, top_facility: dict | None, top_asset: dict | None) -> str:
    facility_name = top_facility["facility_name"] if top_facility else "No hotspot yet"
    asset_name = top_asset["asset_name"] if top_asset else "No asset scored yet"
    return dedent(
        f"""
        Reactive PM Copilot is live.
        - Portfolio scale: {overview['facilities']} facilities, {overview['assets']} assets, {overview['technicians']} technicians, and {overview['work_orders']} work orders.
        - Primary hotspot: {facility_name}.
        - Highest-risk asset: {asset_name}.
        - Next best move: run the top PM conversions first, then use the assistant chips for executive summary, risk prioritization, or occupant-impact framing.
        """
    ).strip()