from fastapi import FastAPI , Request
import os 
from dotenv import load_dotenv
import openai
import requests
from db_controllers import addReadingRecord, addUser, get10ReadingRecords, getLanguage, addConversation, getThreadID, get10ReadingRecordsID

from weather_api import get_current_weather_data , get_forecast
import tempfile

from rag_query_template import get_rag_query
from datetime import datetime
from pydub import AudioSegment
from helpers import get_schedule, get_follow_up

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")


from rag import agent

    
OPENAI_CLIENT = openai.OpenAI(
    api_key=API_KEY,
)



app = FastAPI()

@app.get("/")
async def root():
    print("Hello World ")
    return {"message": "Hello World"}


@app.post('/transcribeAudio')
async def transcribe_audio(request: Request):
    audio_content = await request.body()
    try:
        # print("Audio Content:",audio_content)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
            temp_audio_file.write(audio_content)
            temp_audio_file_path = temp_audio_file.name
        
            print(f"Temporary audio file path: {temp_audio_file_path}") 

        transcript_text = None
        with open(temp_audio_file_path, 'rb') as audio_file:
            transcription = OPENAI_CLIENT.audio.transcriptions.create(
                            model="whisper-1", 
                            file=audio_file
            )

            transcript_text = transcription.text 
            print("Transcript:", transcript_text)  
            
    except Exception as e:
        print(f"Error during transcription: {e}")  
    finally:
        os.remove(temp_audio_file_path)  
    
    
    return {
        "transcript": transcript_text
    }

