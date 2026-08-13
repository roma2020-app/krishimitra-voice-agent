# Krishi Mitra – AI Voice Assistant for Indian Farmers
## Krishi Mitra – Farm & Field 🌾

Krishi Mitra is a voice-based agricultural assistant designed to help
Indian farmers with farming-related questions through natural voice
conversation.

The project is being developed as part of **10 Days of Voice Agents –
VoiceForBharat Edition**.

# Day 1 :Get Your Voice Agent Talking

- Fork the starter repository named as KrishiMitra-voice-agent
- Set up and run the voice agent
- Configure the required API keys
- Select a track: Farm & Field
- Give the agent an Indian voice
- Connect to the agent
- Have a short voice conversation as Crop information, Weather,Rain alerts,Agricultural guidance,Government schemes,Market information,Farmer-specific assistance


# Day 2 – Give Krishi Mitra a Personality, a Job, and Limits

## Krishi Mitra – Farm & Field

On Day 1, Krishi Mitra was able to hear the user and respond using voice.

For Day 2, Krishi Mitra becomes a defined agricultural voice assistant with:

- A clear identity
- Specific call objectives
- Agricultural responsibilities
- Language and code-mixing behavior
- Safety guardrails
- Escalation behavior
- A consistent conversational personality

The goal is not just to make Krishi Mitra talk, but to make it clear **what Krishi Mitra is responsible for and what it must not do**.
#Day2 Demo:

Farmer:
नमस्ते।

Krishi Mitra:
नमस्ते! मैं Krishi Mitra हूँ।
मैं खेती, मौसम और कृषि योजनाओं से जुड़ी
जानकारी में आपकी मदद कर सकती हूँ।

Farmer:
कल Jaipur में rain की possibility कितनी है?

Krishi Mitra:
Jaipur में कल बारिश की संभावना 94 प्रतिशत है...

Farmer:
Can you tell me the current wheat market price?

Krishi Mitra:
मेरे पास अभी verified और current market price
की जानकारी नहीं है, इसलिए मैं अनुमान लगाकर
गलत कीमत नहीं बताऊँगी।

# Day 3 – Personalise Your Agent's Frontend

On Day 3, Krishi Mitra's frontend was personalised for the **Farm & Field** track.

The goal was to make the voice interface simple, clear, and accessible for farmers while clearly showing the current state of the voice agent.

The frontend provides a simple flow:

    Ready
       ↓
    Connecting
       ↓
    Listening
       ↓
    Speaking
       ↓
    Call Ended
       ↓
    Start Again


Day 3 gives Krishi Mitra a user-facing interface designed specifically for the Farm & Field track.

The project now has:

    Voice Agent
          +
    Agricultural Personality
          +
    Safety Guardrails
          +
    Farmer-Friendly Frontend

This provides the foundation for the next stages of Krishi Mitra.

#Day3 Demo

### Ready

    🌾 Krishi Mitra

    आपका खेती का Voice Assistant

    [ Start Conversation ]

---

### Connecting

    Connecting...

    Krishi Mitra से जुड़ रहे हैं।

---

### Listening

    🎤 Listening to you

    Farmer:
    कल Jaipur में बारिश की संभावना कितनी है?

---

### Speaking

    🔊 Agent is speaking

    Krishi Mitra:
    Jaipur में कल बारिश की संभावना 94 प्रतिशत है...

---

### Call Ended

    Call ended

    धन्यवाद!

    [ Start Again ]

---
# Day 4 – Give Your Agent a Memory That Lasts

On Day 4, Krishi Mitra was given persistent memory.

Previously, the agent could have a conversation but would forget the farmer when the call ended.

For Day 4, Krishi Mitra stores farmer information in a SQLite database so that the information can be retrieved during future conversations.

# 1. Database

Krishi Mitra uses SQLite for persistent memory.

Database:    krishi_mitra.db

SQLite was selected because it is lightweight and suitable for the project.

