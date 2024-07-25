from db_schema import User, Reading, getEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc

def addUser(name, address, phone, city, country, language):
    # Setup the engine and session
    engine = getEngine()
    Session = sessionmaker(bind=engine)

    # Step 2: Create a session
    session = Session()

    # Step 3: Create an instance of your model
    new_user = User(name=name, address=address, phone=phone, city=city, country=country, language=language)

    # Step 4: Add the instance to the session
    session.add(new_user)

    # Step 5: Commit the transaction
    session.commit()

    # Close the session
    session.close()

def addReadingRecord(pH, nitrogen, phosphorous, potassium, temperature, moisture, conductivity, battery):
    engine = getEngine()
    Session = sessionmaker(bind=engine)

    session = Session()

    new_reading = Reading(
        pH=pH, nitrogen=nitrogen, 
        phosphorous=phosphorous, 
        potassium=potassium, 
        temperature=temperature, 
        moisture=moisture, 
        conductivity=conductivity, 
        battery=battery)

    session.add(new_reading)

    session.commit()

    session.close()

def get10ReadingRecords():
    engine = getEngine()
    Session = sessionmaker(bind=engine)

    session = Session()
    query = session.query(Reading).order_by(desc(Reading.created_at)).limit(10)

    # Using `with_entities` to specify the columns you want as dictionary keys
    dict_results = [
        {column.name: getattr(row, column.name) 
        for column in Reading.__table__.columns}
        for row in query
    ]

    session.close()

    return dict_results