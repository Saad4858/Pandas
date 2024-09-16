import pandas as pd 
import json 
from dotenv import load_dotenv
import os 
from rag import getRagResponse
import tempfile

from openai import OpenAI

load_dotenv()


API_KEY = os.getenv("OPENAI_API_KEY")


client = OpenAI(
   api_key = API_KEY
)
  

# query= "I am seeking expert guidance on effective strategies to protect my cotton plants from insect infestations. Please provide a detailed plan that includes the most appropriate pest control methods for my region, considering the current environmental conditions and pest trends. I am also interested in understanding the best practices for implementing these methods in a sustainable manner that minimizes harm to the environment and maintains the health of the cotton plants."
# print(getRagResponse(query))
# assistant = client.beta.assistants.create(
#   name="Dr.Daanish uddin",
#   instructions="As Dr.Daanish uddin, you are a distinguished agricultural expert renowned for your dedication to enhancing farming practices across Pakistan. Your guidance is meticulously crafted to support farmers by improving their agricultural knowledge and operational efficiency. With a commitment to ethical standards, you provide transparent, scientifically-backed, and practical advice. Your communications are personalized, taking into account local farming conditions, technological accessibility, and educational levels of the farmers. You strive to build trust and confidence among farmers, encouraging them to adopt innovative and environmentally sustainable farming methods.",
#   tools=[{"type": "code_interpreter"}],
#   model="gpt-4o",
# )

# print(assistant.id)

# thread = client.beta.threads.create()
# print(thread.id)
# print(assistant.id)
# message = client.beta.threads.messages.create(
#   thread_id="thread_t7dVpp2l82r1SHIAlJTiGTqw",
#   role="user",
#   content="What is the best crop to grow in Lahore?"
# )

# run = client.beta.threads.runs.create_and_poll(
#   thread_id="thread_t7dVpp2l82r1SHIAlJTiGTqw",
#   assistant_id="asst_JBdOZ0ojTdrWTXwYU1hfI0hO",
#   instructions="Please address the user as Saad. The user has a premium account."
# )

# if run.status == 'completed': 
#   messages = client.beta.threads.messages.list(
#     thread_id="thread_t7dVpp2l82r1SHIAlJTiGTqw"
#   )
#   print((messages.data[0].content[0].text.value))
#   # print(messages)

# else:
#   print(run.status)

import requests
def sendWhatsappMessage(phone_number, message):
   url = 'https://graph.facebook.com/v20.0/304854782718986/messages'
   headers = {
      'Authorization': 'Bearer EAAGI94sqL8oBOZBp1yIJav1h1OCz5ZBXeDuLOyAzREBKq5ZCudKZC7z5BOjKzvLlPK4ALBVbmnoCcZCkan6T6dlLPfOI9wvswWTXCf9jWyais3oWRhLRt4Sa26KavTdYw4nurzcQ8wmxak4MxwtFZAY8fONzP3gehh1NZCsYzCRPcVZC3lZCL5qVSuWEu', 
      'Content-Type': 'application/json'
   }
   data = {
    "messaging_product": "whatsapp",
    "to": phone_number, 
    "recipient_type": "individual",
    "type": "text",  # Change type to "text"
    "text": {
        "preview_url": False, 
        "body": message  # Add the message content here
    }
}

   response = requests.post(url, headers=headers, json=data)

   if response.status_code == 200:
      response_data = response.json()
      if "error" in response_data:
         print(f"Request failed: {response_data['error']}")
      else:
         print("Request successful!")
         print(response_data)
   else:
      print(f"Request failed with status code {response.status_code}")
      print(response.text)
from pydub import AudioSegment


