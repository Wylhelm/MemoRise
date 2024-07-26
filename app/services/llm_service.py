import requests
import json

LM_STUDIO_API_URL = "http://localhost:1234/v1/chat/completions"

def query_local_llm(prompt, max_tokens=100):
    """
    Send a query to the local LLM running in LM Studio.
    """
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens
    }

    try:
        response = requests.post(LM_STUDIO_API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.RequestException as e:
        print(f"Error querying LLM: {e}")
        return None

from datetime import datetime

def chat_with_memories(query, relevant_memories):
    """
    Generate a response to the user's query based on relevant memories.
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    context = "\n".join([
        f"Memory {i+1}:\n"
        f"Content: {memory.content}\n"
        f"Timestamp: {memory.timestamp}\n"
        f"Category: {memory.category}\n"
        f"Sentiment: {memory.sentiment}\n"
        f"Language: {memory.language}\n"
        f"Key Phrases: {', '.join(json.loads(memory.key_phrases) if isinstance(memory.key_phrases, str) else memory.key_phrases)}\n"
        f"Entities: {format_entities(memory.entities)}\n"
        for i, memory in enumerate(relevant_memories)
    ])

def format_entities(entities):
    if isinstance(entities, str):
        entities = json.loads(entities)
    if isinstance(entities, list):
        return ', '.join([f'{e[0]} ({e[1]})' if isinstance(e, (list, tuple)) and len(e) > 1 else str(e) for e in entities])
    return str(entities)
    prompt = f"Current date and time: {current_time}\n\n" \
             f"Based on the following memories:\n{context}\n\n" \
             f"User query: {query}\n\n" \
             f"Please consider the timestamps, categories, sentiments, languages, key phrases, " \
             f"and entities of the memories when formulating your response.\n\n" \
             f"Response:"
    
    return query_local_llm(prompt)
