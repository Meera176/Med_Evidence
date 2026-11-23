import os
from groq import Groq

_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")


def build_context(chunks: list[dict]) -> str:
    blocks = []
    for i, chunk in enumerate(chunks, 1):
        blocks.append(
            f"[{i}] (source: {chunk['source']}, page: {chunk['page']})\n{chunk['text']}"
        )
    return "\n\n".join(blocks)


def ask(query: str, top_chunks: list[dict]) -> str:
    context = build_context(top_chunks)
    messages = [
        {
            "role": "system",
            "content": (
                "You are a medical research assistant. "
                "Answer only based on the provided context. "
                "If the answer is not in the context, say you don't know. "
                "Always structure your answer in the following format:\n\n"
                "## Overview\n"
                "A brief 2-3 sentence summary of the answer.\n\n"
                "## Key Points\n"
                "- Point 1\n"
                "- Point 2\n"
                "- Point 3\n\n"
                "## Details\n"
                "A more detailed explanation with citations like [1], [2] referring to the source numbers.\n\n"
                "## Important Notes\n"
                "Any warnings, limitations, or important considerations."
            ),
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {query}",
        },
    ]
    response = _client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.2,
    )
    return response.choices[0].message.content
