"""
Anchor — Database Seed Script.

Populates initial data for development and demo:
1. Member **Maya** (email: maya@example.com, role: member)
2. Guardian **David** (email: david@example.com, role: guardian)
3. MemberProfile & EmergencyContact for Maya (with encrypted phone)
4. Curated KB articles + passages (SUD recovery, urge surfing, HALT principles, supportive communication)
5. Default `risk_config` parameters
"""

from __future__ import annotations

import asyncio
from datetime import date, datetime, timezone

from app.core.crypto import encrypt_field
from app.core.security import hash_password
from app.db.session import async_session_factory
from app.models.caregiver import CaregiverLink
from app.models.consent import Consent
from app.models.kb import KBArticle, KBChunk
from app.models.profile import EmergencyContact, MemberProfile, Trigger
from app.models.risk import RiskConfig
from app.models.user import User


async def seed() -> None:
    async with async_session_factory() as session:
        print("[SEED] Seeding database...")

        # ── 1. Create Users (Maya & David) ─────────────────────────
        maya_pwd = hash_password("Password123!")
        maya = User(
            email="maya@example.com",
            password_hash=maya_pwd,
            role="member",
            status="active",
        )
        david_pwd = hash_password("Password123!")
        david = User(
            email="david@example.com",
            password_hash=david_pwd,
            role="guardian",
            status="active",
        )
        session.add_all([maya, david])
        await session.flush()
        print(f"  [OK] Users created: Maya ({maya.id}) & David ({david.id})")

        # ── 2. Maya Profile & Emergency Contact ────────────────────
        maya_profile = MemberProfile(
            user_id=maya.id,
            recovery_goal="Maintain alcohol abstinence & manage stress triggers",
            substance_focus="Alcohol Use Disorder",
            recovery_start_date=date(2025, 11, 1),
            voice_first=True,
            nudge_frequency="medium",
            quiet_hours_start="22:00",
            quiet_hours_end="07:00",
            region="US",
        )

        contact = EmergencyContact(
            user_id=maya.id,
            name="David (Father)",
            relationship="Guardian / Family",
            phone_ciphertext=encrypt_field("+15550192834") or "",
            is_sponsor=False,
            priority=1,
        )

        trigger1 = Trigger(
            user_id=maya.id,
            label="Evening solitude after work",
            type="temporal",
            time_of_day="19:00",
        )
        trigger2 = Trigger(
            user_id=maya.id,
            label="Work stress / tight deadlines",
            type="emotional",
        )
        session.add_all([maya_profile, contact, trigger1, trigger2])

        # ── 3. Consents ────────────────────────────────────────────
        consent1 = Consent(user_id=maya.id, scope="data_processing", version="1.0")
        consent2 = Consent(user_id=maya.id, scope="share_with_guardian", version="1.0")
        consent3 = Consent(user_id=maya.id, scope="voice_processing", version="1.0")
        session.add_all([consent1, consent2, consent3])

        # ── 4. Caregiver Link ─────────────────────────────────────
        link = CaregiverLink(
            member_id=maya.id,
            guardian_id=david.id,
            status="active",
            accepted_at=datetime.now(timezone.utc),
        )
        session.add(link)

        # ── 5. Default Risk Config ─────────────────────────────────
        risk_config = RiskConfig(
            key="default",
            version="1.0",
            active=True,
            weights={
                "craving_base": 1.0,
                "sleep_multiplier": 1.2,
                "halt_flag_weight": 5.0,
                "missed_checkin_weight": 8.0,
                "evening_time_weight": 4.0,
                "med_nonadherence_weight": 10.0,
            },
        )
        session.add(risk_config)

        # ── 6. Curated KB Articles & Chunks ───────────────────────
        kb1 = KBArticle(
            title="Understanding Cravings and Urge Surfing",
            body=(
                "Cravings are temporary emotional and physiological responses that typically peak within "
                "10 to 20 minutes before naturally subsiding. Urge surfing is a mindfulness technique where "
                "you picture the craving as an ocean wave and ride it rather than fighting or giving in."
            ),
            source_name="SMART Recovery Clinical Guidance",
            source_url="https://smartrecovery.org",
            review_date=date(2025, 1, 15),
            tags=["cravings", "urge_surfing", "mindfulness"],
        )
        session.add(kb1)
        await session.flush()

        chunk1 = KBChunk(
            article_id=kb1.id,
            chunk_text=(
                "[kb-101] Cravings peak within 10 to 20 minutes and gradually diminish. Urge surfing involves "
                "focused breathing and treating the craving as a wave to ride without acting on it."
            ),
            ord=1,
        )

        kb2 = KBArticle(
            title="The HALT Framework for Relapse Prevention",
            body=(
                "HALT stands for Hungry, Angry, Lonely, Tired. These four physiological and emotional states "
                "significantly lower cognitive capacity and increase vulnerability to cravings."
            ),
            source_name="NIDA Recovery Guidelines",
            source_url="https://nida.nih.gov",
            review_date=date(2025, 2, 1),
            tags=["HALT", "prevention", "triggers"],
        )
        session.add(kb2)
        await session.flush()

        chunk2 = KBChunk(
            article_id=kb2.id,
            chunk_text=(
                "[kb-102] The HALT framework identifies Hungry, Angry, Lonely, and Tired states as primary "
                "vulnerability factors. Addressing these basic physiological needs promptly reduces craving intensity."
            ),
            ord=1,
        )

        kb3 = KBArticle(
            title="Supportive Communication for Caregivers",
            body=(
                "Caregivers support loved ones best by offering calm, non-judgmental presence without lecturing, "
                "interrogating, or expressing panic. Validate their effort while affirming safety."
            ),
            source_name="CRAFT Caregiver Protocol",
            source_url="https://craft-recovery.org",
            review_date=date(2025, 3, 10),
            tags=["caregiver", "support", "communication"],
        )
        session.add(kb3)
        await session.flush()

        chunk3 = KBChunk(
            article_id=kb3.id,
            chunk_text=(
                "[kb-103] Effective caregiver communication focuses on concise, calm validation (e.g. 'I'm glad "
                "you reached out, I am proud of you') while avoiding intrusive questioning about triggers or relapse details."
            ),
            ord=1,
        )

        session.add_all([chunk1, chunk2, chunk3])

        await session.commit()
        print("[OK] Database seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed())
