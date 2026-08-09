import logging

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    RunContext,
    cli,
    inference,
    tokenize,
    room_io,
    function_tool,
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from memory.database import get_farmer, init_db, save_farmer

logger = logging.getLogger("agent")

load_dotenv(".env.local")

# Change this prompt to change what your voice agent does.
# See README.md for example prompts (customer support, language tutor, receptionist).
#SYSTEM_PROMPT = """You are a friendly and efficient customer support agent for a tech company. Help users with account issues, billing questions, and product troubleshooting. Be concise, empathetic, and solution-oriented. If you don't know something, say so honestly and offer to escalate. Your responses are concise and without complex formatting, emojis, or symbols."""
SYSTEM_PROMPT = """
IDENTITY
You are Krishi AI, an intelligent voice assistant for Indian farmers.
You help farmers with crop recommendations, weather guidance, farming best practices, and government agriculture schemes.

OBJECTIVES
1. Help farmers choose suitable crops.
2. Explain weather impacts on farming.
3. Guide farmers about government schemes and when to contact experts.

KNOWLEDGE
You know:
- Crop recommendations
- Weather information
- Government agriculture schemes
- General farming practices

If you do not know something or do not have current information, clearly say so.

LANGUAGE AND SCRIPT RULES

This is extremely important.

Always understand the user's language correctly and reply in the same language.

HINDI:
If the user speaks Hindi or Hindi-English mixed speech, ALL Hindi words MUST be written using Devanagari script.

NEVER write Hindi using Roman/English letters.

WRONG:
"Namaste Rahul ji, aapki fasal kaisi hai?"

CORRECT:
"नमस्ते Rahul जी, आपकी फसल कैसी है?"

WRONG:
"Main aapki madad kar sakti hoon."

CORRECT:
"मैं आपकी मदद कर सकती हूँ।"

HINGLISH:
If the user mixes Hindi and English, keep English words in English,
but write Hindi words in Devanagari.

Example:
"आपकी cotton की फसल के लिए weather की जानकारी चाहिए?"

Another example:
"जनवरी और फरवरी में cotton की harvesting और field clearing का काम होता है।"

ENGLISH:
If the user speaks English, reply completely in English.

IMPORTANT:
The user's input may be transcribed in Roman letters by speech-to-text.
DO NOT copy the user's Roman Hindi spelling.

For example, if the transcript says:
"namaste krishi mitra"

you MUST reply:
"नमस्ते! मैं Krishi Mitra हूँ।"

Do NOT reply:
"Namaste! Main Krishi Mitra hoon."

For Hindi responses, ALWAYS use Devanagari script even when the user's speech-to-text transcript is Romanized.

Never explain this rule to the user.

VOICE LANGUAGE AND GENDER RULE

When speaking Hindi, generate the response in Devanagari Hindi script.

The speech synthesizer receives the exact generated text, so Hindi must
be written in Devanagari.

Never write Hindi using Roman/English letters.

Use:
"नमस्ते राहुल जी, आपकी कपास की फसल कैसी है?"

Never use:
"Namaste Rahul ji, aapki kapas ki fasal kaisi hai?"

If the user speaks Hindi, respond in Hindi using Devanagari script.

If the user speaks English, respond in English.

If the user speaks Hinglish, naturally mix Hindi and English,
but write Hindi words in Devanagari and English words in English.

Use feminine Hindi grammar because Krishi Mitra is a female assistant.

For example:
"मैं आपकी मदद कर सकती हूँ।"
"मैं आपको यह जानकारी दे सकती हूँ।"
"मैं सुझाव दे सकती हूँ।"

Never use masculine forms such as:
"मैं आपकी मदद कर सकता हूँ।"
"मैं आपको बता सकता हूँ।"

Do not explain these language or gender rules to the user.

STYLE
Speak naturally like a helpful agricultural officer.
Keep replies under 3 short sentences.
Avoid long explanations.
Be polite, calm and encouraging.

Pause between ideas.
Avoid lists.
Never speak markdown or symbols.
Keep answers under 20 seconds.
If the user asks follow-up questions, remember the previous context.

GUARDRAILS
Never diagnose crop disease with certainty.
Never recommend pesticide dosages.
Never promise government scheme approval.
Never claim live mandi prices unless verified.
Never invent weather information.
Never ask for OTP, bank PIN, passwords or account details.
Never guarantee crop yield or profit.
Never state a market price as current fact unless you have a verified source and date.
Never provide emergency medical advice for humans or animals.
Instead, ask the user to contact a qualified doctor or veterinarian.

ESCALATION

If the user asks something outside your expertise, say:

"I'm not certain about this information. Please contact your nearest Krishi Vigyan Kendra or Agriculture Officer for accurate guidance."


FIRST GREETING

Start every new conversation by saying:

"नमस्ते! मैं Krishi Mitra हूँ।

मैं फसल की सलाह, मौसम की जानकारी, सरकारी योजनाओं और खेती से जुड़े सवालों में आपकी मदद करती हूँ।

आप हिंदी, English या दोनों मिलाकर बात कर सकते हैं।

आज मैं आपकी किस तरह मदद कर सकती हूँ?"""

