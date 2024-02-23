from google.generativeai import GenerationConfig
import google.generativeai as genai

model = genai.GenerativeModel('gemini-pro')

generation_config = GenerationConfig(candidate_count=1, max_output_tokens=50)

api_key = input("Enter your API key: ")
genai.configure(api_key=api_key)


response = model.generate_content("Respond to this prompt with 1.", generation_config=generation_config)

if hasattr(response, 'text'):
    print(response.text)
