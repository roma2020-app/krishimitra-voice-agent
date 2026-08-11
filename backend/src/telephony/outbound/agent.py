
"""Krishi Mitra outbound telephony agent."""

import asyncio
import json
import logging
import os
import sys

from dotenv import load_dotenv
from livekit import api, rtc

from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    RunContext,
    cli,
    function_tool,
    room_io,
    tokenize,
)

from livekit.plugins import (
    deepgram,
    google,
    murf,
    noise_cancellation,
    silero,
)

from livekit.plugins.turn_detector.multilingual import MultilingualModel


# ============================================================
# PATH SETUP
# ============================================================

# This allows:
# uv run python src/telephony/outbound/agent.py dev
#
# to import:
# src.tools.weather_tool

BACKEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../..")
)

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


# ============================================================
# WEATHER TOOL
# ============================================================

try:
    from src.tools.weather_tool import get_weather

    WEATHER_TOOL_AVAILABLE = True

except ImportError as e:
    WEATHER_TOOL_AVAILABLE = False
    get_weather = None

    print(
        f"WARNING: Weather tool could not be imported: {e}"
    )


# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger("krishi-outbound-agent")


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv(".env.local")


# ============================================================
# LIVEKIT OUTBOUND SIP TRUNK
# ============================================================

OUTBOUND_TRUNK_ID = os.getenv(
    "LIVEKIT_SIP_OUTBOUND_TRUNK_ID"
)

logger.info(
    "Outbound SIP trunk configured: %s",
    bool(OUTBOUND_TRUNK_ID),
)


# ============================================================
# KRISHI MITRA SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are Krishi Mitra, an intelligent voice assistant for Indian farmers.

This is an OUTBOUND phone call.

You are calling the farmer proactively to provide an important
weather alert or farming-related update.

IMPORTANT OUTBOUND CALL RULES:

1. Immediately identify yourself.
2. Explain why you are calling.
3. Be brief and respectful because the farmer did not initiate the call.
4. Give the farmer a clear way to stop the call.
5. Keep responses short and conversational.
6. Do not use markdown, lists, emojis, or technical language.
7. Keep each response under 3 short sentences.
8. Never invent current weather information.
9. If current weather information is unavailable, clearly say so.
10. Never ask for OTP, PIN, password, bank details, or other sensitive information.

LANGUAGE RULES:

If the farmer speaks Hindi, reply in Hindi using Devanagari script.

If the farmer speaks English, reply completely in English.

If the farmer speaks Hinglish, naturally mix Hindi and English,
but write Hindi words using Devanagari script.

Use feminine Hindi grammar.

For example:

"मैं आपकी मदद कर सकती हूँ।"

Never use Roman Hindi.

WEATHER:

If the farmer asks about current weather, today's weather,
temperature, rain, rainfall, humidity, wind, or tomorrow's weather,
use the weather tool.

Never invent live weather information.

If the weather tool fails, clearly tell the farmer that
live weather information is temporarily unavailable.

OUTBOUND PURPOSE:

The purpose of this demonstration is to provide a weather alert
to the farmer.

After explaining the alert, allow the farmer to ask questions.

If the farmer says they do not want the call, politely end the call.

If the farmer asks to end the call, use the end_call tool.

