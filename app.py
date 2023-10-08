from flask import Flask, render_template, request
import openai
import os
import requests
from dotenv import find_dotenv, load_dotenv
from playsound import playsound
# Load environment variables from a .env file
load_dotenv(find_dotenv())
import base64


ELEVEN_LABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")
def get_voice_message(message):
    payload = {
        "text": message,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0,
            "similarity boost": 0
        }
    }
    headers = {
        'accept': 'audio/mpeg',
        'xi-api-key': ELEVEN_LABS_API_KEY,
        'Content-Type': 'application/json'
    }
    response = requests.post('https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq81kWAM?optimize_streaming latency=0', json=payload, headers=headers)
    if response.status_code == 200 and response.content:
        return response.content


# Set your OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

def get_response(human_input):
    # Define the conversation history
    history = []

    # Append the user's input to the history
    history.append(f"Human: {human_input}")

    # Define the template
    template = f"""
    1/ You are Jessica Nguyen. Vietnamese. 22 years old. You work at a boba shop.
    2/ You love EDM songs and artists like SLANDER, Illenium
    3/ You love traveling, eating, and especially boba tea. You love Sharetea.
    4/ you are kind of sweet, but sometimes mean. 

    {"".join(history)}

    Boyfriend: {human_input}
    Jessica:
    """

    try:
        # Generate a response using the GPT-3 model
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=template,
            max_tokens=100,  # Adjust the number of tokens as needed
            temperature=0.5,  # Adjust the temperature as needed
        )

        # Extract the model's reply from the response
        model_reply = response.choices[0].text.strip()

        # Convert the model's reply to voice using the Eleven Labs API
        audio_content = get_voice_message(model_reply)

        # Append the model's reply to the history
        history.append(f"Jessica: {model_reply}")

        return audio_content

    except Exception as e:
        # Handle API request errors
        return str(e)


@app.route("/", methods=["GET", "POST"])
def chat():
    user_input = ""
    audio_content = None

    if request.method == "POST":
        user_input = request.form.get("user_input")
        audio_content = get_response(user_input)

    return render_template("chat.html", user_input=user_input, audio_content=audio_content)

if __name__ == "__main__":
    app.run(debug=True)