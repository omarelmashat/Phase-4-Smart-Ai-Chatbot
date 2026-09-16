from src.api_client import get_ai_response
from src.prompts import build_prompt, add_to_history
from src.utils import (
    Colors,
    colorize,
    supports_color,
    print_banner,
    show_typing_indicator,
    clear_line,
)


EXIT_COMMAND = "exit"
COLOR_ENABLED = supports_color()


def validate_input(message: str) -> bool:
    return bool(message and message.strip())


def get_user_message() -> str:
    prompt = colorize("You: ", Colors.CYAN + Colors.BOLD, COLOR_ENABLED)
    return input(prompt).strip()


def generate_response(
    user_message: str,
    history: list
) -> str:
    prompt = build_prompt(user_message, history)
    return get_ai_response(prompt)


def display_response(response: str) -> None:
    label = colorize("AI:", Colors.GREEN + Colors.BOLD, COLOR_ENABLED)
    print(f"{label} {response}")


def run_chatbot() -> None:
    history = []

    print_banner("Smart AI Chatbot", "Type 'exit' to end the conversation")
    print()

    while True:
        user_message = get_user_message()

        if user_message.lower() == EXIT_COMMAND:
            print(colorize("AI: Goodbye! 👋", Colors.GREEN, COLOR_ENABLED))
            break

        if not validate_input(user_message):
            print(colorize("AI: Please enter a message.\n", Colors.YELLOW, COLOR_ENABLED))
            continue

        try:
            show_typing_indicator(COLOR_ENABLED)
            response = generate_response(
                user_message,
                history
            )
            clear_line()

            display_response(response)

            history = add_to_history(
                history,
                "user",
                user_message
            )

            history = add_to_history(
                history,
                "assistant",
                response
            )

        except Exception as error:
            clear_line()
            print(colorize(f"AI: Sorry, something went wrong: {error}", Colors.RED, COLOR_ENABLED))

        print()


if __name__ == "__main__":
    run_chatbot()