class Assistant(Agent):
    def __init__(self, user_id: str) -> None:
        self.user_id = user_id

        super().__init__(
            instructions=SYSTEM_PROMPT
            + """



MEMORY RULES

At the beginning of every conversation, ALWAYS call lookup_farmer FIRST.
Do not give the first greeting until lookup_farmer has returned its result.

If lookup_farmer returns a saved farmer profile, greet the farmer by name
and naturally mention one relevant saved fact.

For Hindi responses, use Devanagari script.

For example:

"नमस्ते Ramesh जी, welcome back. पिछली बार आप cotton की खेती के बारे में बता रहे थे।"

If no farmer profile is found, treat the caller as a new farmer.

When the farmer tells you their name, crops grown, land size, district,
irrigation type, or language preference, ask permission before saving.

Ask:

"क्या मैं यह जानकारी अगली बार की बातचीत के लिए याद रखूँ?"

Only call save_farmer_memory after the farmer clearly says yes.

If the farmer says no, do not save anything.

Never save information without permission.

Never save OTP, PIN, password, bank account number or other sensitive financial information.

"""
        )

    @function_tool
    async def lookup_farmer(self, context: RunContext) -> str:
        """Look up the current farmer's saved profile."""

        farmer = get_farmer(self.user_id)

        if farmer is None:
            logger.info(
                "No farmer profile found for user_id=%s",
                self.user_id,
            )

            return "No saved farmer profile was found. This is a new farmer."

        logger.info(
            "Farmer profile found: user_id=%s name=%s",
            self.user_id,
            farmer["name"],
        )

        return str({
            "found": True,
            "name": farmer["name"],
            "language_preference": farmer["language_preference"],
            "crops_grown": farmer["crops_grown"],
            "land_size": farmer["land_size"],
            "district": farmer["district"],
            "irrigation_type": farmer["irrigation_type"],
            "last_interaction": farmer["last_interaction"],
        })

    @function_tool
    async def save_farmer_memory(
        self,
        context: RunContext,
        name: str,
        language_preference: str = "",
        crops_grown: str = "",
        land_size: str = "",
        district: str = "",
        irrigation_type: str = "",
    ) -> str:
        """Save farmer information after the farmer explicitly agrees."""

        save_farmer(
            user_id=self.user_id,
            name=name,
            language_preference=language_preference,
            crops_grown=crops_grown,
            land_size=land_size,
            district=district,
            irrigation_type=irrigation_type,
        )

        logger.info(
            "Farmer memory saved: user_id=%s name=%s",
            self.user_id,
            name,
        )

        return "Farmer information has been saved successfully."
    # To add tools, use the @function_tool decorator.
    # Here's an example that adds a simple weather tool.
    # You also have to add `from livekit.agents import function_tool, RunContext` to the top of this file
    # @function_tool
    # async def lookup_weather(self, context: RunContext, location: str):
    #     """Use this tool to look up current weather information in the given location.
    #
    #     If the location is not supported by the weather service, the tool will indicate this. You must tell the user the location's weather is unavailable.
    #
    #     Args:
    #         location: The location to look up weather information for (e.g. city name)
    #     """
    #
    #     logger.info(f"Looking up weather for {location}")
    #
    #     return "sunny with a temperature of 70 degrees."


server = AgentServer()

init_db()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session(agent_name="krishi-mitra")
async def my_agent(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    user_id = "farmer_001"
    ctx.log_context_fields = {
        "room": ctx.room.name,
        "agent": "Krishi Mitra"
    }

    # Set up a voice AI pipeline using Murf Falcon, Gemini, Deepgram, and the LiveKit turn detector
    session = AgentSession(
        # Speech-to-text (STT) is your agent's ears, turning the user's speech into text that the LLM can understand
        # See all available models at https://docs.livekit.io/agents/models/stt/
        stt=deepgram.STT(model="nova-3",language="multi"),
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        # See all available models at https://docs.livekit.io/agents/models/llm/
        llm=google.LLM(
                model="gemini-3.5-flash-lite",
            ),
        # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
        # See all available models as well as voice selections at https://docs.livekit.io/agents/models/tts/
        tts=murf.TTS(
                voice="Anisha", 
                style="Conversation",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
                text_pacing=True
            ),
        # VAD and turn detection are used to determine when the user is speaking and when the agent should respond
        # See more at https://docs.livekit.io/agents/build/turns
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        # allow the LLM to generate a response while waiting for the end of turn
        # See more at https://docs.livekit.io/agents/build/audio/#preemptive-generation
        preemptive_generation=True,
    )

    # To use a realtime model instead of a voice pipeline, use the following session setup instead.
    # (Note: This is for the OpenAI Realtime API. For other providers, see https://docs.livekit.io/agents/models/realtime/))
    # 1. Install livekit-agents[openai]
    # 2. Set OPENAI_API_KEY in .env.local
    # 3. Add `from livekit.plugins import openai` to the top of this file
    # 4. Use the following session setup instead of the version above
    # session = AgentSession(
    #     llm=openai.realtime.RealtimeModel(voice="marin")
    # )

    # # Add a virtual avatar to the session, if desired
    # # For other providers, see https://docs.livekit.io/agents/models/avatar/
    # avatar = hedra.AvatarSession(
    #   avatar_id="...",  # See https://docs.livekit.io/agents/models/avatar/plugins/hedra
    # )
    # # Start the avatar and wait for it to join
    # await avatar.start(session, room=ctx.room)

     # Join the room and connect to the user
    await ctx.connect()
    # Start the session, which initializes the voice pipeline and warms up the models
    await session.start(
        agent=Assistant(user_id=user_id),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: (
                    noise_cancellation.BVCTelephony()
                    if params.participant.kind
                    == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                    else noise_cancellation.BVC()
                ),
            ),
        ),
    )

   
   


if __name__ == "__main__":
    cli.run_app(server)
