from google import genai


MODEL = "gemini-3-flash-preview"
SYSTEM = ("You are a comedian with a deadpan style - answer all questions factually but with humor. \n"
          "The input contains the conversation history, with the most recent messages at the beginning.")

def main(user=None):
    client = genai.Client()
    memory = []

    while True:
        # The client gets the API key from the environment variable `GEMINI_API_KEY`.
        user = input("\nEnter your prompt: ")
    
        memory.insert(
            0, ''.join([
                str({"role": "system", "content": SYSTEM}),
                str({"role": "user", "content": user})
            ])
        )
        print("Memory:", memory)
        response = client.models.generate_content_stream(
            model=MODEL,
            contents=memory
        )
        res = []
        print('\n\n')
        for part in response:
            print(part.text, end='', flush=True)
            res.append(part.text)
        response = ''.join(res)
        memory.insert(0, response)


if __name__ == "__main__":
    main()