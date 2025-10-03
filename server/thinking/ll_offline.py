from openai import OpenAI
from config.llm import LOCAL_LLM_MODEL
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")


def think(query: str, context: list):
  # query is user question
  # context is last 5 messages
    messages = context + [{
        "role": "user",
        "content": (
            # f"{query} "
            "Only return the number. No words, no explanation, no punctuation. "
            "I don't need code to generate number — I need the number only."
        )
    }]
    resp = client.chat.completions.create(
        model=LOCAL_LLM_MODEL,
        messages=messages,
        temperature=1.0,
        max_tokens=5,
    )
    # return resp.choices[0].message.content
    return "1" # TODO: when proper offline llm part is implemented than delete this line and uncomment the above line
