from db_schema import User, Reading, Message, AppUsage, MessageWithTranslation, getEngine
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

# Function to drop the 'app_usage' table
def drop_app_usage_table(engine):
    Base.metadata.drop_all(engine, tables=[AppUsage.__table__])
    print("Dropped 'app_usage' table.")

# Function to drop the 'app_usage' table
def drop_message_translation_table(engine):
    Base.metadata.drop_all(engine, tables=[MessageWithTranslation.__table__])
    print("Dropped 'app_usage' table.")


# Drop the 'messages' table
drop_messages_table(engine)

# Drop the 'readings' table
drop_readings_table(engine)

drop_app_usage_table(engine)

drop_message_translation_table(engine)

# # Now drop the 'users' table
# drop_users_table(engine)

# drop_app_usage_table(engine)