
from src.groq_client import ask_groq

question = (
    "Hello VERA. Explain in two sentences how you can help "
    "me manage tasks on my computer."
)

try:
    answer = ask_groq(question)

    print("\nVERA:")
    print(answer)

except Exception as error:
    print("\nGroq connection failed:")
    print(error)
