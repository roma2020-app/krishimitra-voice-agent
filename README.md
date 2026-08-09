# Krishi Mitra – AI Voice Assistant for Indian Farmers

Krishi Mitra is a voice-based agricultural assistant designed to help
Indian farmers with farming-related questions through natural voice
conversation.

The project is being developed as part of **10 Days of Voice Agents –
VoiceForBharat Edition**.

## Day 5 – Tools

### Live Weather Lookup Tool

For Day 5, Krishi Mitra was connected to a real-time weather lookup tool.

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

## Day 5 Validation

The following Day 5 requirements have been tested:

- [x] Real domain tool implemented
- [x] Live weather data retrieved
- [x] Agent automatically calls the weather tool
- [x] Weather result is spoken naturally
- [x] Weather data timestamp is communicated
- [x] API failure path tested
- [x] Agent does not hallucinate weather when API is unavailable

## Day 5 Demo

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

## Challenge

This project is being developed as part of:

**10 Days of Voice Agents – VoiceForBharat Edition**

The voice agent uses **Murf Falcon** for text-to-speech.

#VoiceForBharat
