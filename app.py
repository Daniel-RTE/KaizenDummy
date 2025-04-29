from flask import Flask, render_template, request, jsonify
from openai import AzureOpenAI

app = Flask(__name__)

# Azure OpenAI config
endpoint = "https://u4cs-llm-kaizen.openai.azure.com/"
deployment = "gpt-4o-mini"
subscription_key = "4iQxBaBOsAFz81RtNuxf3GlOk16MVdJHiiSuWzjuZmVxOMzxzOBAJQQJ99BCACfhMk5XJ3w3AAAAACOGTVgr"
api_version = "2024-12-01-preview"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_message},
        ],
        max_tokens=4096,
        temperature=1.0,
        top_p=1.0,
        model=deployment
    )

    assistant_reply = response.choices[0].message.content
    return jsonify({'reply': assistant_reply})


if __name__ == '__main__':
    app.run(debug=True)
