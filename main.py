from fastapi import FastAPI
import os 
from dotenv import load_dotenv
import openai
import requests
from db_controllers import addReadingRecord, addUser, get10ReadingRecords, getLanguage, addConversation, getThreadID, get10ReadingRecordsID

from weather_api import get_current_weather_data , get_forecast
import tempfile



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


@app.get('/transcribeAudio')
async def transcribe_audio(audio_content:bytes):
    try:
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

        records = ""

        # # Temporary For LUMS Farm Situation (Shared Sensor Data but Separate Users)
        # if (user_id == 3):
        #     records = get10ReadingRecordsID(user_id - 1)
        # else:
        #     records = get10ReadingRecordsID(user_id)

        # # records = get10ReadingRecords()

        # current_weather_data = get_current_weather_data("Lahore")

        # forecast , six_hour_forecast = get_forecast("Lahore",3)

        # context = "Context of the user's farmland"
        # context  = context +"\n"+"Considering the weather conditions \n" + current_weather_data
        # context = context + "\n" + six_hour_forecast


        # rag_info = agent.query(user_prompt) # Temporary For Now

        # context = "\n" + "The following is additional information: \n" + str(rag_info) + "\n"   
        context = "Context of the user's farmland"

        message = OPENAI_CLIENT.beta.threads.messages.create(
        thread_id="thread_t7dVpp2l82r1SHIAlJTiGTqw",
        role="user",
        content=f"{user_prompt}"
        )

        run = OPENAI_CLIENT.beta.threads.runs.create_and_poll(
        thread_id="thread_t7dVpp2l82r1SHIAlJTiGTqw",
        assistant_id="asst_JBdOZ0ojTdrWTXwYU1hfI0hO",
        instructions=f"You are a helpful assistant who has great knowledge of agriculture. You answer in simple language with no markdown. Keep your answers short, to the point and to a maximum of two sentences. Do not mention technical details in your answer. The user's farmland has the following record: {str(records)} and the following is additional information: {context}"
        )

        if run.status == 'completed': 
            messages = OPENAI_CLIENT.beta.threads.messages.list(
            thread_id="thread_t7dVpp2l82r1SHIAlJTiGTqw"
        )
            print(messages.data[0].content[0].text.value)
            response = (messages.data[0].content[0].text.value)
            
            addConversation(1, user_prompt, response)
        # print(messages)
        else:
            print(run.status)



        # completion_response = OPENAI_CLIENT.chat.completions.create(
        #     model = 'gpt-3.5-turbo',
        #     messages=[
        #         {"role": "system", "content": f"You are a helpful assistant who has great knowledge of agriculture. You answer in simple language with no markdown. Keep your answers short, to the point and to a maximum of two sentences. Do not mention technical details in your answer. The user's farmland has the following record: {str(records)} and the following is additional information: {context}"},
        #         {"role": "user", "content": f"{user_prompt}"}
        #     ]
        # )

        # response = completion_response.choices[0].message.content

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
                 'original_response': f'{response}',
                 'context' : f'{context}',
                 'IOT Rows': f'{records}'
                 }
    
    except Exception as e:
        print(e)
        return {'message':'failure getting latest message'}
    

@app.post('/addReadingRecord')
async def add_reading_record(pH: float, nitrogen: float, phosphorous: float, potassium: float, temperature: float, moisture: float, conductivity: float, battery: float, user_id: int):
    try:
        addReadingRecord(pH, nitrogen, phosphorous, potassium, temperature, moisture, conductivity, battery, user_id)
        return {'message':'success'}
    except Exception as e:
        print(e)
        return {'message':'failure adding reading record'}



