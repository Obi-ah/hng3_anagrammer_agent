# from google import genai
# import google.generativeai as genai
import google.generativeai as genai

import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)


def generate_anagrams(word: str):

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(
            contents=f"Generate upper-case anagrams of the word - {word}. For example - if the word is 'cat', return 'CAT,ACT'"
                     f"ONLY RETURN VALID ENGLISH WORDS"
                     f"if there are no valid anagrams simply generate 'No Valid Anagrams Found for {word}'"
        )

        result = response.text

        return result

    except Exception as e:
        print(f"An error occurred: {e}")



# print(generate_anagrams('earth'))