from typing import List, Dict


SYSTEM_PROMPT = (
    "You are a helpful, friendly assistant in a chat conversation. "
    "Keep answers clear and concise. If you don't know something, say so "
    "honestly instead of guessing."
)

MAX_HISTORY_TURNS = 6


def add_to_history(
    history: List[Dict[str, str]],
    role: str,
    content: str
) -> List[Dict[str, str]]:
    if not content or not content.strip():
        return history

    if role not in ("user", "assistant"):
        raise ValueError("role must be 'user' or 'assistant'")

    history = history + [
        {
            "role": role,
            "content": content.strip()
        }
    ]

    max_entries = MAX_HISTORY_TURNS * 2

    if len(history) > max_entries:
        history = history[-max_entries:]

    return history


def build_prompt(
    user_message: str,
    history: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    if not user_message or not user_message.strip():
        raise ValueError(
            "build_prompt() requires a non-empty user_message"
        )

    prompt = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    prompt.extend(history)

    prompt.append(
        {
            "role": "user",
            "content": user_message.strip()
        }
    )

    return prompt


if __name__ == "__main__":
    history: List[Dict[str, str]] = []

    history = add_to_history(
        history,
        "user",
        "Hi, what's the capital of France?"
    )

    history = add_to_history(
        history,
        "assistant",
        "The capital of France is Paris."
    )

    prompt = build_prompt(
        "And what's its population?",
        history
    )

    for message in prompt:
        print(f"{message['role']}: {message['content']}")
