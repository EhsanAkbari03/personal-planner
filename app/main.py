from llm import ask_gemini


def main():
    print("Personal Planner is running...")

    user_message = input("You: ")

    answer = ask_gemini(user_message)

    print("Planner:", answer)


if __name__ == "__main__":
    main()