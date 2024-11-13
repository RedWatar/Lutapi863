from groq import Groq

client = Groq(api_key='your_api_key_here')

# Upload file (hypothetical)
file_url = client.files.upload(input("Which file do u plan on uplodaing? "))

completion = client.chat.completions.create(
    model="llama-3.1-70b-versatile",
    messages=[
        {
            "role": "system",
            "content": f"Generate insights based on the file available at {file_url}."
        },
        {
            "role": "user",
            "content": f"Here is the file URL: {file_url}"
        }
    ],
    temperature=1,
    max_tokens=1024,
    top_p=1,
    stream=True,
    stop=None,
)

for chunk in completion:
    print(chunk.choices[0].delta.content or "", end="")
