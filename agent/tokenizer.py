import re

class Tokenizer:
    def __init__(self):
        self.number_map = {
            "zero": "0",
            "one": "1",
            "two": "2",
            "three": "3",
            "four": "4",
            "five": "5",
            "six": "6",
            "seven": "7",
            "eight": "8",
            "nine": "9",
            "ten": "10",
            "twenty": "20",
            "thirty": "30",
            "forty": "40",
            "fifty": "50",
            "hundred": "100"
        }

    def normalize(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def replace_number_words(self, text: str) -> str:
        words = text.split()
        converted = []
        for w in words:
            converted.append(self.number_map.get(w, w))
        return " ".join(converted)

    def tokenize(self, text: str) -> list[str]:
        text = self.normalize(text)
        text = self.replace_number_words(text)
        return text.split()
