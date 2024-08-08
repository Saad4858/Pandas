from db_schema import User, Reading, Message, getEngine
from sqlalchemy.orm import sessionmaker
import pandas as pd

engine = getEngine()
Session = sessionmaker(bind=engine)
session = Session()

# Define the export function
def export_table_to_csv(table_class, csv_filename):
    # Query all data from the table
    data = session.query(table_class).all()

    # Convert the data to a list of dictionaries
    data_dicts = [row.__dict__ for row in data]

    # Remove SQLAlchemy's internal state key
    for data_dict in data_dicts:
        data_dict.pop('_sa_instance_state', None)

    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(data_dicts)

    # Export the DataFrame to a CSV file
    df.to_csv(csv_filename, index=False)
    print(f"Data from {table_class.__tablename__} table exported to {csv_filename}")

# Export each table to a separate CSV file
export_table_to_csv(User, 'users.csv')
export_table_to_csv(Message, 'messages.csv')
export_table_to_csv(Reading, 'readings.csv')

# Close the session
session.close()