---

# 2. Farmer Profile

The farmer profile stores:

```text
user_id
name
language_preference
crops_grown
land_size
district
irrigation_type
last_interaction
Saved one record:
  {
    "user_id": "farmer001",
    "name": "Ravi",
    "language_preference": "hi",
    "crops_grown": "गेहूं",
    "land_size": "5 acres",
    "district": "Jaipur",
    "irrigation_type": "Canal",
    "last_interaction": "2026-08-11T12:23:39"
}
--

# Day 4 – Demo
First Conversation:
Farmer
मेरा नाम Ravi है।
मैं Jaipur में गेहूं उगाता हूँ।
मेरे पास 5 acres जमीन है।
Krishi Mitra
Ravi जी, क्या मैं आपकी गेहूं की फसल,
5 acres जमीन और Jaipur की जानकारी
आगे की बातचीत के लिए याद रखूँ?
Farmer
हाँ।
Krishi Mitra
ठीक है Ravi जी।
मैं आपकी यह जानकारी याद रखूँगी।

The information is then stored in SQLite.

Second Conversation:
Krishi Mitra:

नमस्ते Ravi जी!
आपसे फिर बात करके अच्छा लगा।

पिछली बार आपने बताया था कि आप Jaipur में
गेहूं की खेती करते हैं।

बताइए, आज मैं आपकी कैसे मदद करूँ?
--

# Day 5– Tools
On Day 5, Krishi Mitra was connected to a real-world weather data source.

Until Day 4, Krishi Mitra could:

- Talk to farmers
- Follow its Farm & Field role
- Follow safety guardrails
- Remember farmer information

On Day 5, Krishi Mitra can retrieve real weather information instead of guessing.

### Live Weather Lookup Tool

The purpose of the tool is to provide farmers with current weather
information instead of relying on static or hallucinated information.

A farmer can ask questions such as:

- "आज मुंबई का मौसम कैसा है?"
- "What is the weather in Nashik today?"
- "Will it rain in Pune today?"

The agent automatically decides when the weather tool is required and
calls it to retrieve the latest available weather information.

### Weather Tool Capabilities

The weather tool can retrieve:

- City or district
- Current temperature
- Humidity
- Rainfall
- Wind speed
- Latest available weather data time

The returned weather information is converted into a natural voice
response instead of exposing raw JSON or technical API fields to the
farmer.

### Real Data Source

Weather data is retrieved live from **Open-Meteo**.

Open-Meteo:
https://open-meteo.com/

The project uses live weather data and does not use a hand-built local
weather dataset.

### Tool Calling

The weather tool is implemented as a LiveKit function tool.

The agent's tool description instructs the model to use the tool when
the farmer asks about:

- Current weather
- Today's temperature
- Rain
- Rainfall
- Humidity
- Wind
- Current weather conditions

The agent should not invent current weather information.

### Data Freshness

The weather tool returns the latest available weather data timestamp.

For example, the voice response can communicate:

"नवीनतम उपलब्ध मौसम डेटा के अनुसार, आज सुबह 5 बजे Mumbai में
तापमान लगभग 26.5 डिग्री सेल्सियस है और हल्की बारिश की संभावना है।"

This makes it clear to the farmer when the information is from.

### Failure Handling

The weather API may become unavailable or take too long to respond.

The tool handles these failures and returns a failure response to the
agent.

When the weather service is unavailable, Krishi Mitra does not invent
weather information.

Instead, it gives the farmer a natural fallback such as:

"मौसम सेवा अभी अस्थायी रूप से उपलब्ध नहीं है। कृपया थोड़ी देर बाद
फिर से प्रयास करें।"

This ensures that the voice agent fails gracefully instead of
hallucinating current weather information.

## Day 4 + Day 5 Integration

Krishi Mitra also maintains a farmer profile using the memory system
introduced on Day 4.

The saved farmer profile can contain information such as:

- Farmer name
- District
- Crops grown
- Land size
- Irrigation type
- Language preference

The saved district can be used by the weather tool so that the farmer
does not have to repeatedly provide their location.

Example:

Farmer:
"आज मौसम कैसा है?"

Agent:
Uses the saved farmer district and calls the live weather tool.

This connects the Day 4 memory capability with the Day 5 tool capability.

## Voice AI Stack

- LiveKit Agents
- Google Gemini
- Deepgram STT
- Murf Falcon TTS
- Open-Meteo Weather API
- Python
- Farmer memory database

### Voice Pipeline

User Speech
    ↓
Deepgram STT
    ↓
Google Gemini
    ↓
Weather Function Tool
    ↓
Open-Meteo
    ↓
Weather Result
    ↓
Google Gemini
    ↓
Murf Falcon TTS
    ↓
Natural Voice Response
--

## Day 5 Validation

The following Day 5 requirements have been tested:

- [x] Real domain tool implemented
- [x] Live weather data retrieved
- [x] Agent automatically calls the weather tool
- [x] Weather result is spoken naturally
- [x] Weather data timestamp is communicated
- [x] API failure path tested
- [x] Agent does not hallucinate weather when API is unavailable

# Day 5 –Demo

Example successful interaction:

Farmer:
"आज Mumbai का मौसम कैसा है?"

Krishi Mitra:
"नवीनतम उपलब्ध मौसम डेटा के अनुसार, आज सुबह 5 बजे Mumbai में
तापमान लगभग 26.5 डिग्री सेल्सियस है और हल्की बारिश की संभावना है।"

Example failure interaction:

Farmer:
"आज Mumbai का मौसम कैसा है?"

Krishi Mitra:
"मौसम सेवा अभी अस्थायी रूप से उपलब्ध नहीं है। कृपया थोड़ी देर बाद
फिर से प्रयास करें।"


# Day 6 – Krishi Mitra Outbound Calls

## Farm & Field – Proactive Weather Alert

For Day 6 of the **10 Days of Voice Agents – Voice for Bharat Challenge 2026**, Krishi Mitra has been extended from a browser-based voice assistant to an **outbound voice agent**.

Krishi Mitra can proactively call a farmer and provide personalized agricultural information such as weather and rain alerts.

The outbound call uses:

- SQLite farmer database
- LiveKit Agents
- LiveKit room and agent dispatch
- Linphone SIP
- Open-Meteo weather API
- Murf AI TTS
- Hindi and English voice interaction

-- 
# Day 6 – Krishi Mitra Outbound Calls:Demo
After phone answering Agent asks:
नमस्ते Ravi जी!

मैं Krishi Mitra हूँ।
आपकी गेहूं की फसल के लिए एक महत्वपूर्ण
बारिश की चेतावनी देने के लिए कॉल कर रही हूँ।

कल Jaipur में बारिश की संभावना बहुत अधिक है।
कृपया अपनी फसल के लिए आवश्यक सावधानी रखें।

अगर आप यह कॉल नहीं चाहते हैं,
तो कह सकते हैं "कॉल बंद करें"।
The farmer can ask:

कल बारिश की संभावना कितनी है?

The weather tool retrieves the forecast.

Example result:

Rain probability : 94%
Rainfall         : 15.9 mm
Temperature      : 25.1°C - 32.4°C

The agent responds:

Jaipur में कल बारिश की संभावना 94 प्रतिशत है।
लगभग 15.9 मिलीमीटर बारिश होने का अनुमान है।
तापमान न्यूनतम 25.1 और अधिकतम 32.4 डिग्री रहेगा।
Krishi Mitra can handle Hindi and English conversations.

Example:

Farmer:
You please repeat it in English?

The agent can respond:

Under the PM Kisan scheme, eligible farmers
receive an annual financial assistance of
six thousand rupees.

This amount is transferred directly to
the bank account.
The farmer can continue the conversation after receiving the weather warning.

For example:

Farmer:
Do I know about PM Kisan scheme?

Krishi Mitra can provide information about government schemes and other agricultural topics.

This makes the outbound call interactive rather than a simple automated announcement.
The farmer can request to end the conversation.

Example:

Farmer:
No. No. Thank you.

The agent invokes the end-call functionality.

Example response:

धन्यवाद, Ravi जी!
आपका दिन शुभ हो।

The LiveKit session is then closed.


#Day7 Know When to Ask for Human Help
🌱 Serious Crop Problem → Human Expert

When a farmer reports a serious crop disease or damage, Krishi Mitra can recognize that expert help is needed instead of giving an uncertain diagnosis.

It can escalate the request to a human agriculture expert.

🔐 Permission First

Before sharing farmer information, Krishi Mitra asks for permission.

The farmer can say हाँ, and only then is the escalation request created.

🧠 Farmer Memory

The system uses the farmer's saved information such as:

Name

District

Crop

Language preference

🎫 Human Escalation

The request receives a reference ID:

KM-E8D30098

with an OPEN status for human follow-up.

🖥️ Human Help Dashboard

I also created a simple dashboard where the human expert can see the open request and the useful information needed to handle it.

The complete flow

Farmer reports problem → AI identifies need for human help → asks permission → creates escalation → generates reference ID → human sees the request


Day 8 – Build a Call Analytics Dashboard
A Streamlit-based monitoring dashboard has been implemented for Krishi Mitra to provide real-time visibility into voice-agent performance and human-help escalations.

The dashboard loads call information from the live call analytics database and displays the overall number of calls, successful calls, failed calls, and calculated success rate. It also provides a channel-wise breakdown of agent activity, separately tracking Browser Calls and SIP Outbound Calls, including total, successful, and failed calls for each channel.

In addition to call analytics, the dashboard includes a Human Help monitoring section. It retrieves open escalation requests and displays the number of open requests along with high- and medium-priority requests. Each escalation is presented as a detailed request card containing the farmer name, district, crop, reason for escalation, what happened during the interaction, what Krishi Mitra already checked, urgency, language, preferred follow-up method, status, and creation time.

A Refresh button allows the dashboard to reload the latest information from the database, ensuring that the displayed metrics reflect newly completed calls and newly created human-help requests.

Dashboard Flow
Browser Voice Call ──┐
                     │
                     ├──> Call Analytics Database ──> Streamlit Dashboard
SIP Outbound Call ───┘                                  │
                                                        ├── Total Calls
                                                        ├── Successful Calls
                                                        ├── Failed Calls
                                                        ├── Success Rate
                                                        ├── Browser Metrics
                                                        └── SIP Metrics

Voice Agent ──> Human Escalation ──> Escalation Database ──> Human Help Dashboard
                                                              │
                                                              ├── Open Requests
                                                              ├── High Priority
                                                              ├── Medium Priority
                                                              └── Detailed Farmer Request
What Has Been Demonstrated
Live call analytics loaded from the database
Total / successful / failed call tracking
Overall success-rate calculation
Browser vs SIP channel analytics
Human-help escalation monitoring
Priority-based escalation counts
Detailed farmer escalation information
Manual dashboard refresh
No hardcoded call statistics

Provided a single dashboard to monitor both voice-agent call performance and human-in-the-loop support activity.


## Day 9 – Hand Off to a Specialist Agent

On Day 9, **Krishi Mitra** was upgraded with a dedicated **Crop Problem Specialist** that takes over when a farmer needs focused crop-health assistance. The specialist receives the existing conversation context so the farmer does not need to repeat the problem, and when additional support is required, it can use the existing **Human Help escalation system** to create a request for an agriculture expert and display it on the Human Help Dashboard.


## Challenge

This project is being developed as part of:

**10 Days of Voice Agents – VoiceForBharat Edition**

The voice agent uses **Murf Falcon** for text-to-speech.

#VoiceForBharat
