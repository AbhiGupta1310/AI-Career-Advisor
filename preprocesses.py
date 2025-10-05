import requests
import os 
import json
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics.pairwise import cosine_similarity
def create_embedding(text_list):
    # https://github.com/ollama/ollama/blob/main/docs/api.md#generate-embeddings
    r = requests.post("http://localhost:11434/api/embed",
                json={"model":"bge-m3",
                        "input":text_list}
                )
    embedding = r.json()['embeddings']
    return embedding

jsons = os.listdir("merged_jsons") #List all the jsons 
jsons.sort()
# print(jsons)
my_dicts = []
chunk_id = 0
for json_file in jsons:
    with open(f"merged_jsons/{json_file}") as f:
        content = json.load(f)
    print('Creating embeddings for ',json_file)
    embeddings = create_embedding([c['text'] for c in content])
    for i,chunk in enumerate(content):
        chunk['chunk_id']  = chunk_id
        chunk['embedding'] = embeddings[i]
        chunk_id+=1
        my_dicts.append(chunk)

# print(my_dicts)

df  = pd.DataFrame.from_records(my_dicts)
# SAVE THE DATAFRAME
joblib.dump(df,'embeddings.joblib')



