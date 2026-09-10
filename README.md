# Career-Agent (Digital Twin)

**Live demo:** https://career-agent-k7lt.onrender.com/
*(Hosted on Render's free tier — the server sleeps after inactivity, so the first load may take 30–60 seconds to wake up.)*

A conversational AI agent that acts as my "digital twin" — it answers questions about my career, background, and skills on my behalf, so recruiters and collaborators can get quick, accurate answers even when I'm not available to chat directly.

## How it works

- **Main conversation model**: Llama 3.3 70B served via the Groq API, given a system prompt built from my resume and LinkedIn profile as context.
- **Guardrail / judge model**: every response is checked by a second LLM call (via OpenRouter, using structured/parsed output) that classifies whether the reply is actually career-related. If it isn't, the agent is nudged to try again, up to a retry limit, instead of answering off-topic questions.
- **Tool calling**: the agent can call functions to (1) record a visitor's name and email when they express interest in getting in touch, and (2) log any question it couldn't answer, so I can review and improve the knowledge base later. Both are pushed to my phone in real time via Pushover.
- **Interface**: a Gradio `ChatInterface` with custom CSS/JS and example prompts for a more polished chat experience than the Gradio default.

## Tech stack

- Python
- Gradio (UI)
- Groq API (Llama 3.3 70B — main chat model)
- OpenRouter API (Llama 3.3 70B — guardrail/judge with structured outputs)
- Pydantic (structured output schema for the judge)
- Pushover API (real-time notifications)
- python-dotenv (environment/config management)

## Architecture

```
app.py         → Gradio app, main chat loop, guardrail logic
context.py     → Builds the system prompt from my resume/LinkedIn/summary (see Knowledge base below)
tools.py       → Tool definitions + handlers (record_user_details, record_unknown_question)
models.py      → Pydantic schema for the judge's structured output
styles.py      → Custom CSS/JS and example prompts for the Gradio UI
```

## Knowledge base

`context.py` builds the agent's system prompt from three source files at startup:

- `Danish_Arshid.pdf` — my resume, parsed with `pypdf`
- `linkedin.pdf` — an exported copy of my LinkedIn profile, parsed with `pypdf`
- `summary.txt` — a short hand-written summary of my background

Their extracted text is injected directly into the system prompt, so the agent's answers are grounded in these documents rather than invented. These files are required for the app to run — removing them will break both local and deployed versions.

## Setup (run locally)

1. Clone the repo and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` file in the project root with:
   ```
   GROQ_API_KEY=your_groq_key
   OPENROUTER_API_key=your_openrouter_key
   PUSHOVER_USER=your_pushover_user_key
   PUSHOVER_TOKEN=your_pushover_app_token
   ```
3. Run the app:
   ```bash
   python app.py
   ```
   This launches a local Gradio interface in your browser.

## Deployment

Deployed on [Render](https://render.com) as a web service, with the same environment variables configured in the Render dashboard instead of a local `.env` file.

## Why I built this

I wanted to explore practical multi-agent patterns beyond a single prompt-response loop — specifically, using a second model as a guardrail/judge with structured outputs, and giving an agent real tool-calling ability with side effects (push notifications) rather than just retrieval. It's also genuinely useful as a first point of contact for anyone looking into my background.

## Possible next steps

- Add retrieval over my resume/projects instead of stuffing everything into the system prompt
- Add automated tests for the guardrail logic
- Move off Render's free tier (or add a keep-alive ping) to avoid cold-start delays on first load