from ollama import chat


response = chat(
    model="llama3.1",
    messages=[
        {
            "role": "user",
            "content": "راجب برنامه نویسی پایتون و کاربردهای آن توضیح بده"
        }
    ]
)

print(response.message.content)
