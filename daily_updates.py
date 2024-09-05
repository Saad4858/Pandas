import os 
from dotenv import load_dotenv
import openai
import requests
from db_controllers import addReadingRecord, addUser, get10ReadingRecords, getLanguage, addConversation, getThreadID, get10ReadingRecordsID

from datetime import datetime
from helpers import sendWhatsappMessage

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
    
OPENAI_CLIENT = openai.OpenAI(
    api_key=API_KEY,
)

def sendDailyUpdate(phone):
    try:
        thread_id, user_id = getThreadID(phone)
        language = getLanguage(user_id)

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


        # current_weather_data = get_current_weather_data("Lahore")

        # forecast , six_hour_forecast = get_forecast("Lahore",3)

        current_date = datetime.now().date()
  
        profile = "" 

        if (user_id == 3):
            profile ="A meticulous and detail-oriented individual, she holds a PhD in Computer Science with a specialization in Human-Computer Interaction. She is an instructor at a prestigious university and applies her rigorous academic mindset to her home farming activities. Growing blackberries in DHA, Lahore, Punjab, Pakistan, she dedicates daily attention to her crop, striving for the highest quality. Her interest in innovative techniques aligns with her commitment to successful and sustainable farming practices. Given her preference for efficiency, she values concise, 2-3 line responses from a chatbot to quickly address her queries and needs. She specifically seeks brief but actionable advice that she can put into practice, ensuring her time is used effectively"

        if (user_id == 1):
            profile ="A meticulous and detail-oriented individual, she holds a PhD in Computer Science with a specialization in Human-Computer Interaction. She is an instructor at a prestigious university and applies her rigorous academic mindset to her home farming activities. Growing blackberries in DHA, Lahore, Punjab, Pakistan, she dedicates daily attention to her crop, striving for the highest quality. Her interest in innovative techniques aligns with her commitment to successful and sustainable farming practices. Given her preference for efficiency, she values concise, 2-3 line responses from a chatbot to quickly address her queries and needs. She specifically seeks brief but actionable advice that she can put into practice, ensuring her time is used effectively"

        if (user_id == 2):
            profile ="Prepare a message for a 45-year-old female from a low socio-economic background, farming 5 acres with a focus on maize and rice. Optimize her traditional farming and tube well irrigation practices while improving manual pest control methods. Given her primary education and basic mobile phone usage, ensure the advice is straightforward and practical. Use simple Urdu text messages to communicate ways to enhance soil fertility and manage water efficiently. Highlight strategies to combat frequent floods and limited access to chemical fertilizers. Motivate her to explore drip irrigation given her interest in modern techniques, and clarify the importance of pH balance and soil nutrients for better crop health"

        system_prompt = """
            You are an intelligent agricultural assistant designed to help users monitor and manage their crops effectively. Users will provide you with sensor data including moisture, temperature, electrical conductivity, pH, nitrogen (N), phosphorus (P), and potassium (K) levels for their field. Each user will also specify the type of crop planted, such as wheat, corn, or tomatoes.

            When a user asks about the status of their crop, follow these steps:

            1. Identify the Crop: First, recognize the specific crop mentioned by the user (e.g., wheat, corn).

            2. Retrieve Optimal Ranges: Access and reference the optimal ranges for each of the provided sensor data points (moisture, temperature, electrical conductivity, pH, N, P, K) for the identified crop.

            3. Compare and Analyze: Compare the user's sensor data against the optimal ranges. Highlight where the data is within the optimal range and where it deviates.

            4. Provide Insights:
                - If all readings are within the optimal range, confirm that the crop is in good condition.
                - If any readings are outside the optimal range, indicate potential issues, their implications for crop health, and suggest possible corrective actions.

            5. Structure of the Response:
                - Begin with a summary of the crop's overall status.
                - Provide a detailed comparison of each sensor reading against the optimal range, including whether it is too high, too low, or optimal.
                - Offer actionable advice based on the deviations, if any.

            Example response structure:

            - Overall Status: "Your wheat crop is currently in [good condition/at risk]."
            
            - Detailed Analysis:
            - Moisture: "The soil moisture is [optimal/low/high] compared to the optimal range for wheat (X% - Y%). This suggests [implication]."
            - Temperature: "The temperature is [optimal/low/high] at Z°C, which is [below/above] the ideal range for wheat (A°C - B°C). This could [effect]."
            - Electrical Conductivity: "[Comment on conductivity]."
            - pH: "[Comment on pH]."
            - Nitrogen (N): "[Comment on N levels]."
            - Phosphorus (P): "[Comment on P levels]."
            - Potassium (K): "[Comment on K levels]."
            
            - Recommendations: "[Provide tailored advice based on the analysis, such as adjusting irrigation, adding fertilizers, or amending soil pH.]"

            Ensure that your responses are clear, concise, and actionable to help the user make informed decisions about their crop management.
            """

        
        message = OPENAI_CLIENT.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=f"What is the status of my plant"
        )

        run = OPENAI_CLIENT.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id="asst_7NBRXiK2PDPyrSzwHi73LkNX",
        instructions=f"{system_prompt}.\nThe date today is {current_date}.\nUser profile: {profile}.\nThe user's farmland has the following record: {str(final_records)}."
        )
        response = ""
        if run.status == 'completed': 
            messages = OPENAI_CLIENT.beta.threads.messages.list(
            thread_id=thread_id
        )
            response = (messages.data[0].content[0].text.value)
            
            addConversation(user_id, "daily update", response)
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
            print(f"\nResponse:\n{response}" )

            sendWhatsappMessage(phone, response)

            return { 'user_prompt': f'daily update',
                 'original_response': f'{response}',
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

        print(f"\nResponse:\n{translated_response}" )
            
        sendWhatsappMessage(phone, translated_response)
        
        return { 'user_prompt': 'daily update',
                 'original_response': f'{translated_response}',
                 'IOT Rows': f'{records}'
                 }
    
    except Exception as e:
        print(e)
        return {'message':'failure getting latest message'}
    
# Add Function Calls For Users to Update Here
sendDailyUpdate("923200006080")