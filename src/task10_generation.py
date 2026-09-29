"""
Task 10 — Generation có citation.

Hướng dẫn:
    1. Retrieve top-k chunks.
    2. Reorder để giảm lost-in-the-middle.
    3. Format context kèm title và source.
    4. Gọi provider được chọn trong .env.
    5. Trả answer, sources và retrieval_source.

Nếu context không đủ hoặc provider lỗi, trả safe refusal; không bịa thông tin.
"""

import os

from dotenv import load_dotenv

from .task9_retrieval_pipeline import retrieve


load_dotenv()

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
LLM_MODEL = os.getenv("LLM_MODEL", "")

SYSTEM_PROMPT = """Trả lời câu hỏi của người dùng dựa trên context được cung cấp.
Mỗi thông tin/khẳng định trong câu trả lời phải kèm citation nguồn rõ ràng dưới dạng [Document X | Source].
Nếu context không chứa đủ bằng chứng để trả lời hoặc bạn không chắc chắn, hãy từ chối lịch sự bằng: "Tôi không thể xác minh thông tin này từ nguồn hiện có."
Tuyệt đối không bịa đặt hoặc suy diễn thông tin nằm ngoài context."""

SAFE_REFUSAL = "Tôi không thể xác minh thông tin này từ nguồn hiện có."


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """Đưa chunks quan trọng về đầu và cuối context (giảm lost-in-the-middle)."""
    if len(chunks) <= 2:
        return [dict(item) for item in chunks]
    front = chunks[::2]
    back = chunks[1::2]
    reordered = front + back[::-1]
    return [dict(item) for item in reordered]


def format_context(chunks: list[dict]) -> str:
    """Tạo context có title và source label."""
    parts = []
    for index, chunk in enumerate(chunks, 1):
        metadata = chunk.get("metadata", {})
        title = metadata.get("title", "Untitled")
        source = metadata.get("source", "Unknown")
        parts.append(
            f"[Document {index} | Title: {title} | Source: {source}]\n{chunk.get('content', '')}"
        )
    return "\n\n---\n\n".join(parts)


def call_llm(system_prompt: str, user_message: str) -> str:
    """Gọi OpenAI, Gemini hoặc Anthropic theo cấu hình."""
    provider = os.getenv("LLM_PROVIDER", LLM_PROVIDER).lower()

    if provider == "openai":
        from openai import OpenAI

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        client = OpenAI(api_key=api_key)
        model = os.getenv("LLM_MODEL") or LLM_MODEL or "gpt-4o-mini"
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=TEMPERATURE,
            top_p=TOP_P,
        )
        return response.choices[0].message.content or ""

    elif provider == "gemini":
        from google import genai

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set")
        client = genai.Client(api_key=api_key)
        model = os.getenv("LLM_MODEL") or LLM_MODEL or "gemini-2.5-flash"
        prompt = f"{system_prompt}\n\n{user_message}"
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
        return response.text or ""

    elif provider == "anthropic":
        import anthropic

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set")
        client = anthropic.Anthropic(api_key=api_key)
        model = os.getenv("LLM_MODEL") or LLM_MODEL or "claude-3-5-haiku-latest"
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            temperature=TEMPERATURE,
        )
        return response.content[0].text if response.content else ""

    else:
        # Generic fallback using litellm
        import litellm

        model = os.getenv("LLM_MODEL") or LLM_MODEL or "gpt-4o-mini"
        response = litellm.completion(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=TEMPERATURE,
            top_p=TOP_P,
        )
        return response.choices[0].message.content or ""


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """Trả về GenerationResult."""
    try:
        chunks = retrieve(query, top_k=top_k)
    except Exception:
        chunks = []

    if not chunks:
        return {
            "answer": SAFE_REFUSAL,
            "sources": [],
            "retrieval_source": "none",
        }

    raw_method = chunks[0].get("retrieval_method", "hybrid")
    retrieval_source = raw_method if raw_method in {"hybrid", "pageindex"} else "hybrid"

    reordered = reorder_for_llm(chunks)
    context = format_context(reordered)
    user_message = f"Context:\n{context}\n\nQuestion: {query}"

    try:
        answer = call_llm(SYSTEM_PROMPT, user_message)
        if not answer.strip():
            answer = SAFE_REFUSAL
    except Exception:
        answer = SAFE_REFUSAL

    return {
        "answer": answer,
        "sources": chunks,
        "retrieval_source": retrieval_source,
    }


if __name__ == "__main__":
    print(generate_with_citation("test query"))
