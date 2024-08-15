from fastapi import FastAPI
import os 
from dotenv import load_dotenv
import openai
import requests
from db_controllers import addReadingRecord, addUser, get10ReadingRecords, getLanguage, addConversation, getThreadID

from weather_api import get_current_weather_data , get_forecast


load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")


from RAG.rag_main import agent

    
OPENAI_CLIENT = openai.OpenAI(
    api_key=API_KEY,
)



app = FastAPI()

@app.get("/")
async def root():
    print("Hello World ")
    return {"message": "Hello World"}

@app.get('/translatedResponseUser')
async def get_translated_response(user_prompt: str , language: str, phone: str):
    try:

        thread_id, user_id = getThreadID(phone)
       
        records = get10ReadingRecords()

        current_weather_data = get_current_weather_data("Lahore")

        forecast , six_hour_forecast = get_forecast("Lahore",3)

        context = "Context of the user's farmland"
        context  = context +"\n"+"Considering the weather conditions \n" + current_weather_data
        context = context + "\n" + six_hour_forecast



        rag_info = agent.query(user_prompt) # user_prompt for now

        context = "\n" + "The following is additional information: \n" + rag_info + "\n"   

        message = OPENAI_CLIENT.beta.threads.messages.create(
        thread_id="thread_8iLgae7iQ0MXtSoLq5XHNoK0",
        role="user",
        content=f"{user_prompt}"
        )

        run = OPENAI_CLIENT.beta.threads.runs.create_and_poll(
        thread_id="thread_8iLgae7iQ0MXtSoLq5XHNoK0",
        assistant_id="asst_osvt9lAtJC3oxsI7CQJ2r3GO",
        instructions=f"You are a helpful assistant who has great knowledge of agriculture. You answer in simple language with no markdown. Keep your answers short, to the point and to a maximum of two sentences. Do not mention technical details in your answer. The user's farmland has the following record: {str(records)} and the following is additional information: {context}"
        )

        if run.status == 'completed': 
            messages = OPENAI_CLIENT.beta.threads.messages.list(
            thread_id="thread_8iLgae7iQ0MXtSoLq5XHNoK0"
        )
            print(messages.data[0].content[0].text.value)
            response = (messages.data[0].content[0].text.value)
            
            addConversation(user_id, user_prompt, response)
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



