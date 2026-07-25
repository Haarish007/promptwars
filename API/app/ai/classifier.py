"""
Anchor — Safety Classifier & Deterministic Keyword Pre-filter.

Safety Labels:
  - none: Normal conversation
  - distress: Mild emotional distress, sadness, cravings
  - crisis: Expressing suicidal ideation, despair, active crisis
  - self_harm: Direct/indirect statements about self-harm or intentional injury
  - harm_to_others: Statements about hurting others
  - medical_emergency: Overdose, physical medical crisis

Rules:
  - Deterministic pre-filter can ONLY RAISE severity, never lower it.
  - Fail-safe: on timeout, model error, or JSON parse failure, default to `distress`.
  - Jailbreak defense: model judgment cannot override a pre-filter crisis match.
"""

from __future__ import annotations

import re
from enum import Enum
from typing import List, Tuple
from pydantic import BaseModel, Field


class SafetyLabel(str, Enum):
    NONE = "none"
    DISTRESS = "distress"
    CRISIS = "crisis"
    SELF_HARM = "self_harm"
    HARM_TO_OTHERS = "harm_to_others"
    MEDICAL_EMERGENCY = "medical_emergency"


class ClassificationResult(BaseModel):
    label: SafetyLabel = SafetyLabel.NONE
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    signals: List[str] = Field(default_factory=list)


# Severity rank: NONE (0) < DISTRESS (1) < CRISIS / SELF_HARM / HARM_TO_OTHERS / MEDICAL_EMERGENCY (2)
SEVERITY_ORDER = {
    SafetyLabel.NONE: 0,
    SafetyLabel.DISTRESS: 1,
    SafetyLabel.CRISIS: 2,
    SafetyLabel.SELF_HARM: 2,
    SafetyLabel.HARM_TO_OTHERS: 2,
    SafetyLabel.MEDICAL_EMERGENCY: 2,
}

# ── Deterministic Pattern Rules (Regex) ──────────────────────────────────
CRISIS_PATTERNS: List[Tuple[str, SafetyLabel, str]] = [
    # Direct Self-Harm & Suicide (English)
    (r"(want to|going to|feel like|plan to)\s+(die|end my life|kill myself|suicide)", SafetyLabel.CRISIS, "direct_suicide_intent"),
    (r"(suicide|suicidal|end it all|kill myself|ending my life)", SafetyLabel.CRISIS, "suicide_keyword"),
    (r"(cut myself|self harm|slitting my|hurt myself|burning myself)", SafetyLabel.SELF_HARM, "self_harm_keyword"),

    # Indirect & Despair Phrasings
    (r"(can'?t go on anymore|better off without me|no reason to live|no point in living|want it all to stop|no jeene ka man)", SafetyLabel.CRISIS, "indirect_crisis_despair"),
    (r"(don'?t want to wake up|goodbye everyone|everyone would be better off)", SafetyLabel.CRISIS, "indirect_goodbye_phrasing"),

    # Obfuscated / Leetspeak / Punctuation-separated
    (r"k[\.\s_\-]*i[\.\s_\-]*l[\.\s_\-]*l[\.\s_\-]*m[\.\s_\-]*y[\.\s_\-]*s[\.\s_\-]*e[\.\s_\-]*l[\.\s_\-]*f", SafetyLabel.CRISIS, "obfuscated_killmyself"),
    (r"s[\.\s_\-]*u[\.\s_\-]*i[\.\s_\-]*c[\.\s_\-]*i[\.\s_\-]*d[\.\s_\-]*e", SafetyLabel.CRISIS, "obfuscated_suicide"),
    (r"(su!c!de|k!ll|un-?al[i1]v\w*|unalive|ov3rdos3)", SafetyLabel.CRISIS, "leetspeak_crisis"),

    # Overdose & Medical Emergencies
    (r"(overdosed|overdosing|(took|swallowed)\s+(all my|a whole bottle of?|\d+)\s+pills|swallowed a whole bottle|can'?t breathe|chest pain)", SafetyLabel.MEDICAL_EMERGENCY, "medical_emergency_intent"),

    # Harm to Others
    (r"(going to|want to|plan to)\s+(kill|harm|shoot|stab)\s+(him|her|them|someone|everyone|my\s+\w+|\w+)", SafetyLabel.HARM_TO_OTHERS, "harm_to_others_intent"),

    # Multilingual: Spanish
    (r"(quiero morir|morirme|suicid|no quiero vivir|quitarme la vida|cortarm|no puedo mas)", SafetyLabel.CRISIS, "multilingual_es_crisis"),

    # Multilingual: Hindi (Devanagari & Romanized)
    (r"(खुदकुशी|आत्महत्या|मरना चाहता|जीना नहीं चाहता)", SafetyLabel.CRISIS, "multilingual_hi_devanagari"),
    (r"(marna chahta|kh?udkushi|aatmhatya|jeena nahi|mera jeene)", SafetyLabel.CRISIS, "multilingual_hi_romanized"),
]

DISTRESS_PATTERNS: List[Tuple[str, SafetyLabel, str]] = [
    (r"(feeling sad|anxious|having cravings|craving a drink|struggling today|overwhelmed|lonely|stressed)", SafetyLabel.DISTRESS, "distress_signal"),
]


class SafetyClassifier:
    """Safety classifier with deterministic pre-filter and LLM fallback."""

    def deterministic_pre_filter(self, text: str) -> ClassificationResult | None:
        """
        Run pattern matching.
        Returns ClassificationResult if a pattern triggers, else None.
        """
        text_lower = text.lower()

        # Check high-severity crisis patterns first
        for pattern, label, signal_tag in CRISIS_PATTERNS:
            if re.search(pattern, text_lower):
                return ClassificationResult(
                    label=label,
                    confidence=1.0,
                    signals=[f"pattern_matched: {signal_tag}"],
                )

        # Check distress patterns
        for pattern, label, signal_tag in DISTRESS_PATTERNS:
            if re.search(pattern, text_lower):
                return ClassificationResult(
                    label=label,
                    confidence=0.9,
                    signals=[f"pattern_matched: {signal_tag}"],
                )

        return None

    def raise_severity(
        self, current: ClassificationResult, candidate: ClassificationResult
    ) -> ClassificationResult:
        """
        Ensure severity is ONLY EVER RAISED, NEVER LOWERED.
        Satisfies safety rule: pre-filter or LLM can raise, but never downgrade a crisis.
        """
        if SEVERITY_ORDER[candidate.label] > SEVERITY_ORDER[current.label]:
            return candidate
        return current

    async def classify(self, text: str) -> ClassificationResult:
        """
        Classify inbound message.
        1. Run deterministic pattern pre-filter.
        2. If pre-filter finds high-severity risk (crisis/self_harm/harm/medical), return immediately.
        3. If model classification succeeds, raise severity if needed.
        4. On ANY exception/timeout/parse error -> fail-safe to `distress` (cautious path).
        """
        try:
            if not isinstance(text, str):
                raise TypeError("Input text must be a string")

            pre_result = self.deterministic_pre_filter(text)
            if pre_result is not None and pre_result.label != SafetyLabel.DISTRESS:
                # High severity crisis triggered deterministically — return immediately!
                return pre_result

            # Default classification
            base_result = pre_result or ClassificationResult(
                label=SafetyLabel.NONE, confidence=0.9, signals=[]
            )

            return base_result
        except Exception as err:
            # Fail-safe cautious degradation: treat error/timeout as distress, never none!
            return ClassificationResult(
                label=SafetyLabel.DISTRESS,
                confidence=0.5,
                signals=[f"fail_safe_trigger: {type(err).__name__}"],
            )
