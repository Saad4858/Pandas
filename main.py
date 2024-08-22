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
        print("Audio Content:",audio_content)
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

        thread_id, user_id = getThreadID(phone)
        language = getLanguage(user_id)

        print(f"Thread: {thread_id}")
        print(f"User id: {user_id}")

        records = ""

        # Temporary For LUMS Farm Situation (Shared Sensor Data but Separate Users)
        if (user_id == 1):
            records = get10ReadingRecords()
        else:
            records = get10ReadingRecordsID(user_id)

        # records = get10ReadingRecords()

        current_weather_data = get_current_weather_data("Lahore")

        forecast , six_hour_forecast = get_forecast("Lahore",3)

        current_date = datetime.now().date()
        print(f"Current Date: {current_date}")

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
        assistant_id="asst_FBRU2BrRnNhJCdvFO2cTgT9A",
        instructions=f"You are a helpful assistant who has great knowledge of agriculture. You answer in simple language with no markdown. Provide Natural language responses with no markdown. Keep your answers short, to the point and to a maximum of two to three sentences. Do not mention technical details in your answer. The date today is {current_date}. The user profile is as provided , {profile}. The user's farmland has the following record: {str(records)} and the following is additional information: {context}. The current weather situation is as follows: {current_weather_data}. The forecast for the next week in 6 hours intervals is as follows: {six_hour_forecast}. You should respond mostly in English."
        )

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

        # users_language = language

        # # Translating Response To Local Language of User (Pulled From DB)
        # translated_response = OPENAI_CLIENT.chat.completions.create(
        #     model = 'gpt-3.5-turbo',
        #     messages=[
        #         {"role": "system", "content": f"You are a helpful assistant who has great knowledge of languages. You translate English to local languages for farmers in Pakistan."},
        #         {"role": "user", "content": f"Translate the following {response} into {users_language} language."}
        #     ]
        # )

        # print(f"You asked: {user_prompt}")
        # print(f"Response: {translated_response.choices[0].message.content}")
        
        

        return { 'user_prompt': f'{user_prompt}',
                 'original_response': f'{translated_response}',
                 'context' : f'{context}',
                 'IOT Rows': f'{records}'
                 }
    
    except Exception as e:
        print(e)
        return {'message':'failure getting latest message'}
    
# @app.post('/addUser')
# async def add_user(phone: str, user_id: int):
#     try:
#         addUser(phone, user_id)
#         return {'message':'success'}
#     except Exception as e:
#         print(e)
#         return {'message':'failure adding user'}
    

@app.post('/addReadingRecord')
async def add_reading_record(pH: float, nitrogen: float, phosphorous: float, potassium: float, temperature: float, moisture: float, conductivity: float, battery: float, user_id: int):
    try:
        addReadingRecord(pH, nitrogen, phosphorous, potassium, temperature, moisture, conductivity, battery, user_id)
        return {'message':'success'}
    except Exception as e:
        print(e)
        return {'message':'failure adding reading record'}