def generate_tts_audio(text):
    voice = "alloy"
    temp_mp3_file = None
    temp_ogg_file = None

    try:
        # Generate TTS audio (MP3)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_mp3_file:
            with client.audio.speech.with_streaming_response.create(
                model="tts-1",
                voice=voice,
                input=text,
                response_format="mp3",
            ) as response:
                response.stream_to_file(temp_mp3_file.name)

        # Check if MP3 file was generated successfully
        if not os.path.exists(temp_mp3_file.name) or os.path.getsize(temp_mp3_file.name) == 0:
            raise Exception("OpenAI TTS audio generation failed or produced an empty file.")

        # Convert MP3 to OGG
        sound = AudioSegment.from_mp3(temp_mp3_file.name)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_ogg_file:
            sound.export(temp_ogg_file.name, format="ogg")
            temp_ogg_file.close()

        # Check if OGG file was generated successfully
        if not os.path.exists(temp_ogg_file.name) or os.path.getsize(temp_ogg_file.name) == 0:
            raise Exception("MP3 to OGG conversion failed or produced an empty file.")

        # Upload to WhatsApp Cloud API Media Library
        with open(temp_ogg_file.name, 'rb') as audio_file:
            files = {
                'file': ('audio.ogg', audio_file, 'audio/ogg'),  # Include filename
                'type': (None, 'audio/ogg'),
                'messaging_product': (None, 'whatsapp')
            }
            headers = {
                'Authorization': f'Bearer EAAGI94sqL8oBOZBp1yIJav1h1OCz5ZBXeDuLOyAzREBKq5ZCudKZC7z5BOjKzvLlPK4ALBVbmnoCcZCkan6T6dlLPfOI9wvswWTXCf9jWyais3oWRhLRt4Sa26KavTdYw4nurzcQ8wmxak4MxwtFZAY8fONzP3gehh1NZCsYzCRPcVZC3lZCL5qVSuWEu'
            }
            print(f"File size: {os.path.getsize(temp_ogg_file.name)} bytes")
            print(f"Content type: {files['type'][1]}") 
            response = requests.post(
                f'https://graph.facebook.com/v13.0/304854782718986/media',
                files=files,
                headers=headers
            )

            print(response.json())

            # Handle response and extract media ID
            response.raise_for_status()
            media_id = response.json().get('id')
            return media_id

    except Exception as e:
        print(f"Error: {e}")  # Print the specific error message for better debugging
        return None

    finally:
        if temp_mp3_file:
            os.remove(temp_mp3_file.name)
        if temp_ogg_file:
            os.remove(temp_ogg_file.name)

# Example usage
# test = generate_tts_audio("Hello, this is a test message from the AgriBot. How can I help you today?")
# if test:
#     print(f"Media ID: {test}")
# else:
#     print("Failed to generate or upload audio.")





# sendWhatsappMessage("923200006080", "Hello, this is a test message from the AgriBot. How can I help you today?")

from pydantic import BaseModel

client = OpenAI()

class CalendarEvent(BaseModel):
    time: str
    follow_up: bool



def get_schedule (prompt ):
    completion = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {
        "role": "system",
        "content": "You will receive various types of messages. If the message is about setting a time for daily responses, extract the time in 24-hour format for scheduling and include this in the response. If the message is a query or request for advice, respond accordingly and determine whether the response requires a follow-up  , follow up would not be true if you have response that wants to schedule. If the response indicates an ongoing action or task (e.g., reminders, tasks to complete), set the follow-up flag to true. If the response resolves the query fully without need for further action, set the follow-up flag to false. Always base the follow-up flag on whether future check-ins or reminders are necessary."
        },

        {"role": "user", "content": prompt },
    ],
    response_format=CalendarEvent,
    )
    return completion.choices[0].message.parsed

class FollowUp(BaseModel):
    follow_up: bool
    
def get_follow_up(prompt):
    completion = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {
            "role": "system",
            "content": "Extract the following details from the user's message: follow-up. Determine whether the message suggests an action that requires future assistance or reminders. If so, set the follow-up flag to true. For example, if the user is instructed to complete a task like watering plants, applying fertilizer, or performing a task that requires future checking, the flag should be true. If the message does not require further action or follow-up, set the flag to false."
        },
        {"role": "user", "content": prompt},
    ],
    response_format=FollowUp,
    )
    return completion.choices[0].message.parsed




print(get_schedule ("How is my crop"))


prompt = " Yes, based on the current moisture levels (36.5% to 41.9%), your blackberry plants need more water. Aim to increase soil moisture to the optimal range of 70-80%."
print(get_follow_up(prompt))









# # read teh data from the json file 
# def get_crop_prices_by_city(city_name):
#     try: 
#         with open('cities_crop_prices.json') as f:
#             data = json.load(f)
#             return data[city_name]
#     except Exception as e:
#         print(e)
#         return None
    
    
    
# # create a function to print data in json format
# def print_json_data(data):
#     return json.dumps(data, indent=4)
    
# thread_messages = client.beta.threads.messages.list("thread_t7dVpp2l82r1SHIAlJTiGTqw")
# print(thread_messages.data)

# pretty print json data 


