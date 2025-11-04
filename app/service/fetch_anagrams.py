import requests

from app.service.llm_layer import generate_anagrams


def fetch_anagrams(word: str):
    result = generate_anagrams(word)

    return result


# print(fetch_anagrams('meat'))