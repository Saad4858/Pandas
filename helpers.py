import pandas as pd 
import json 
from dotenv import load_dotenv
import os 


from openai import OpenAI

load_dotenv()


API_KEY = os.getenv("OPENAI_API_KEY")


client = OpenAI(
   api_key = API_KEY
)
  

    

assistant = client.beta.assistants.create(
  name="Agriculture Specialist Assistant",
  instructions="You are a hepful assistant who has greate knowledge of agriculture tasked to interpret farmers IOT data and provide actionable insights to the farmers. You also should be able to provide market analysis and make best descisions for farmers telling them about the best crops to grow in their area and providing them with knowledge in any agricultural domain possible.",
  tools=[{"type": "code_interpreter"}],
  model="gpt-3.5-turbo",
)

thread = client.beta.threads.create()
print(thread.id)
print(assistant.id)
# message = client.beta.threads.messages.create(
#   thread_id="thread_8iLgae7iQ0MXtSoLq5XHNoK0",
#   role="user",
#   content="What is the best crop to grow in Lahore?"
# )

# run = client.beta.threads.runs.create_and_poll(
#   thread_id="thread_8iLgae7iQ0MXtSoLq5XHNoK0",
#   assistant_id="asst_osvt9lAtJC3oxsI7CQJ2r3GO",
#   instructions="Please address the user as Saad. The user has a premium account."
# )

# if run.status == 'completed': 
#   messages = client.beta.threads.messages.list(
#     thread_id="thread_8iLgae7iQ0MXtSoLq5XHNoK0"
#   )
#   print((messages.data[0].content[0].text.value))
#   # print(messages)

# else:
#   print(run.status)





# read teh data from the json file 
def get_crop_prices_by_city(city_name):
    try: 
        with open('cities_crop_prices.json') as f:
            data = json.load(f)
            return data[city_name]
    except Exception as e:
        print(e)
        return None
    
    
    
# create a function to print data in json format
def print_json_data(data):
    return json.dumps(data, indent=4)
    


