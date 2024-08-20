from db_schema import User, Reading, Message, getEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc

def addUser(name, address, phone, city, country, language, thread_id):
    try:
        # Setup the engine and session
        engine = getEngine()
        Session = sessionmaker(bind=engine)

        # Step 2: Create a session
        session = Session()

        # Step 3: Create an instance of your model
        new_user = User(name=name, address=address, phone=phone, city=city, country=country, language=language, thread_id=thread_id)

        # Step 4: Add the instance to the session
        session.add(new_user)

        # Step 5: Commit the transaction
        session.commit()

        # Close the session
        session.close()
    except Exception as e:
        print(f"Error: Could Not Add User. Exception: {e}")

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

def addConversation(user_id, message, response):
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
            response=response
        )

        # Add the instance to the session
        session.add(new_message)

        # Commit the transaction
        session.commit()

        # Close the session
        session.close()
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
            return user.thread_id, user.id
        else:
            # If the user does not exist, return None or handle accordingly
            print("Error: Could Not Get User Thread")
            return "", ""
    except Exception as e:
        print(f"Error: Could Not Get User Thread. Exception: {e}")
        return "", ""