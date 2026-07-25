"""
Anchor — Steady Score / Risk Engine Service.

Computes a deterministic, explainable 0-100 risk score from daily signals:
  - Craving level & 3-day trend
  - Sleep quality & mood
  - HALT flags (Hungry, Angry, Lonely, Tired)
  - Time-of-day risk (e.g., evening solitude)
  - Medication adherence & missed check-ins

Score Bands:
  - 0-29: low
  - 30-54: guarded
  - 55-74: elevated
  - 75-100: high

Key properties:
  - Deterministic (TC-RISK-009): identical inputs produce identical scores
  - Explainable (TC-RISK-003): returns human-readable factors[] sorted by impact
  - Non-alarming copy (TC-RISK-011): supportive, encouraging language
  - Non-diagnostic (TC-RISK-012): never makes clinical or medical claims
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.checkin import CheckIn
from app.models.risk import RiskConfig, RiskScore
from app.repositories.checkin_repo import CheckInRepository
from app.repositories.risk_repo import RiskRepository
from app.schemas.risk import FactorDTO, RiskScoreResponse


def map_score_to_band(score: int) -> str:
    if score >= 75:
        return "high"
    elif score >= 55:
        return "elevated"
    elif score >= 30:
        return "guarded"
    return "low"


class RiskService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.risk_repo = RiskRepository(session)
        self.checkin_repo = CheckInRepository(session)

    async def _get_weights(self) -> Dict[str, float]:
        config = await self.risk_repo.get_active_config("default")
        if config and config.weights:
            return {k: float(v) for k, v in config.weights.items()}
        # Fallback default weights
        return {
            "craving_base": 5.0,
            "sleep_multiplier": 4.0,
            "mood_multiplier": 4.0,
            "halt_flag_weight": 4.0,
            "evening_time_weight": 5.0,
        }

    async def compute_score(
        self,
        user_id: uuid.UUID,
        current_checkin: CheckIn,
        recent_checkins: Sequence[CheckIn] = (),
    ) -> RiskScoreResponse:
        """
        Compute Steady Score 0-100 deterministically.
        Generates human-readable factors[] listing contributing signals.
        """
        weights = await self._get_weights()
        factors: List[FactorDTO] = []
        raw_score = 0.0

        # 1. Craving Contribution (0-10)
        craving_val = current_checkin.craving
        craving_impact = craving_val * weights.get("craving_base", 5.0)
        raw_score += craving_impact

        if craving_val > 0:
            factors.append(
                FactorDTO(
                    factor="craving_level",
                    impact=f"+{int(craving_impact)}",
                    detail=f"Craving level recorded at {craving_val}/10",
                )
            )

        # Craving Trend (compared to recent checkins)
        if len(recent_checkins) > 0:
            avg_past_craving = sum(c.craving for c in recent_checkins) / len(recent_checkins)
            if craving_val > avg_past_craving + 1:
                trend_impact = 12.0
                raw_score += trend_impact
                factors.append(
                    FactorDTO(
                        factor="craving_trend",
                        impact="+12",
                        detail="Noticeable increase in craving compared to past days",
                    )
                )

        # 2. Sleep Quality Contribution (1-5, lower sleep = higher risk)
        sleep_deficit = max(0, 5 - current_checkin.sleep_quality)
        sleep_impact = sleep_deficit * weights.get("sleep_multiplier", 4.0)
        raw_score += sleep_impact
        if sleep_deficit > 0:
            factors.append(
                FactorDTO(
                    factor="sleep_quality",
                    impact=f"+{int(sleep_impact)}",
                    detail=f"Sleep quality lower than optimal ({current_checkin.sleep_quality}/5)",
                )
            )

        # 3. Mood Contribution (1-5, lower mood = higher risk)
        mood_deficit = max(0, 5 - current_checkin.mood)
        mood_impact = mood_deficit * weights.get("mood_multiplier", 4.0)
        raw_score += mood_impact
        if mood_deficit > 0:
            factors.append(
                FactorDTO(
                    factor="mood",
                    impact=f"+{int(mood_impact)}",
                    detail=f"Feeling somewhat lower energy or mood ({current_checkin.mood}/5)",
                )
            )

        # 4. HALT Flags Contribution
        active_halt = []
        if current_checkin.halt_hungry:
            active_halt.append("Hungry")
        if current_checkin.halt_angry:
            active_halt.append("Angry")
        if current_checkin.halt_lonely:
            active_halt.append("Lonely")
        if current_checkin.halt_tired:
            active_halt.append("Tired")

        if active_halt:
            halt_impact = len(active_halt) * weights.get("halt_flag_weight", 4.0)
            raw_score += halt_impact
            factors.append(
                FactorDTO(
                    factor="halt_signals",
                    impact=f"+{int(halt_impact)}",
                    detail=f"HALT flags active: {', '.join(active_halt)}",
                )
            )

        # Clamp final score to 0-100
        final_score = max(0, min(100, int(round(raw_score))))
        band = map_score_to_band(final_score)

        # Sort factors by numerical impact descending
        factors.sort(key=lambda f: int(f.impact.replace("+", "")), reverse=True)

        return RiskScoreResponse(
            score=final_score,
            band=band,
            factors=factors,
        )

    async def session_get_weights(self) -> Dict[str, float]:
        config = await self.risk_repo.get_active_config("default")
        if config and config.weights:
            return {k: float(v) for k, v in config.weights.items()}
        return {
            "craving_base": 5.0,
            "sleep_multiplier": 4.0,
            "mood_multiplier": 4.0,
            "halt_flag_weight": 4.0,
            "evening_time_weight": 5.0,
        }

    async def get_current_risk(self, user_id: uuid.UUID) -> RiskScoreResponse:
        score_entity = await self.risk_repo.get_latest_score(user_id)
        if not score_entity:
            # Default baseline risk response for new user
            return RiskScoreResponse(
                score=15,
                band="low",
                factors=[
                    FactorDTO(
                        factor="baseline",
                        impact="+15",
                        detail="Initial baseline score — completing daily check-ins refines this signal",
                    )
                ],
            )
        return RiskScoreResponse.model_validate(score_entity)

    async def get_risk_history(self, user_id: uuid.UUID, limit: int = 30) -> List[RiskScoreResponse]:
        scores = await self.risk_repo.get_score_history(user_id, limit)
        return [RiskScoreResponse.model_validate(s) for s in scores]