@app.get('/translatedResponseUser')
async def get_translated_response(user_prompt: str , language: str, phone: str):
    try:

        # thread_id, user_id = getThreadID(phone)
        user_id = 1

        language = getLanguage(user_id)
        print("User Prompt : ", user_prompt)
        thread_id = "thread_Hq7Rk8o86gUmd2sML0o7ra5Q"

        # print(f"Thread: {thread_id}")
        # print(f"User id: {user_id}")

        records = ""

        # Temporary For LUMS Farm Situation (Shared Sensor Data but Separate Users)
        if (user_id == 1):
            records = get10ReadingRecords()
        else:
            records = get10ReadingRecordsID(user_id)

        # records = get10ReadingRecords()

        formatted_records = []

        for record in records:
            formatted_record = (
                f"ID: {record['id']}, "
                f"User ID: {record['user_id']}, "
                f"pH: {record['pH']} pH, "
                f"Nitrogen: {record['nitrogen']} mg/kg, "
                f"Phosphorus: {record['phosphorus']} mg/kg, "
                f"Potassium: {record['potassium']} mg/kg, "
                f"Temperature: {record['temperature']} ℃, "
                f"Moisture: {record['moisture']}%, "
                f"Conductivity: {record['conductivity']} us/cm, "
                f"Battery: {record['battery']}%, "
                f"Created At: {record['created_at']}, "
                f"Updated At: {record['updated_at']}"
            )
            formatted_records.append(formatted_record)

        final_records = "\n".join(formatted_records)


        current_weather_data = get_current_weather_data("Lahore")

        forecast , six_hour_forecast = get_forecast("Lahore",3)

        current_date = datetime.now().date()
        # print(f"Current Date: {current_date}")

        # context = "Context of the user's farmland"
        # context  = context +"\n"+"Considering the weather conditions \n" + current_weather_data
        # context = context + "\n" + six_hour_forecast

        translated_user_prompt = user_prompt
        # print(f"Context: {context}")
        if language != "English":
            completion_response = OPENAI_CLIENT.chat.completions.create(
                model = 'gpt-4o',
                messages=[
                    {"role": "system", "content": f"Please translate the following message to English. Do not make any changes to the message itself. If it is already in english, return the message exactly as it was received"},
                    {"role": "user", "content": f"{user_prompt}"}
                ]
            )

            translated_user_prompt = completion_response.choices[0].message.content
            print(f"Translated User Prompt: {translated_user_prompt}")

        # rag_query = get_rag_query(translated_user_prompt)

        schedule = get_schedule(translated_user_prompt)
        time = schedule.time
        if time != '':
            # this is where we will add the reminder to the user's calendar
            resp = "I have added a reminder to your calendar for " + time
            return { 'user_prompt': f'{user_prompt}',
                 'original_response': f'{resp}',
                 'context' : f'{""}',
                 'IOT Rows': f'{records}'
                 }

        


        rag_prompt = ""

        if (user_id == 3):
            rag_prompt = rag_prompt + "For Blackberries: \n" + translated_user_prompt
        else:
            rag_prompt = translated_user_prompt
        

        rag_info = agent.query(str(rag_prompt)) # Temporary For Now

        context = "\n" + str(rag_info) + "\n"  
        profile = "" 

        if (user_id == 3):
            profile ="A meticulous and detail-oriented individual, she holds a PhD in Computer Science with a specialization in Human-Computer Interaction. She is an instructor at a prestigious university and applies her rigorous academic mindset to her home farming activities. Growing blackberries in DHA, Lahore, Punjab, Pakistan, she dedicates daily attention to her crop, striving for the highest quality. Her interest in innovative techniques aligns with her commitment to successful and sustainable farming practices. Given her preference for efficiency, she values concise, 2-3 line responses from a chatbot to quickly address her queries and needs. She specifically seeks brief but actionable advice that she can put into practice, ensuring her time is used effectively"

        if (user_id == 1):
            profile ="A meticulous and detail-oriented individual, she holds a PhD in Computer Science with a specialization in Human-Computer Interaction. She is an instructor at a prestigious university and applies her rigorous academic mindset to her home farming activities. Growing blackberries in DHA, Lahore, Punjab, Pakistan, she dedicates daily attention to her crop, striving for the highest quality. Her interest in innovative techniques aligns with her commitment to successful and sustainable farming practices. Given her preference for efficiency, she values concise, 2-3 line responses from a chatbot to quickly address her queries and needs. She specifically seeks brief but actionable advice that she can put into practice, ensuring her time is used effectively"

        if (user_id == 2):
            profile ="Prepare a message for a 45-year-old female from a low socio-economic background, farming 5 acres with a focus on maize and rice. Optimize her traditional farming and tube well irrigation practices while improving manual pest control methods. Given her primary education and basic mobile phone usage, ensure the advice is straightforward and practical. Use simple Urdu text messages to communicate ways to enhance soil fertility and manage water efficiently. Highlight strategies to combat frequent floods and limited access to chemical fertilizers. Motivate her to explore drip irrigation given her interest in modern techniques, and clarify the importance of pH balance and soil nutrients for better crop health"

        message = OPENAI_CLIENT.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=f"{user_prompt}"
        )

        run = OPENAI_CLIENT.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id="asst_7NBRXiK2PDPyrSzwHi73LkNX",
        instructions=f"You are a helpful assistant who has great knowledge of agriculture. You answer in simple language with no markdown. Provide Natural language responses with no markdown. Keep your answers short, to the point and to a maximum of two to three sentences. Do not mention technical details in your answer. The date today is {current_date}.\nUser profile: {profile}.\nThe user's farmland has the following record: {str(final_records)} and the following is additional information: {context}.\nThe current weather situation is as follows: {current_weather_data}. The forecast for the next week in 6 hours intervals is as follows: {six_hour_forecast}."
        )
        response = ""
        if run.status == 'completed': 
            messages = OPENAI_CLIENT.beta.threads.messages.list(
            thread_id=thread_id
        )
            print(messages.data[0].content[0].text.value)
            response = (messages.data[0].content[0].text.value)
            
            addConversation(user_id, user_prompt, response)
        # print(messages)
        else:
            print(run.status)
            return { 'user_prompt': 'No response from the assistant',
                 'original_response': 'No response from the assistant',
                 'context' : 'No response from the assistant',
                 'IOT Rows': 'No response from the assistant'
                 }

        
        print(f"Users Language: {language}")
        if language == "English":
            return { 'user_prompt': f'{user_prompt}',
                 'original_response': f'{response}',
                 'context' : f'{context}',
                 'IOT Rows': f'{records}'
                 }

        completion_response = OPENAI_CLIENT.chat.completions.create(
            model = 'gpt-4o',
            messages=[
                {"role": "system", "content": f"Please translate the following message to {language} for the user. Do not make any changes to the message itself."},
                {"role": "user", "content": f"{response}"}
            ]
        )

        translated_response = completion_response.choices[0].message.content
        
        return { 'user_prompt': f'{user_prompt}',
                 'original_response': f'{translated_response}',
                 'context' : f'{context}',
                 'IOT Rows': f'{records}'
                 }
    
    except Exception as e:
        print(e)
        return {'message':'failure getting latest message'}
      
@app.get('/getAudioResponse')
async def generate_tts_audio(text:str):
    voice = "alloy"
    temp_mp3_file = None
    temp_ogg_file = None

    try:
        # Generate TTS audio (MP3)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_mp3_file:
            with OPENAI_CLIENT.audio.speech.with_streaming_response.create(
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

@app.post('/addReadingRecord')
async def add_reading_record(pH: float, nitrogen: float, phosphorous: float, potassium: float, temperature: float, moisture: float, conductivity: float, battery: float, user_id: int):
    try:
        addReadingRecord(pH, nitrogen, phosphorous, potassium, temperature, moisture, conductivity, battery, user_id)
        return {'message':'success'}
    except Exception as e:
        print(e)
        return {'message':'failure adding reading record'}



