# sim_backend/ai_client.py

import os
import json
import openai
from dotenv import load_dotenv
from openai import OpenAI

from sim_backend.prompt_builder_01 import (
    get_mouse_trial_system_prompt,
    build_user_prompt
)

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    api_key=os.environ.get(
        "OPENAI_API_KEY", API_KEY
    )
)



def run_trial(params: dict) -> str:
    system_msg = get_mouse_trial_system_prompt()
    user_msg   = build_user_prompt(params)

    resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user",   "content": user_msg},
            ],
            temperature=0.0,
        )
    return resp.to_dict()["choices"][0]["message"]["content"]


#raw = resp.choices[0].message.content

