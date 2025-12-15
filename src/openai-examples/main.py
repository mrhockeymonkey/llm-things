from openai import OpenAI
from dotenv import load_dotenv
import os 
import pprint

load_dotenv()


def main():
    client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"))

    models = client.models.list()

    # Filter for custom models (fine-tuned models typically start with "ft:")
    custom_models = [model for model in models.data]

    print(f"Found {len(custom_models)} custom model(s):\n")
    for model in custom_models:
        print(f"ID: {model.id}")
        print(f"Created: {model.created}")
        print(f"Owned by: {model.owned_by}")
        print("-" * 80)

    # If you want to see all models, uncomment below:
    # print("\nAll models:")
    # pprint.pprint(models)


if __name__ == "__main__":
    main()
