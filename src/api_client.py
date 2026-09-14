import os
from dotenv import load_dotenv
import cohere
from huggingface_hub import InferenceClient

from cohere.errors import (
    UnauthorizedError,
    InvalidTokenError,
    ForbiddenError,
    TooManyRequestsError,
    GatewayTimeoutError,
    ServiceUnavailableError,
    InternalServerError,
)
from huggingface_hub.errors import HfHubHTTPError

load_dotenv()

AI_PROVIDER = os.getenv("AI_PROVIDER", "cohere").lower()

cohere_client =cohere.Client(os.getenv("COHERE_API_KEY"))
hf_client = InferenceClient(model= os.getenv("HF_MODEL") , token =os.getenv("HF_API_KEY"))

def get_ai_response(prompt: str) -> str:
    if AI_PROVIDER == "cohere":
        try:
            response = cohere_client.chat(message = prompt)
            return response.text.strip()
        except (UnauthorizedError, InvalidTokenError, ForbiddenError) as e:
            print("Auth error:", e)
            return "Sorry, there's an authentication issue. Please check the API key."
        except TooManyRequestsError as e:
            print("Rate limit error:", e)
            return "Sorry, too many requests right now. Please try again shortly."
        except (GatewayTimeoutError, ServiceUnavailableError, InternalServerError) as e:
            print("Provider/network error:", e)
            return "Sorry, I couldn't reach the AI service. Please try again."
        except Exception as e:
            print("Unexpected error:", e)
            return "Sorry, something went wrong while generating a response."

    elif AI_PROVIDER == "huggingface":
        try:
            response = hf_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=512,
            )
            return response.choices[0].message.content.strip()

        except HfHubHTTPError as e:
            status = e.response.status_code if e.response is not None else None

            if status == 401:
                print("Auth error:", e)
                return "Sorry, there's an authentication issue. Please check the API key."
            elif status == 429:
                print("Rate limit error:", e)
                return "Sorry, too many requests right now. Please try again shortly."
            elif status and status >= 500:
                print("Provider/network error:", e)
                return "Sorry, I couldn't reach the AI service. Please try again."
            else:
                print("Unexpected HF error:", e)
                return "Sorry, something went wrong while generating a response."

        except Exception as e:
            print("Unexpected error:", e)
            return "Sorry, something went wrong while generating a response."

    else:
        return f"Unknown AI_PROVIDER: {AI_PROVIDER}. Please set it to 'cohere' or 'huggingface'."

if __name__ == "__main__":
    print(get_ai_response("Say hello in one sentence."))

# testing the error handling by using an invalid API key

#bad_client = cohere.Client("this_is_not_a_real_key")
#bad_client.chat(message="hello")
#bad_hf_client = InferenceClient(
#    model=os.getenv("HF_MODEL"),
#    token="hf_" + "x" * 34   # correctly formatted, but not a real token
#)
#bad_hf_client.chat_completion(messages=[{"role": "user", "content": "hello"}])