from fastapi import FastAPI
import os 
from dotenv import load_dotenv
import openai
import requests
from db_controllers import addReadingRecord, addUser, get10ReadingRecords


load_dotenv()


API_KEY = os.getenv("OPENAI_API_KEY")

    
OPENAI_CLIENT = openai.OpenAI(
    api_key=API_KEY,
)



app = FastAPI()

@app.get("/")
async def root():
    print("Hello World ")
    return {"message": "Hello World"}

@app.get('/translatedResponseUser')
async def get_translated_response(user_prompt: str , language: str):
    try:

        
       
        records = "IOT Data"
        context = "Context of the user's farmland"
        context  = context +"\n"+"Considering the weather conditions \n" 
        context = context + "\n" 
        completion_response = OPENAI_CLIENT.chat.completions.create(
            model = 'gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": f"You are a helpful assistant who has great knowledge of agriculture. You answer in simple language with no markdown. Keep your answers short, to the point and to a maximum of two sentences. Do not mention technical details in your answer. The user's farmland has the following record: {str(records)} and the following is additional information: {context}"},
                {"role": "user", "content": f"{user_prompt}"}
            ]
        )

        response = completion_response.choices[0].message.content

        users_language = language

        # Translating Response To Local Language of User (Pulled From DB)
        translated_response = OPENAI_CLIENT.chat.completions.create(
            model = 'gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": f"You are a helpful assistant who has great knowledge of languages. You translate English to local languages for farmers in Pakistan."},
                {"role": "user", "content": f"Translate the following {response} into {users_language} language."}
            ]
        )

        print(f"You asked: {user_prompt}")
        print(f"Response: {translated_response.choices[0].message.content}")
        

        return { 'user_prompt': f'{user_prompt}',
                 'original_response': f'{response}',
                 'translated_response': f'{translated_response.choices[0].message.content}',
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



