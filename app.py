from openai import OpenAI
import os
from context import TWIN_SYSTEM_PROMPT, system_prompt2
from tools import tools, handle_tool_calls
from styles import CSS, JS, EXAMPLES
from dotenv import load_dotenv
import gradio as gr
from models import JudgeGuardrail

#The main LLM Call
base_url = "https://api.groq.com/openai/v1"
api_key = os.getenv("GROQ_API_KEY")
load_dotenv(override=True)
openai = OpenAI(base_url = base_url,api_key = api_key)

system = [{"role": "system", "content": TWIN_SYSTEM_PROMPT}]

#The Judge call : 
base_url = "https://openrouter.ai/api/v1"
api_key = os.getenv("OPENROUTER_API_key")
openrouter =OpenAI(base_url = base_url,api_key=api_key)


def chat(user_message, history, retries=0):
    # Convert Gradio history to OpenAI format
    history = [
        {"role": h["role"], "content": h["content"]}
        for h in history
    ]

    messages = (
        [{"role": "system", "content": TWIN_SYSTEM_PROMPT}]
        + history
        + [{"role": "user", "content": user_message}]
    )

    # Initial LLM call
    response = openai.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        tools=tools
    )

    # Handle tool calls until the model produces a final answer
    while response.choices[0].finish_reason == "tool_calls":
        assistant_message = response.choices[0].message

        tool_calls = assistant_message.tool_calls
        results = handle_tool_calls(tool_calls)

        messages.append(assistant_message)
        messages.extend(results)

        response = openai.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=tools
        )

    # Final assistant response
    txt = response.choices[0].message.content

    # ---------- Guardrail ----------
    response2 = openrouter.beta.chat.completions.parse(
        model="meta-llama/llama-3.3-70b-instruct",
        messages=[
            {
                "role": "system",
                "content": system_prompt2
            },
            {
                "role": "user",
                "content": txt
            }
        ],
        response_format=JudgeGuardrail
    )

    judge = response2.choices[0].message.parsed

    if judge.careerRelated.lower() == "no":
        print(response2)
        print("Guardrail triggered")

        # Prevent infinite recursion
        if retries >= 2:
            return "I'm only able to answer career-related questions."

        # Preserve conversation history
        history.append({
            "role": "assistant",
            "content": txt
        })

        history.append({
            "role": "user",
            "content": "Your previous response was not career-related. Please answer only career-related questions."
        })

        return chat(user_message, history, retries + 1)

    return txt


if __name__ == "__main__":
    gr.ChatInterface(
        chat,
        examples=EXAMPLES,
        title="Digital Twin",
        description="Talk to my AI twin about my career",
        chatbot=gr.Chatbot(show_label=False),
    ).launch(css=CSS, js=JS, theme=gr.themes.Base())
