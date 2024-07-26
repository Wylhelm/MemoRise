import requests

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

def chat_with_memories(query, relevant_memories):
    """
    Generate a response to the user's query based on relevant memories.
    """
    context = "\n".join([f"Memory {i+1}: {memory.content}" for i, memory in enumerate(relevant_memories)])
    prompt = f"Based on the following memories:\n{context}\n\nUser query: {query}\n\nResponse:"
    
    return query_local_llm(prompt)
