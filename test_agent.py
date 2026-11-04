from src.agent import run_agent
from uuid import uuid4

# Create one conversation ID for this entire session
conversation_id = str(uuid4())

print("\n========== VERA CLI ==========")
print("Conversation memory test")
print("Type 'exit' to stop.")
print("Type 'new' to start a fresh conversation.")
print("==============================\n")

while True:
    user_input = input("You: ").strip()

    if user_input.lower() == "exit":
        print("VERA: Goodbye!")
        break

    if user_input.lower() == "new":
        conversation_id = str(uuid4())
        print("\nVERA: Started a new conversation.\n")
        continue

    if not user_input:
        continue

    try:
        response = run_agent(
            user_input,
            conversation_id=conversation_id
        )

        print(f"\nVERA: {response}\n")

    except Exception as e:
        print(f"\nError: {e}\n")