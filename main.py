from fastapi import FastAPI , Request
import os 
from dotenv import load_dotenv
import openai
import requests
from db_controllers import addReadingRecord, addUser, get10ReadingRecords, getLanguage, addConversation, getThreadID, get10ReadingRecordsID , updateUserTime , getUserDetails, addConversationWithTranslation

from weather_api import get_current_weather_data , get_forecast
import tempfile

from rag_query_template import get_rag_query
from datetime import datetime
from pydub import AudioSegment
from helpers import get_schedule, get_follow_up
import subprocess


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

        thread_id,assistant_id, user_id  = getThreadID(phone)
        print(f"Thread: {thread_id} Assistant: {assistant_id} User: {user_id}")

        language = getLanguage(user_id)

        records = ""

        records = get10ReadingRecords()

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

        translated_user_prompt = user_prompt
      
        if language != "English":
            completion_response = OPENAI_CLIENT.chat.completions.create(
                model = 'gpt-4o',
                messages=[
                    {"role": "system", "content": f"Please translate the following message to English. Do not make any changes to the message itself, do not remove or add anything else to your translation. Provide only the translation. If it is already in english, return the message exactly as it was received."},
                    {"role": "user", "content": f"{user_prompt}"}
                ]
            )

            translated_user_prompt = completion_response.choices[0].message.content


        schedule = get_schedule(translated_user_prompt)
        time = schedule.time

        if time != '':
            # this is where we will add the reminder to the user's calendar

            resp = "I have added a reminder to your calendar for " + time
            updateUserTime(user_id, time)

            return { 'user_prompt': f'{user_prompt}',
                 'original_response': f'{resp}',
                 'context' : f'{""}',
                 'IOT Rows': f'{records}'
                 }

        
        completion_response = OPENAI_CLIENT.chat.completions.create(
            model = 'gpt-4o',
            messages=[
                {"role": "system", "content": f"Your task is to rewrite user-provided queries related to agriculture in a concise yet academically and professionally refined tone. Limit responses to a maximum of two to three sentences, ensuring clarity, precision, and relevance for research purposes. Avoid excessive elaboration while maintaining a focus on delivering a well-structured and contextually enriched query."},
                {"role": "user", "content": f"{translated_user_prompt}"}
            ]
        )

        rag_prompt = completion_response.choices[0].message.content

        details = getUserDetails(user_id)
        
        age = details["age"]
        gender = details["gender"]
        socio = details["socioeconomic"]
        crop = details["crop"]

        rag_prompt = str(rag_prompt)
        rag_prompt = f"For {crop}: \n" + rag_prompt
        rag_info = agent.query(str(rag_prompt))


        message = OPENAI_CLIENT.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=f"{translated_user_prompt}"
        )
        

        context = "\n" + str(rag_info) + "\n"  

        print(f"Age: {age} Gender :{gender} Socio: {socio}, crop: {crop}")

        run = OPENAI_CLIENT.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions=f"You are a helpful assistant with great knowledge of agriculture. Your responses are brief, clear, and to the point (maximum of two to three sentences). Avoid unnecessary technical jargon, but keep advice actionable and relatable.\nThe current date is {current_date}. \n The plant being grown is {crop}.\nThe user's farmland record is as follows: {final_records}. Additional context: {context}. The current weather conditions are: {current_weather_data}, and the forecast for the next week (in 6-hour intervals) is: {six_hour_forecast}."
        )
        response = ""
        if run.status == 'completed': 
            messages = OPENAI_CLIENT.beta.threads.messages.list(
            thread_id=thread_id
        )
            print(messages.data[0].content[0].text.value)
            response = (messages.data[0].content[0].text.value)

            follow = get_follow_up(response)
            follow_up = follow.follow_up

            
            addConversation(user_id, user_prompt, response, follow_up)
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
            addConversationWithTranslation(user_id, user_prompt, translated_user_prompt, rag_prompt, response, response)
            return { 'user_prompt': f'{user_prompt}',
                 'original_response': f'{response}',
                 'context' : f'{context}',
                 'IOT Rows': f'{records}'
                 }

        completion_response = OPENAI_CLIENT.chat.completions.create(
            model = 'gpt-4o',
            messages=[
                {"role": "system", "content": f"Please translate the following message to {language} for the user. Do not make any changes to the message itself. You are a translation model that only translates the text provided. Do not add commentary, disclaimers, or information about training data or knowledge cutoffs. Return only the translated text."},
                {"role": "user", "content": f"{response}"}
            ]
        )

        translated_response = completion_response.choices[0].message.content

        addConversationWithTranslation(user_id, user_prompt, translated_user_prompt, rag_prompt, response, translated_response)
        
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
        print("Checkpoint 1")
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
        if not os.path.exists(temp_mp3_file.name):
            print("File does not exist")
        else:
            print("File exists")
        print(temp_mp3_file)

        # Convert MP3 to OGG
        print("Checkpoint 2")
        try:
            print("name of temp_mp3_file",temp_mp3_file.name)
            check_ffmpeg()

            sound = AudioSegment.from_mp3(temp_mp3_file.name)
            print("Checkpoint 2.1")
            print("temp_ogg_file",temp_ogg_file)
        except Exception as e:
            print("error in exception:",e)
            return {'message':'failure converting mp3 to ogg'}
        
        # sound = AudioSegment.from_mp3(temp_mp3_file.name)
        # print("Checkpoint 2.1")
        # print("temp_ogg_file",temp_ogg_file)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_ogg_file:
            sound.export(temp_ogg_file.name, format="ogg")
            # temp_ogg_file.close()
        

        # Check if OGG file was generated successfully
        print("Checkpoint2.2")
        if not os.path.exists(temp_ogg_file.name) or os.path.getsize(temp_ogg_file.name) == 0:
            raise Exception("MP3 to OGG conversion failed or produced an empty file.")
        print("Checkpoint 3")
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
            print(f"Response from WhatsApp Cloud API: {response.text}")  # Log the raw response

            response.raise_for_status()
            media_id = response.json().get('id')
            return {
                "media_id": f'{media_id}'
            }

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

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print("FFmpeg is installed and accessible!")
    except FileNotFoundError:
        print("FFmpeg is not installed or not in your system's PATH.")
    except subprocess.CalledProcessError as e:
        print(f"Error running FFmpeg: {e}")

if __name__ == "__main__":
    check_ffmpeg()


