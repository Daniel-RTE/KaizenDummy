from flask import Flask, render_template, request, jsonify
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
import os

app = Flask(__name__)

# Azure OpenAI config
endpoint = "https://u4cs-llm-kaizen.openai.azure.com/"
deployment = "gpt-4o-mini"
subscription_key = "4iQxBaBOsAFz81RtNuxf3GlOk16MVdJHiiSuWzjuZmVxOMzxzOBAJQQJ99BCACfhMk5XJ3w3AAAAACOGTVgr"
api_version = "2024-12-01-preview"

# Azure Cognitive Search config
search_service_name = "u4cs-llmpilot-search-basic-01" 
search_index_name = "edbokonomi310325" 
search_key = "RaXq8JiYbQwdHlI7tDfDMoNYaXwMF8ZrqKMyG3WnroAzSeCluKjh"  

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

# Create Azure Search client
search_client = SearchClient(
    endpoint=f"https://{search_service_name}.search.windows.net",
    index_name=search_index_name,
    credential=AzureKeyCredential(search_key)
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    
    # First search for relevant documents
    search_results = search_azure_index(user_message)
    
    # Create the system message with context
    system_message = """
    You are a helpful assistant. Use the following context to help answer the user's question.
    If you don't know the answer, just say you don't know. Don't try to make up an answer.
    
    Context:
    {context}
    """.format(context="\n".join([result['content'] for result in search_results]))
    
    # Generate response with context
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
        max_tokens=4096,
        temperature=0.7,  # Lower temperature for more factual responses
        top_p=0.9,
        model=deployment
    )

    assistant_reply = response.choices[0].message.content
    return jsonify({'reply': assistant_reply})

def search_azure_index(query, top=3):
    try:
        results = search_client.search(
            search_text=query,
            top=top
        )
        return [dict(result) for result in results]
    except Exception as e:
        print(f"Error searching Azure index: {e}")
        return []

if __name__ == '__main__':
    app.run(debug=True)