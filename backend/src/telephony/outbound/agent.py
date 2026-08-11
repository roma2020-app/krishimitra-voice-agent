"""Krishi Mitra personalized outbound telephony agent."""

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

CALLEE_IDENTITY = "krishi-farmer"

logger.info(
    "Outbound SIP trunk configured: %s",
    bool(OUTBOUND_TRUNK_ID),
)


# ============================================================
# BASE KRISHI MITRA SYSTEM PROMPT
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

WEATHER:

If the farmer asks about current weather, today's weather,
tomorrow's weather, future weather, temperature, rain,
rainfall, humidity, wind, or rain probability, use the
weather tool.

IMPORTANT:

The weather tool returns:

"current" = current weather

"tomorrow" = tomorrow's forecast

If the farmer asks about tomorrow, ALWAYS use the
"tomorrow" values.

For example, if the tool returns:

tomorrow:
temperature minimum = 25.1°C
temperature maximum = 32.4°C
rain probability = 94%
rainfall = 15.9 mm

and the farmer asks:

"कल का weather कैसा रहेगा?"

You should answer using those values.

Do NOT say:
"मैं कल का मौसम नहीं बता सकती।"

Do NOT say tomorrow's weather is unavailable when
the weather tool has returned tomorrow's data.

For a Hindi response, say naturally:

"कल तापमान लगभग 25 से 32 डिग्री रहेगा और बारिश की
संभावना 94 प्रतिशत है। लगभग 15.9 मिलीमीटर बारिश
होने का अनुमान है।"

Never invent weather information.
Only use values returned by the weather tool.

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
# OUTBOUND AGENT
# ============================================================

class OutboundAgent(Agent):

    def __init__(
        self,
        ctx: JobContext,
        farmer: dict | None = None,
    ) -> None:

        self.ctx = ctx
        self.farmer = farmer or {}

        farmer_name = self.farmer.get(
            "name",
            "किसान जी",
        )

        crop = self.farmer.get(
            "crop",
            "",
        )

        district = self.farmer.get(
            "district",
            "",
        )

        language = self.farmer.get(
            "language",
            "hi",
        )

        farmer_context = f"""

FARMER PROFILE FOR THIS CALL:

Farmer name: {farmer_name}
Preferred language: {language}
Crop grown: {crop}
District: {district}
Land size: {self.farmer.get("land_size", "")}
Irrigation type: {self.farmer.get("irrigation_type", "")}

PERSONALIZATION RULES:

1. Address the farmer by their name when appropriate.
2. Use the farmer's crop when discussing farming advice.
3. Use the farmer's district for weather context.
4. Do not repeatedly mention personal information.
5. Never reveal that the information came from a database.
6. Never invent farmer information.
7. If information is missing, simply avoid mentioning it.
"""

        super().__init__(
            instructions=SYSTEM_PROMPT + farmer_context
        )

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
        Get current and forecast weather for a city or district.
        Use this tool whenever the farmer asks about:
        - current weather
        - today's weather
        - tomorrow's weather
        - future weather
        - rain
        - rainfall
        - temperature
        - humidity
        - wind
        - tomorrow's rain probability
        IMPORTANT:
        The tool returns TWO sections:
        1. "current" = current weather
        2. "tomorrow" = tomorrow's forecast
        When the farmer asks about tomorrow, you MUST use the
        values inside the "tomorrow" section.
        Do NOT say that tomorrow's weather is unavailable if the tool returns a "tomorrow" section.
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
# GET CALL METADATA
# ============================================================

