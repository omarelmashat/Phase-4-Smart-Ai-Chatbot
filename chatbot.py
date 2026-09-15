from src.api_client import get_ai_response
from src.prompts import build_prompt, add_to_history


EXIT_COMMAND = "exit"


def validate_input(message: str) -> bool:
    """Check whether the user entered a valid message."""
    return bool(message and message.strip())


def get_user_message() -> str:
    """Receive a message from the user."""
    return input("You: ").strip()


def generate_response(
    user_message: str,
    history: list
) -> str:
    """Build the prompt and get a response from the AI."""
    prompt = build_prompt(user_message, history)
    return get_ai_response(prompt)


def display_response(response: str) -> None:
    """Display the AI response."""
    print(f"AI: {response}")


def run_chatbot() -> None:
    """Run the main chatbot conversation loop."""
    history = []

    print("=" * 40)
    print("      Smart AI Chatbot")
    print("=" * 40)
    print("Type 'exit' to end the conversation.\n")

    while True:
        user_message = get_user_message()

        # Check exit command
        if user_message.lower() == EXIT_COMMAND:
            print("AI: Goodbye! 👋")
            break

        # Reject empty messages
        if not validate_input(user_message):
            print("AI: Please enter a message.\n")
            continue

        try:
            # Generate AI response
            response = generate_response(
                user_message,
                history
            )

            # Display response
            display_response(response)

            # Save both sides of the conversation
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
            print(f"AI: Sorry, something went wrong: {error}")

        print()


if __name__ == "__main__":
    run_chatbot()
    
