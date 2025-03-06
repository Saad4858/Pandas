from db_schema import User, Reading, Message, MessageWithTranslation, getEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc

def addUser(name, address, phone, city, country, language, thread_id, assistant_id, update_time, gender, age, socioeconomic, TypeOfFarm, crop):
    try:
        # Setup the engine and session
        engine = getEngine()
        Session = sessionmaker(bind=engine)

        # Step 2: Create a session
        session = Session()

        # Step 3: Create an instance of your model
        new_user = User(
            name=name, 
            address=address, 
            phone=phone, 
            city=city, 
            country=country, 
            language=language, 
            thread_id=thread_id, 
            assistant_id=assistant_id,
            update_time=update_time,
            gender=gender,
            age=age,
            socioeconomic=socioeconomic,
            TypeOfFarm=TypeOfFarm,
            crop=crop
        )

        # Step 4: Add the instance to the session
        session.add(new_user)

        # Step 5: Commit the transaction
        session.commit()

        # Close the session
        session.close()
    except Exception as e:
        print(f"Error: Could Not Add User. Exception: {e}")

def getUserDetails(user_id):
    try:
        # Setup the engine and session
        engine = getEngine()
        Session = sessionmaker(bind=engine)
        
        # Step 2: Create a session
        session = Session()
        
        # Step 3: Query the User by user_id
        user = session.query(User).filter(User.id == user_id).first()

        # Close the session
        session.close()

        # Step 4: Check if the user exists and return details
        if user:
            return {
                "user_id": user.id,
                "name": user.name,
                "address": user.address,
                "phone": user.phone,
                "city": user.city,
                "country": user.country,
                "language": user.language,
                "thread_id": user.thread_id,
                "assistant_id": user.assistant_id,
                "update_time": user.update_time,
                "gender": user.gender,
                "age": user.age,
                "socioeconomic": user.socioeconomic,
                "TypeOfFarm": user.TypeOfFarm,
                "crop": user.crop
            }
        else:
            return f"No user found with ID {user_id}"

    except Exception as e:
        return f"Error: Could not retrieve user details. Exception: {e}"

def addReadingRecord(pH, nitrogen, phosphorous, potassium, temperature, moisture, conductivity, battery, user_id):
    try: 
        engine = getEngine()
        Session = sessionmaker(bind=engine)

        session = Session()

        new_reading = Reading(
            pH=pH, 
            nitrogen=nitrogen, 
            phosphorus=phosphorous, 
            potassium=potassium, 
            temperature=temperature, 
            moisture=moisture, 
            conductivity=conductivity, 
            battery=battery,
            user_id=user_id
            )

        session.add(new_reading)

        session.commit()

        session.close()
    except Exception as e:
        print(f"Error: Could Not Add Reading. Exception: {e}")
    
def get10ReadingRecords():
    try:
        engine = getEngine()
        Session = sessionmaker(bind=engine)

        session = Session()
        query = session.query(Reading).order_by(desc(Reading.created_at)).limit(10)

        # Using with_entities to specify the columns you want as dictionary keys
        dict_results = [
            {column.name: getattr(row, column.name) 
            for column in Reading.__table__.columns}
            for row in query
        ]

        session.close()

        return dict_results
    except Exception as e:
        print(f"Error: Could Not Get Latest Readings. Exception: {e}")
        return ""

def get10ReadingRecordsID(user_id):
    try:
        engine = getEngine()
        Session = sessionmaker(bind=engine)

        session = Session()
        
        # Query to get the latest 10 readings for the specified user_id
        query = (
            session.query(Reading)
            .filter_by(user_id=user_id)
            .order_by(desc(Reading.created_at))
            .limit(10)
        )

        # Using `with_entities` to specify the columns you want as dictionary keys
        dict_results = [
            {column.name: getattr(row, column.name) 
            for column in Reading.__table__.columns}
            for row in query
        ]

        session.close()

        return dict_results
    except Exception as e:
        print(f"Error: Could Not Get Latest Readings. Exception: {e}")
        return ""

