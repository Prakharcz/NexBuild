import logging
from typing import Dict, List, Optional
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMAdvisor:
    """
    Financial intelligence advisor with local Ollama integration and
    automatic template-based fallback.
    """

    def __init__(self, base_url: str = settings.OLLAMA_BASE_URL, model: str = settings.OLLAMA_MODEL):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def query_ollama(self, prompt: str, timeout: float = 2.0) -> Optional[str]:
        """
        Attempt to query the local Ollama LLM endpoint.
        Returns the generated text response, or None if Ollama is offline or times out.
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": f"You are an expert personal financial risk advisor. Provide a concise, actionable 2-sentence piece of financial advice for this situation:\n\n{prompt}",
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 100
            }
        }
        try:
            with httpx.Client(timeout=timeout) as client:
                resp = client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    response_text = data.get("response", "").strip()
                    if response_text:
                        return response_text
        except Exception as e:
            logger.debug(f"Ollama local LLM unavailable ({e}). Using intelligent template fallback.")
        return None

    def explain_recurring_price_hike(
        self,
        merchant: str,
        old_amount: float,
        new_amount: float,
        pct_increase: float
    ) -> str:
        """
        Generate explanation for a subscription or recurring bill price hike.
        """
        diff = abs(new_amount) - abs(old_amount)
        annual_impact = diff * 12.0
        prompt = (
            f"The user's recurring subscription for {merchant} increased by {pct_increase:.1f}% "
            f"(from ${abs(old_amount):.2f} to ${abs(new_amount):.2f}), costing an extra ${annual_impact:.2f}/year."
        )

        llm_reply = self.query_ollama(prompt)
        if llm_reply:
            return f"[AI Advisor] {llm_reply}"

        # Intelligent template fallback
        return (
            f"{merchant} has increased its charge by {pct_increase:.1f}% (from ${abs(old_amount):.2f} to "
            f"${abs(new_amount):.2f}). This silent escalation adds ${annual_impact:.2f} to your annual expenses. "
            f"Review your usage to decide if downgrading or switching to an alternative plan makes sense."
        )

    def explain_liquidity_alert(self, runway_months: float, monthly_burn: float) -> str:
        """
        Generate explanation for low emergency cash liquidity runway.
        """
        prompt = f"The user currently has {runway_months:.1f} months of liquidity buffer based on a monthly spend of ${monthly_burn:.2f}."
        llm_reply = self.query_ollama(prompt)
        if llm_reply:
            return f"[AI Advisor] {llm_reply}"

        return (
            f"Your current cash reserves cover approximately {runway_months:.1f} months of baseline living expenses "
            f"(${monthly_burn:.2f}/month). Financial resilience models recommend a minimum 3 to 6-month buffer "
            f"to withstand emergency income disruptions without incurring high-interest debt."
        )

    def explain_high_category_spend(self, category: str, total_amount: float, pct_of_budget: float) -> str:
        """
        Generate explanation for high expenditure concentration in a category.
        """
        prompt = f"The user spent ${total_amount:.2f} in '{category}', representing {pct_of_budget:.1f}% of total outflow."
        llm_reply = self.query_ollama(prompt)
        if llm_reply:
            return f"[AI Advisor] {llm_reply}"

        return (
            f"Expenditures in '{category}' represent {pct_of_budget:.1f}% (${total_amount:.2f}) of your total monthly outflow. "
            f"Trimming non-essential discretionary expenses here by just 10-15% can generate significant surplus to accelerate your savings goals."
        )

    def explain_anomaly_spike(self, description: str, amount: float, reason: str) -> str:
        """
        Generate explanation for an unusual transaction anomaly.
        """
        prompt = f"A single transaction '{description}' for ${abs(amount):.2f} was flagged as an outlier: {reason}."
        llm_reply = self.query_ollama(prompt)
        if llm_reply:
            return f"[AI Advisor] {llm_reply}"

        return (
            f"The transaction '{description}' for ${abs(amount):.2f} was detected as a statistical outlier ({reason}). "
            f"Ensure this charge is legitimate, and consider categorizing one-off emergency costs separately so they do not distort your recurring cash flow projection."
        )


llm_advisor = LLMAdvisor()
