import pandas as pd
import re
import html
from bs4 import BeautifulSoup


def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = BeautifulSoup(text, "html.parser").get_text(" ")
    text = html.unescape(text)
    text = re.sub(r"[^A-Za-zÀ-ÖØ-öø-ÿ0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text