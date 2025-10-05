import json
import csv
import time
import google.generativeai as genai
API_KEY = "AIzaSyDD4vDYp3_1uheoLWMSC_SH5HItsaXuP64"   # 👈 Replace this with your key
genai.configure(api_key=API_KEY)
for m in genai.list_models():
    print(m.name)
