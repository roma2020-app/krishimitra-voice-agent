import logging
from typing import Callable, Optional

from livekit.agents import Agent, RunContext, function_tool

from memory.database import get_farmer
from tools.escalation_tool import create_escalation

logger = logging.getLogger("crop-specialist")


class CropProblemSpecialist(Agent):
    """Day 9 specialist focused on crop problems, with the existing Human Help path."""

    def __init__(
        self,
        user_id: str,
        chat_ctx=None,
        mark_call_success: Optional[Callable[[str], None]] = None,
    ):
        self.user_id = user_id
        self._mark_call_success = mark_call_success

        super().__init__(
            instructions="""
You are Krishi Mitra's Crop Problem Specialist.

ROLE
Your only job is to help Indian farmers understand and troubleshoot crop problems.
Focus on symptoms such as yellowing leaves, leaf spots, pests, visible damage,
possible nutrient problems, irrigation issues, and possible crop disease.

LIMITS
- Do not claim a definite disease diagnosis from a voice description alone.
- Do not prescribe pesticide dosages or chemical treatment rates.
- Ask short, practical questions when more information is needed.
- Suggest safe observation and basic next steps.
- Recommend contacting a qualified agriculture officer, Krishi Vigyan Kendra,
  or agriculture expert when the problem is serious or uncertain.
- Never ask for OTPs, PINs, passwords, bank details, card numbers, or other sensitive information.

CONVERSATION
The farmer has already spoken with the main Krishi Mitra agent. Continue from the
existing conversation and do not ask the farmer to repeat information that is already
available in the conversation.

HUMAN HELP ESCALATION
You have access to the SAME existing Krishi Mitra human-help escalation system.
If the farmer wants a human agriculture expert, you may create a request using
create_human_help, but ONLY after explicit permission.

Appropriate situations include:
- serious crop disease or severe crop damage
- a crop problem requiring expert diagnosis
- the farmer explicitly asks to speak to or get help from a human agriculture expert

Before creating the request, ask only one short permission question:

"क्या मैं आपकी समस्या, फसल और जिले की जानकारी कृषि विशेषज्ञ के साथ साझा करके मदद का अनुरोध बनाऊँ?"

WAIT for the farmer's answer. Do not call the tool before clear permission.

Treat these as clear permission: yes, yes please, okay, ok, go ahead, हाँ, हां, जी हाँ,
जी हां, अनुमति है, कर दीजिए, भेज दीजिए, बना दीजिए.

If the farmer says no or refuses, do not create a request and respect the decision.
If the answer is genuinely unclear, ask one short clarification and do not repeatedly ask.

Only share information needed by the agriculture expert:
famer name, farmer/user ID, district, crop, what happened, what the agent checked,
urgency, language, and preferred follow-up method.
Never include OTP, PIN, password, bank account number, card number, or unnecessary private data.

After the tool succeeds, tell the farmer the EXACT reference ID returned by the tool.
Do not invent or guess a reference ID. Do not promise an immediate response.

LANGUAGE
Reply in the same language as the farmer. For Hindi or Hinglish, write Hindi words
in Devanagari script. Use feminine Hindi grammar.

STYLE
Be warm, concise, practical, and calm. Keep replies to 2-3 short sentences unless
a clarification question is needed.
""",
            chat_ctx=chat_ctx,
        )

    def _mark_success(self, reason: str) -> None:
        if self._mark_call_success is not None:
            self._mark_call_success(reason)

    @function_tool
    async def create_human_help(
        self,
        context: RunContext,
        reason: str,
        what_happened: str,
        urgency: str,
        preferred_follow_up: str,
    ) -> str:
        """Create the existing human-help escalation after explicit farmer permission."""

        farmer = get_farmer(self.user_id)

        if farmer is None:
            logger.warning(
                "Crop specialist could not find farmer profile: user_id=%s",
                self.user_id,
            )
            return (
                "I could not create the human-help request because the farmer profile "
                "is unavailable. Please ask the farmer to provide their profile details "
                "through the main Krishi Mitra flow."
            )

        farmer_name = farmer.get("name", "")
        district = farmer.get("district", "")
        crop = farmer.get("crops_grown", "")
        language = farmer.get("language_preference", "")

        result = create_escalation(
            user_id=self.user_id,
            farmer_name=farmer_name,
            district=district,
            crop=crop,
            reason=reason,
            what_happened=what_happened,
            agent_checked=(
                "Krishi Mitra Crop Problem Specialist reviewed the reported crop symptoms "
                "and provided safe troubleshooting guidance without a definitive diagnosis."
            ),
            urgency=urgency,
            language=language,
            preferred_follow_up=preferred_follow_up,
        )

        if not result.get("success"):
            logger.error(
                "Crop specialist human-help escalation failed: user_id=%s result=%s",
                self.user_id,
                result,
            )
            return "I could not create the human-help request right now. Please try again."

        reference_id = result["reference_id"]

        logger.info(
            "Human-help request created by crop specialist: user_id=%s reference=%s",
            self.user_id,
            reference_id,
        )

        self._mark_success("Human-help request successfully created by Crop Problem Specialist")

        return (
            f"SUCCESS. Human-help request has been created. "
            f"Reference ID is {reference_id}. Status is OPEN. "
            "A human agriculture expert will review it."
        )

    async def on_enter(self) -> None:
        await self.session.generate_reply(
            instructions=(
                "Introduce yourself briefly as Krishi Mitra's Crop Problem Specialist "
                "and continue from the farmer's existing crop problem. Do not ask the "
                "farmer to repeat the problem. Ask one useful short question if needed."
            )
        )
