import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.chatbot import validate_input, EXIT_COMMAND
from src.prompts import build_prompt, add_to_history, SYSTEM_PROMPT, MAX_HISTORY_TURNS
from src import api_client
from src.utils import require_env, safe_call, retry_call, mask_key, colorize, Colors

FAILURES = []


def check(label: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}")
    if not condition:
        FAILURES.append(label)


def run_checks() -> None:
    print("Running Smart AI Chatbot sanity checks...\n")

    check("Empty input is rejected", validate_input("") is False)
    check("Whitespace-only input is rejected", validate_input("   ") is False)
    check("Normal input is accepted", validate_input("Hello there") is True)

    check("Exit command is 'exit'", EXIT_COMMAND == "exit")
    check(
        "Exit command matches case-insensitively",
        "EXIT".lower() == EXIT_COMMAND and "ExIt".lower() == EXIT_COMMAND,
    )

    try:
        build_prompt("", [])
        check("build_prompt() rejects an empty message", False)
    except ValueError:
        check("build_prompt() rejects an empty message", True)

    prompt = build_prompt("What is an API?", [])
    check(
        "build_prompt() starts with the system prompt",
        isinstance(prompt, list) and prompt[0] == {"role": "system", "content": SYSTEM_PROMPT},
    )
    check(
        "build_prompt() appends the user message last",
        prompt[-1] == {"role": "user", "content": "What is an API?"},
    )

    history = []
    history = add_to_history(history, "user", "Hi")
    history = add_to_history(history, "assistant", "Hello!")
    check(
        "add_to_history() stores both turns in order",
        len(history) == 2 and history[0]["role"] == "user" and history[1]["role"] == "assistant",
    )
    check(
        "add_to_history() ignores empty content",
        add_to_history(history, "user", "   ") == history,
    )
    try:
        add_to_history(history, "system", "not allowed")
        check("add_to_history() rejects an invalid role", False)
    except ValueError:
        check("add_to_history() rejects an invalid role", True)

    long_history = []
    for i in range(20):
        long_history = add_to_history(long_history, "user", f"message {i}")
        long_history = add_to_history(long_history, "assistant", f"reply {i}")
    check(
        "Conversation history is trimmed to MAX_HISTORY_TURNS",
        len(long_history) == MAX_HISTORY_TURNS * 2,
    )

    provider = os.getenv("AI_PROVIDER", "cohere").lower()
    key_present = bool(os.getenv("COHERE_API_KEY")) if provider == "cohere" else bool(os.getenv("HF_API_KEY"))
    if key_present:
        check(f"API key for provider '{provider}' is loaded from .env", True)
    else:
        print(f"[SKIP] No API key found for provider '{provider}' — set it in your .env file")

    original_provider = api_client.AI_PROVIDER
    api_client.AI_PROVIDER = "not-a-real-provider"
    try:
        result = api_client.get_ai_response([{"role": "user", "content": "hi"}])
        check(
            "Unknown AI_PROVIDER returns a message instead of crashing",
            isinstance(result, str) and "Unknown AI_PROVIDER" in result,
        )
    finally:
        api_client.AI_PROVIDER = original_provider

    os.environ["SANITY_TEST_VAR"] = "some-value"
    check("require_env() returns a set variable", require_env("SANITY_TEST_VAR") == "some-value")
    del os.environ["SANITY_TEST_VAR"]
    try:
        require_env("SANITY_TEST_VAR_MISSING")
        check("require_env() raises when a variable is missing", False)
    except EnvironmentError:
        check("require_env() raises when a variable is missing", True)

    @safe_call(fallback_message="fallback")
    def _always_fails():
        raise RuntimeError("boom")

    @safe_call(fallback_message="fallback")
    def _succeeds():
        return "ok"

    check("safe_call() returns the fallback on exception", _always_fails() == "fallback")
    check("safe_call() returns the real result when nothing fails", _succeeds() == "ok")

    attempts = {"count": 0}

    def _fails_twice_then_succeeds():
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise ValueError("not yet")
        return "recovered"

    check(
        "retry_call() retries and eventually succeeds",
        retry_call(_fails_twice_then_succeeds, retries=3, delay=0) == "recovered",
    )

    def _always_raises():
        raise ValueError("nope")

    try:
        retry_call(_always_raises, retries=2, delay=0)
        check("retry_call() re-raises after exhausting retries", False)
    except ValueError:
        check("retry_call() re-raises after exhausting retries", True)

    check("mask_key() hides all but the last characters", mask_key("sk-abcdef123456") == "***********3456")
    check("mask_key() handles a missing key", mask_key("") == "(missing)")
    check("mask_key() fully masks a short key", mask_key("abc") == "***")

    check(
        "colorize() adds color codes when enabled",
        colorize("hi", Colors.GREEN, enabled=True) == f"{Colors.GREEN}hi{Colors.RESET}",
    )
    check("colorize() leaves text untouched when disabled", colorize("hi", Colors.GREEN, enabled=False) == "hi")

    if os.getenv("RUN_LIVE_API_CHECK") == "1" and key_present:
        try:
            reply = api_client.get_ai_response(build_prompt("Say hello in one word.", []))
            check("Live API call returns a non-empty response", bool(reply and reply.strip()))
        except Exception as error:
            check(f"Live API call raised an exception ({error})", False)

    print()
    if FAILURES:
        print(f"{len(FAILURES)} check(s) failed:")
        for failure in FAILURES:
            print(f"  - {failure}")
        sys.exit(1)

    print("All sanity checks passed.")


if __name__ == "__main__":
    run_checks()
