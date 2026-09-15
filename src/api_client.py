import os
from dotenv import load_dotenv
import cohere
from huggingface_hub import InferenceClient

load_dotenv()

AI_PROVIDER = os.getenv("AI_PROVIDER", "cohere").lower()

COHERE_MODEL = os.getenv(
    "COHERE_MODEL",
    "command-a-03-2025"
)

cohere_client = cohere.ClientV2(
    api_key=os.getenv("COHERE_API_KEY")
)

hf_client = InferenceClient(
    model=os.getenv("HF_MODEL"),
    token=os.getenv("HF_API_KEY")
)


def get_ai_response(prompt: list[dict[str, str]]) -> str:

    if AI_PROVIDER == "cohere":
        try:
            response = cohere_client.chat(
                model=COHERE_MODEL,
                messages=prompt
            )

            return response.message.content[0].text.strip()

        except Exception as error:
            print("Cohere error:", error)
            return "Sorry, something went wrong while generating a response."

    elif AI_PROVIDER == "huggingface":
        try:
            response = hf_client.chat_completion(
                messages=prompt,
                max_tokens=512
            )

            return response.choices[0].message.content.strip()

        except Exception as error:
            print("Hugging Face error:", error)
            return "Sorry, something went wrong while generating a response."

    else:
        return (
            f"Unknown AI_PROVIDER: {AI_PROVIDER}. "
            "Please set it to 'cohere' or 'huggingface'."
        )