def metadata_from_context(
    ctx: JobContext,
) -> dict:

    metadata = ctx.job.metadata

    if not metadata:
        return {}

    try:

        data = json.loads(metadata)

        if isinstance(data, dict):
            return data

        return {}

    except json.JSONDecodeError:

        logger.warning(
            "Could not parse job metadata as JSON."
        )

        return {}


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

    if destination.lower().startswith("sip:"):
        destination = destination[4:]

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
    # GET METADATA
    # --------------------------------------------------------

    metadata = metadata_from_context(ctx)

    phone_number = metadata.get(
        "phone_number"
    )

    farmer = {
        "user_id": metadata.get(
            "farmer_id",
            "",
        ),
        "name": metadata.get(
            "farmer_name",
            "",
        ),
        "language": metadata.get(
            "language",
            "hi",
        ),
        "crop": metadata.get(
            "crop",
            "",
        ),
        "district": metadata.get(
            "district",
            "",
        ),
        "land_size": metadata.get(
            "land_size",
            "",
        ),
        "irrigation_type": metadata.get(
            "irrigation_type",
            "",
        ),
    }

    # --------------------------------------------------------
    # LOG FARMER INFORMATION
    # --------------------------------------------------------

    logger.info(
        "Outbound farmer: id=%s name=%s crop=%s district=%s",
        farmer["user_id"],
        farmer["name"],
        farmer["crop"],
        farmer["district"],
    )

    # --------------------------------------------------------
    # CHECK DESTINATION
    # --------------------------------------------------------

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

            agent=OutboundAgent(
                ctx,
                farmer,
            ),

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
                    # Use normalized SIP USER
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
    # PERSONALIZED GREETING
    # --------------------------------------------------------

    farmer_name = farmer.get(
        "name"
    ) or "किसान जी"

    crop = farmer.get(
        "crop"
    )

    district = farmer.get(
        "district"
    )

    if crop and district:

        #greeting = (
        #    f"नमस्ते {farmer_name} जी! "
        #    f"मैं Krishi Mitra हूँ। "
        #    f"आपकी {crop} की फसल के लिए "
        #    f"{district} क्षेत्र में मौसम की महत्वपूर्ण "
        #    f"जानकारी देने के लिए कॉल कर रही हूँ। "
        #   f"अगर आप यह कॉल नहीं चाहते हैं, "
        #   f"तो कह सकते हैं 'कॉल बंद करें'।"
        #)

        greeting = (
            f"नमस्ते {farmer_name} जी! "
            f"मैं Krishi Mitra हूँ। "
            f"आपकी {crop} की फसल के लिए एक महत्वपूर्ण "
            f"बारिश की चेतावनी देने के लिए कॉल कर रही हूँ। "
            f"कल {district} में बारिश की संभावना बहुत अधिक है। "
            f"कृपया अपनी फसल के लिए आवश्यक सावधानी रखें। "
            f"अगर आप यह कॉल नहीं चाहते हैं, "
            f"तो कह सकते हैं 'कॉल बंद करें'।"
)

    elif crop:

        greeting = (
            f"नमस्ते {farmer_name} जी! "
            f"मैं Krishi Mitra हूँ। "
            f"आपकी {crop} की फसल के लिए मौसम की "
            f"महत्वपूर्ण जानकारी देने के लिए कॉल कर रही हूँ। "
            f"अगर आप यह कॉल नहीं चाहते हैं, "
            f"तो कह सकते हैं 'कॉल बंद करें'।"
        )

    else:

        greeting = (
            f"नमस्ते {farmer_name} जी! "
            f"मैं Krishi Mitra हूँ। "
            f"मैं आपके खेत के मौसम की महत्वपूर्ण "
            f"जानकारी देने के लिए कॉल कर रही हूँ। "
            f"अगर आप यह कॉल नहीं चाहते हैं, "
            f"तो कह सकते हैं 'कॉल बंद करें'।"
        )

    # --------------------------------------------------------
    # LOG GREETING
    # --------------------------------------------------------

    logger.info(
        "Call answered. Starting personalized Krishi Mitra greeting."
    )

    logger.info(
        "Greeting farmer=%s crop=%s district=%s",
        farmer_name,
        crop,
        district,
    )

    # --------------------------------------------------------
    # SPEAK GREETING
    # --------------------------------------------------------

    try:

        await session.say(
            greeting,
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