If you reach voicemail or an answering machine, use the
detected_answering_machine tool.
"""


# ============================================================
# OUTBOUND GREETING
# ============================================================

GREETING = (
    "नमस्ते! मैं Krishi Mitra हूँ। "
    "मैं आपके खेत के मौसम की महत्वपूर्ण जानकारी देने के लिए "
    "कॉल कर रही हूँ। अगर आप यह कॉल नहीं चाहते हैं, तो कह सकते हैं "
    "'कॉल बंद करें'।"

    #“नमस्ते! मैं Krishi Mitra हूँ। मैं आपको बारिश की महत्वपूर्ण चेतावनी देने के लिए कॉल कर रही हूँ। आपके क्षेत्र में बारिश की संभावना अधिक है, इसलिए कृपया खेत में जरूरी तैयारी कर लें। अगर आप यह कॉल नहीं चाहते हैं, तो कह सकते हैं ‘कॉल बंद करें’।”
)


CALLEE_IDENTITY = "phone-user"


# ============================================================
# OUTBOUND AGENT
# ============================================================

class OutboundAgent(Agent):

    def __init__(self, ctx: JobContext) -> None:

        super().__init__(
            instructions=SYSTEM_PROMPT
        )

        self.ctx = ctx

    # ========================================================
    # WEATHER TOOL
    # ========================================================

    @function_tool
    async def weather(
        self,
        context: RunContext,
        city: str,
    ) -> str:
        """
        Get current real-time weather for a city or district.
        """

        if not WEATHER_TOOL_AVAILABLE or get_weather is None:

            logger.warning(
                "Weather tool is not available."
            )

            return json.dumps(
                {
                    "success": False,
                    "message": (
                        "Live weather information is "
                        "temporarily unavailable."
                    ),
                },
                ensure_ascii=False,
            )

        logger.info(
            "Weather tool requested for city: %s",
            city,
        )

        try:

            # get_weather uses requests, so run it in a
            # background thread instead of blocking the
            # async voice pipeline.

            result = await asyncio.to_thread(
                get_weather,
                city,
            )

            logger.info(
                "Weather result: %s",
                result,
            )

            return json.dumps(
                result,
                ensure_ascii=False,
            )

        except Exception as e:

            logger.exception(
                "Weather tool failed: %s",
                e,
            )

            return json.dumps(
                {
                    "success": False,
                    "message": (
                        "Live weather information is "
                        "temporarily unavailable."
                    ),
                },
                ensure_ascii=False,
            )

    # ========================================================
    # END CALL TOOL
    # ========================================================

    @function_tool
    async def end_call(
        self,
        context: RunContext,
    ) -> str:
        """End the outbound phone call."""

        logger.info(
            "End call requested by farmer."
        )

        try:

            await context.session.generate_reply(
                instructions=(
                    "Say a very short polite goodbye to the farmer. "
                    "Do not ask another question."
                )
            )

            # Give Murf enough time to finish the goodbye
            # before deleting the LiveKit room.

            await asyncio.sleep(2.0)

        except Exception as e:

            logger.warning(
                "Could not generate goodbye: %s",
                e,
            )

        logger.info(
            "Ending Krishi Mitra outbound call"
        )

        await self._hangup()

        return "Call ended."

    # ========================================================
    # ANSWERING MACHINE TOOL
    # ========================================================

    @function_tool
    async def detected_answering_machine(
        self,
        context: RunContext,
    ) -> str:
        """End the call if voicemail or an answering machine answers."""

        logger.info(
            "Answering machine detected. Ending call."
        )

        await self._hangup()

        return "Call ended."

    # ========================================================
    # HANGUP
    # ========================================================

    async def _hangup(self) -> None:
        """Delete the LiveKit room and end the phone call."""

        try:

            await self.ctx.api.room.delete_room(
                api.DeleteRoomRequest(
                    room=self.ctx.room.name
                )
            )

        except Exception as e:

            logger.warning(
                "Error while ending LiveKit room: %s",
                e,
            )


# ============================================================
# LIVEKIT SERVER
# ============================================================

server = AgentServer()


# ============================================================
# PREWARM
# ============================================================

def prewarm(proc: JobProcess):

    logger.info(
        "Loading Silero VAD..."
    )

    proc.userdata["vad"] = silero.VAD.load()

    logger.info(
        "Silero VAD loaded."
    )


server.setup_fnc = prewarm


# ============================================================
# GET PHONE NUMBER FROM DISPATCH METADATA
# ============================================================

def phone_number_from_metadata(
    ctx: JobContext,
) -> str | None:

    metadata = ctx.job.metadata

    if not metadata:
        return None

    try:

        data = json.loads(metadata)

        return data.get("phone_number")

    except json.JSONDecodeError:

        return metadata.strip() or None


# ============================================================
# NORMALIZE SIP DESTINATION
# ============================================================

def normalize_sip_destination(
    destination: str,
) -> str:
    """
    Convert a full SIP URI into the SIP user expected by
    LiveKit's create_sip_participant API.

    Example:

        sip:krishimitra2026@sip.linphone.org

    becomes:

        krishimitra2026
    """

    destination = destination.strip()

    # Remove sip:
    if destination.lower().startswith("sip:"):

        destination = destination[4:]

    # Remove domain
    if "@" in destination:

        destination = destination.split(
            "@",
            1,
        )[0]

    return destination.strip()


# ============================================================
# OUTBOUND SESSION
# ============================================================

@server.rtc_session(
    agent_name="outbound-agent"
)
async def outbound_agent(
    ctx: JobContext,
):

    ctx.log_context_fields = {
        "room": ctx.room.name,
        "agent": "Krishi Mitra",
    }

    # --------------------------------------------------------
    # GET DESTINATION
    # --------------------------------------------------------

    phone_number = phone_number_from_metadata(ctx)

    if not phone_number:

        logger.error(
            "No destination found in job metadata."
        )

        ctx.shutdown()

        return

    logger.info(
        "Preparing outbound call to %s",
        phone_number,
    )

    # --------------------------------------------------------
    # CHECK SIP TRUNK
    # --------------------------------------------------------

    if not OUTBOUND_TRUNK_ID:

        logger.error(
            "LIVEKIT_SIP_OUTBOUND_TRUNK_ID is not set."
        )

        ctx.shutdown()

        return

    # --------------------------------------------------------
    # NORMALIZE SIP DESTINATION
    # --------------------------------------------------------

    sip_destination = normalize_sip_destination(
        phone_number
    )

    if not sip_destination:

        logger.error(
            "SIP destination is empty."
        )

        ctx.shutdown()

        return

    logger.info(
        "Normalized SIP destination: %s",
        sip_destination,
    )

    # --------------------------------------------------------
    # CONNECT TO LIVEKIT
    # --------------------------------------------------------

    await ctx.connect()

    # --------------------------------------------------------
    # VOICE PIPELINE
    #
    # Deepgram → Gemini → Murf
    # --------------------------------------------------------

    session = AgentSession(

        stt=deepgram.STT(
            model="nova-3",
            language="multi",
            smart_format=True,
            endpointing_ms=100,
        ),

        llm=google.LLM(
            model="gemini-3.5-flash-lite",
        ),

        tts=murf.TTS(
            voice="Anisha",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(
                min_sentence_len=2
            ),
            text_pacing=True,
        ),

        turn_detection=MultilingualModel(),

        vad=ctx.proc.userdata["vad"],

        preemptive_generation=True,
    )

    # --------------------------------------------------------
    # START VOICE SESSION
    # --------------------------------------------------------

    session_started = asyncio.create_task(

        session.start(

            agent=OutboundAgent(ctx),

            room=ctx.room,

            room_options=room_io.RoomOptions(

                audio_input=room_io.AudioInputOptions(

                    noise_cancellation=lambda params: (

                        noise_cancellation.BVCTelephony()

                        if (
                            params.participant
                            and params.participant.kind
                            == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                        )

                        else noise_cancellation.BVC()
                    )
                )
            )
        )
    )

    # --------------------------------------------------------
    # DIAL LINPHONE
    # --------------------------------------------------------

    logger.info(
        "Dialing SIP user: %s",
        sip_destination,
    )

    logger.info(
        "Creating SIP participant: trunk=%s, destination=%s",
        OUTBOUND_TRUNK_ID,
        sip_destination,
    )

    try:

        participant = (
            await ctx.api.sip.create_sip_participant(

                api.CreateSIPParticipantRequest(

                    room_name=ctx.room.name,

                    sip_trunk_id=OUTBOUND_TRUNK_ID,

                    # IMPORTANT:
                    # Use normalized SIP USER, NOT:
                    # sip:username@sip.linphone.org
                    sip_call_to=sip_destination,

                    participant_identity=CALLEE_IDENTITY,

                    participant_name="Krishi Farmer",

                    wait_until_answered=True,
                )
            )
        )

        logger.info(
            "SIP participant created successfully: %s",
            participant,
        )

    except api.TwirpError as e:

        logger.error(
            "SIP CALL FAILED: code=%s message=%s status=%s metadata=%s",
            e.code,
            e.message,
            getattr(e, "status", None),
            getattr(e, "metadata", None),
        )

        session_started.cancel()

        ctx.shutdown()

        return

    except Exception as e:

        logger.exception(
            "UNEXPECTED OUTBOUND CALL ERROR: %s",
            e,
        )

        session_started.cancel()

        ctx.shutdown()

        return

    # --------------------------------------------------------
    # WAIT FOR VOICE SESSION
    # --------------------------------------------------------

    try:

        await session_started

    except asyncio.CancelledError:

        logger.warning(
            "Voice session task was cancelled."
        )

        return

    except Exception as e:

        logger.exception(
            "VOICE SESSION FAILED: %s",
            e,
        )

        ctx.shutdown()

        return

    # --------------------------------------------------------
    # FIRST WORDS THE FARMER HEARS
    # --------------------------------------------------------

    logger.info(
        "Call answered. Starting Krishi Mitra greeting."
    )

    try:

        await session.say(
            GREETING,
            allow_interruptions=True,
        )

    except Exception as e:

        logger.exception(
            "Failed to play greeting: %s",
            e,
        )

        ctx.shutdown()

        return


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    cli.run_app(server)