def addConversation(user_id, message, response, actionable):
    try:
        # Setup the engine and session
        engine = getEngine()
        Session = sessionmaker(bind=engine)

        # Create a session
        session = Session()

        # Create an instance of the Message model
        new_message = Message(
            user_id=user_id,
            message=message,
            response=response,
            actionable=actionable
        )

        # Add the instance to the session
        session.add(new_message)

        # Commit the transaction
        session.commit()

        # Close the session
        session.close()
    except Exception as e:
        print(f"Error: Could Not Add Conversation. Exception: {e}")

def addConversationWithTranslation(user_id, message, translated_message, rag_message, response, translated_response):
    try:
        # Setup the engine and session
        engine = getEngine()
        Session = sessionmaker(bind=engine)

        # Create a session
        session = Session()

        # Create an instance of the MessageWithTranslation model
        new_message = MessageWithTranslation(
            user_id=user_id,
            message=message,
            translated_message=translated_message,
            rag_message=rag_message,
            response=response,
            translated_response=translated_response  # New field
        )

        # Add the instance to the session
        session.add(new_message)

        # Commit the transaction
        session.commit()

        # Close the session
        session.close()
        print("Conversation added successfully.")
    except Exception as e:
        print(f"Error: Could Not Add Conversation. Exception: {e}")

def getLanguage(user_id):
    try:
        # Query the User table for the language of the specified user_id
        # Setup the engine and session
        engine = getEngine()
        Session = sessionmaker(bind=engine)

        # Create a session
        session = Session()

        user = session.query(User).filter_by(id=user_id).first()

        # If the user exists, return their language
        if user:
            # Close the session
            session.close()
            return user.language
        else:
            # If the user does not exist, return None or handle accordingly
            return ""
    except Exception as e: 
        print(f"Error: Could Not Get User Language. Exception: {e}")
        return ""
        

def getThreadID(phone):
    try: 
        # Query the user by phone
        engine = getEngine()
        Session = sessionmaker(bind=engine)

        # Create a session
        session = Session()

        user = session.query(User).filter_by(phone=phone).first()
        if user:
            # If the user exists, return the thread_id
            session.close()
            return user.thread_id, user.assistant_id, user.id
        else:
            # If the user does not exist, return None or handle accordingly
            print("Error: Could Not Get User Thread")
            return "", "" ,""
    except Exception as e:
        print(f"Error: Could Not Get User Thread. Exception: {e}")
        return "", "" ,""

def updateUserTime(user_id, new_update_time):
    try:
        # Setup the engine and session
        engine = getEngine()
        Session = sessionmaker(bind=engine)

        # Step 2: Create a session
        session = Session()

        # Step 3: Query the user by user_id
        user = session.query(User).filter_by(id=user_id).first()

        # Check if the user exists
        if user:
            # Step 4: Update the update_time field
            user.update_time = new_update_time

            # Step 5: Commit the transaction
            session.commit()
            print(f"User {user_id} update_time updated to {new_update_time}")
        else:
            print(f"User with id {user_id} not found.")

        # Close the session
        session.close()

    except Exception as e:
        print(f"Error: Could not update update_time. Exception: {e}")

# addUser("Kabir", "Lahore", "923004329358", "Lahore", "Pakistan", "Urdu", "thread_3TpUkU0UoJhcp7EDl1Vg70AA", "asst_0VXWOSPlPvmOyM14EzLYWvsC", "09:00", "male", "52", "low", "personal use", "green pea")
# addUser("Mehboob", "Lahore", "923015919844", "Lahore", "Pakistan", "Urdu", "thread_VyONdSzAZ9BFnmLMfugkouQs", "asst_FG4UQzqQeyqhlX3Bfeb2AaV6", "09:00", "male", "45", "low", "personal use", "green pea")
# addUser("Majid", "Lahore", "923004907501", "Lahore", "Pakistan", "Urdu", "thread_EtQGRB0aZaLmUNB7G64VVRje", "asst_lr8MY3mwPFxPoV66aYpSsPZz", "09:00", "male", "42", "low", "personal use", "green pea")
# addUser("Amjad", "Lahore", "923134196444", "Lahore", "Pakistan", "Urdu", "thread_pYFZ3y4F7bqouPbqdWMXaGFn", "asst_ewP59HXrjOZBhfJHshYphnbN", "09:00", "male", "44", "low", "personal use", "green pea")