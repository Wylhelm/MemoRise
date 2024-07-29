import requests
import json

LM_STUDIO_API_URL = "http://localhost:1234/v1/chat/completions"

def query_local_llm(prompt):
    """
    Send a query to the local LLM running in LM Studio.
    """
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4096  # Set a high value to get the full response
    }

    try:
        response = requests.post(LM_STUDIO_API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.RequestException as e:
        print(f"Error querying LLM: {e}")
        return None

from datetime import datetime

def chat_with_memories(query, relevant_memories, chat_history):
    """
    Generate a response to the user's query based on relevant memories and chat history.
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    context = "\n".join([
        f"Memory ID: {memory.id}\n"
        f"Content: {memory.content}\n"
        f"Timestamp: {memory.timestamp}\n"
        f"Category: {memory.category}\n"
        f"Sentiment: {memory.sentiment}\n"
        f"Language: {memory.language}\n"
        f"Key Phrases: {', '.join(json.loads(memory.key_phrases) if isinstance(memory.key_phrases, str) else memory.key_phrases)}\n"
        f"Entities: {format_entities(memory.entities)}\n"
        for memory in relevant_memories
    ])

    chat_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])

    prompt = f"Current date and time: {current_time}\n\n" \
             f"Based on the following memories:\n{context}\n\n" \
             f"Previous conversation:\n{chat_context}\n\n" \
             f"User query: {query}\n\n" \
             f"Please consider the timestamps, categories, sentiments, languages, key phrases, " \
             f"and entities of the memories, as well as the previous conversation, when formulating your response.\n\n" \
             f"Response:"
    
    return query_local_llm_stream(prompt)

def query_local_llm_stream(prompt):
    """
    Send a query to the local LLM running in LM Studio and stream the response.
    """
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4096,
        "stream": True
    }

    try:
        response = requests.post(LM_STUDIO_API_URL, headers=headers, json=data, stream=True)
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                json_object = json.loads(line.decode('utf-8').split('data: ')[1])
                if 'choices' in json_object and len(json_object['choices']) > 0:
                    content = json_object['choices'][0]['delta'].get('content', '')
                    if content:
                        yield content
    except requests.RequestException as e:
        print(f"Error querying LLM: {e}")
        yield "Error: Unable to generate response."

def format_entities(entities):
    if isinstance(entities, str):
        entities = json.loads(entities)
    if isinstance(entities, list):
        return ', '.join([f'{e[0]} ({e[1]})' if isinstance(e, (list, tuple)) and len(e) > 1 else str(e) for e in entities])
    return str(entities)
