import os
from typing import TypedDict
from langgraph.graph import StateGraph, END
import google.genai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-pro")