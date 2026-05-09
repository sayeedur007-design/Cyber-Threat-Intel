import os
import re
from dotenv import load_dotenv

load_dotenv()

class RiskScorer:
    def __init__(self):
        # Default lists to avoid inefficient empty string checks
        def get_kw(key, default):
            raw = os.getenv(key, default).lower().split(",")
            return [k.strip() for k in raw if k.strip()]

        self.kw_critical = get_kw("RISK_KEYWORDS_CRITICAL", "critical,remote code execution,rce,unauthenticated")
        self.kw_high     = get_kw("RISK_KEYWORDS_HIGH", "high severity,privilege escalation,injection")
        self.kw_medium   = get_kw("RISK_KEYWORDS_MEDIUM", "medium,denial of service,dos")
        
        try:
            self.weight_cvss = float(os.getenv("RISK_WEIGHT_CVSS", 5.0))
            self.weight_crit = float(os.getenv("RISK_WEIGHT_CRITICAL", 35))
            self.weight_high = float(os.getenv("RISK_WEIGHT_HIGH", 20))
            self.weight_med  = float(os.getenv("RISK_WEIGHT_MEDIUM", 10))
        except ValueError:
            self.weight_cvss, self.weight_crit, self.weight_high, self.weight_med = 5.0, 35, 20, 10

    def calculate(self, text: str, base_cvss: float = 0.0) -> float:
        """Calculate a risk score from 0-100."""
        text_lower = text.lower()
        score = base_cvss * self.weight_cvss
        
        # Keyword checks (Critical → High → Medium hierarchy)
        if any(kw in text_lower for kw in self.kw_critical):
            score += self.weight_crit
        elif any(kw in text_lower for kw in self.kw_high):
            score += self.weight_high
        elif any(kw in text_lower for kw in self.kw_medium):
            score += self.weight_med
            
        return min(max(score, 0), 100)

    def get_label(self, score: float) -> str:
        if score >= 90: return "CRITICAL"
        if score >= 70: return "HIGH"
        if score >= 40: return "MEDIUM"
        return "LOW"

    def get_color(self, score: float) -> str:
        if score >= 90: return "#ff4757"
        if score >= 70: return "#ffa502"
        if score >= 40: return "#ffd32a"
        return "var(--accent-primary)"
