from db_schema import User, Reading, Message, getEngine
from sqlalchemy.ext.declarative import declarative_base

# Create an engine
engine = getEngine()

# Create a base class for our classes definitions
Base = declarative_base()

# Function to drop the 'users' table
def drop_users_table(engine):
    Base.metadata.drop_all(engine, tables=[User.__table__])
    print("Dropped 'users' table.")

# Function to drop the 'messages' table
def drop_messages_table(engine):
    Base.metadata.drop_all(engine, tables=[Message.__table__])
    print("Dropped 'messages' table.")

# Function to drop the 'readings' table
def drop_readings_table(engine):
    Base.metadata.drop_all(engine, tables=[Reading.__table__])
    print("Dropped 'readings' table.")


# Drop the 'messages' table
drop_messages_table(engine)

# Drop the 'readings' table
drop_readings_table(engine)

# Now drop the 'users' table
drop_users_table(engine)