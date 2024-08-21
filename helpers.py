import pandas as pd 
import json 
from dotenv import load_dotenv
import os 
from rag import getRagResponse

from openai import OpenAI

load_dotenv()


API_KEY = os.getenv("OPENAI_API_KEY")


client = OpenAI(
   api_key = API_KEY
)
  

query= "I am seeking expert guidance on effective strategies to protect my cotton plants from insect infestations. Please provide a detailed plan that includes the most appropriate pest control methods for my region, considering the current environmental conditions and pest trends. I am also interested in understanding the best practices for implementing these methods in a sustainable manner that minimizes harm to the environment and maintains the health of the cotton plants."
print(getRagResponse(query))
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


