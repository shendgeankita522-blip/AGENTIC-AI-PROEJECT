import os

load_dotenv()

print("API KEY LOADED:", bool(os.getenv("GROQ_API_KEY")))