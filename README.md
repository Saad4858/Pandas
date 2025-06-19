# 🌾 Kissan Dost — AI + IoT Agriculture Advisory System

Kissan Dost is a multilingual AI-powered agriculture assistant designed to help low-literacy farmers in Pakistan. It combines real-time soil sensor data, localized weather forecasts, government market prices, and crop-specific document insights using OpenAI GPT-4o and Retrieval-Augmented Generation (RAG). Users interact via WhatsApp in their local language and receive advice via text and voice.

---

## ✨ Features

- 🧠 Personalized farm advice powered by GPT-4o
- 📡 Real-time sensor logging (soil, weather, battery)
- 🌤️ Live weather data and forecasts via WeatherAPI
- 📊 Daily crop prices from AMIS Pakistan
- 📚 RAG-based document search on crop policies (PDFs)
- 🗣️ Text-to-Speech voice replies via WhatsApp
- 🌍 Local language input/output with translation support
- 🛠️ FastAPI backend, PostgreSQL DB, OpenAI, LlamaIndex

---

## 📁 Project Structure

```
├── main.py                  # FastAPI app (API routes)
├── db_schema.py             # PostgreSQL models
├── db_controllers.py        # DB interaction functions
├── db_csv_dump.py           # Exports data to CSV
├── db_table_droppers.py     # Table deletion utilities
├── weather_api.py           # Weather data fetch
├── market_scraper.py        # Market price scraper
├── index_builder.py         # Crop PDF index builder
├── rag.py                   # RAG agent configuration
├── helpers.py               # WhatsApp API, TTS, Assistant setup
├── requirements.txt         # Python dependencies
├── readings.csv             # Sample soil sensor readings
```

---

## ✅ Requirements

You must have the following installed and configured:

- 🐍 Python 3.9+
- 🐘 PostgreSQL (or compatible SQL DB)
- 🎙️ FFmpeg (for audio processing)
- 🔑 OpenAI API key

Optional:
- 📱 WhatsApp Cloud API token

We used WhatsApp for end user delivery, however that is optional and completely up to you. The server itself is stand-alone and does not require WhatsApp to work.

---

## 🚀 Getting Started

### 1️. Clone the Repository

```bash
git clone https://github.com/Saad4858/Pandas.git
cd Pandas
```

### 2️. Install Dependencies

Make sure you have Python 3.9+ installed. Then install the required packages using pip:

```bash
pip install -r requirements.txt
```

### 3️. Set Up Environment Variables

Create a `.env` file in the root of the project with the following content:

```env
# Database connection
DB_TYPE=postgresql
DB_USER=your_db_user
DB_PASS=your_db_password
DB_HOST=localhost
DB_PORT=your_port
DB_NAME=kissanDost

# OpenAI API
OPENAI_API_KEY=your_api_key

# Weather API
WEATHER_API_KEY=your_api_key

# WhatsApp Cloud API (If using)
WHATSAPP_BEARER=your_bearer_token
```
For the weather api we used: https://www.weatherapi.com/

---

## 🗃️ Database Setup & Sample Data

### 4. Create the Database Tables

Ensure your PostgreSQL (or preferred SQL database) is running and matches the credentials in `.env`.

Run the following Python one-liner to initialize all database tables using SQLAlchemy:

```bash
python -c "import db_schema"
```

This will create the following tables:
- `users`
- `readings`
- `messages`
- `messages_with_translation`
- `app_usage`

---

### 5. Populate the Database with Sample Sensor Readings

A sample dataset is provided in `readings.csv`. You can load it into the database using this script:

```python
import pandas as pd
from db_controllers import addReadingRecord

df = pd.read_csv("readings.csv")
for _, row in df.iterrows():
    addReadingRecord(
        row['pH'], row['nitrogen'], row['phosphorus'], row['potassium'],
        row['temperature'], row['moisture'], row['conductivity'], row['battery'], row['user_id']
    )
```

> Make sure that the `user_id` values in `readings.csv` correspond to actual users in the `users` table. 

> You may need to manually add test users using the `addUser()` function from `db_controllers.py` 

---

### 6. Export Data to CSV (Optional)

If you want to, you can dump your database contents to CSV files:

```bash
python db_csv_dump.py
```

This will generate:
- `users.csv`
- `messages.csv`
- `messages_translation.csv`
- `readings.csv`
- `app_usage.csv`

---

## 📚 RAG Indexing & Market Scraping

### 7. Add Crop Policy Documents

To enable Retrieval-Augmented Generation (RAG), place relevant PDF files into the following directory structure:

```
data/
├── wheat/
│   └── (Add wheat PDFs here)
├── rice/
│   └── (Add rice PDFs here)
├── cotton/
│   └── (Add cotton PDFs here)
├── sugarcane/
│   └── (Add sugarcane PDFs here)
├── maize/
│   └── (Add maize PDFs here)
├── spinach/
│   └── (Add spinach PDFs here)
```

Each folder should contain at least one `.pdf` file for that crop. Files have already been provided in these folders.

---

### 8. Build the RAG Indexes

Run the following script to process all crop PDFs and create persistent vector indexes:

```bash
python index_builder.py
```

This uses `llama-index` to convert documents into searchable embeddings for the ReAct Agent in `rag.py`.

> These indexes will later be queried by GPT-4o during assistant responses to inject factual, crop-specific insights.

---

## 📊 Market Price Scraping (Optional)

### 9. Scrape Daily Crop Prices from AMIS Pakistan

Run the following script to fetch crop market data for different cities from [AMIS.pk](http://amis.pk):

```bash
python market_scraper.py
```

This will generate a file named:

```
cities_crop_prices.json
```

It includes structured daily pricing info such as:

```json
"Lahore": [
  {
    "Crop": "Wheat",
    "Min": "3800",
    "Max": "4200",
    "FQP": "4000"
  },
  ...
]
```

You can use this to supplement GPT responses or visualize trends.

---

## ▶️ Running and Using the App (Locally)

### 1️⃣ Start the FastAPI Server

After completing setup and database initialization, run the application locally using:

```bash
uvicorn main:app --reload
```

By default, the app will be available at:

```
http://127.0.0.1:8000
```

### 2️⃣ Explore the API via Swagger UI

Navigate to:

```
http://127.0.0.1:8000/docs
```

Here you can test endpoints directly through the browser using FastAPI’s interactive documentation.

---

## 🧪 Key API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/` | Health check |
| `POST` | `/transcribeAudio` | Upload MP3 audio, receive transcript (Whisper API) |
| `GET`  | `/translatedResponseUser` | Main advisory pipeline: input → translation → sensor + weather + RAG → GPT response |
| `GET`  | `/getAudioResponse?text=...` | Generate and receive voice response in `.ogg` format |
| `POST` | `/addReadingRecord` | Submit sensor readings for soil and battery metrics |

> ✅ All input to `/translatedResponseUser` is automatically localized and contextualized using user profile, weather, and sensor readings.

## 🙌 Credits

- 💡 Built as part of the **Kissan-Dost** ecosystem. ([`Agri-Chat`](https://github.com/DaaniKhan/Agri-Chat)), (['Agri-Dash'](https://github.com/DaaniKhan/Agri-Dash))
- 🤖 GPT-4o integration by [OpenAI](https://openai.com)
- 📡 Messaging via [Meta's WhatsApp Cloud API](https://developers.facebook.com/docs/whatsapp)