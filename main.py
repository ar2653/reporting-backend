from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pymongo.mongo_client import MongoClient
from pydantic import ValidationError
import os
from urllib.parse import quote_plus
import certifi
from models import Report
from dotenv import load_dotenv

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables from .env file
load_dotenv()

# Get environment variables
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_CLUSTER = os.getenv("DB_CLUSTER")
DB_NAME = os.getenv("DB_NAME")

# Construct the connection string
CONNECTION_STRING = f"mongodb+srv://{DB_USERNAME}:{quote_plus(DB_PASSWORD)}@{DB_CLUSTER}.mongodb.net/?retryWrites=true&w=majority&appName={DB_NAME}"

# Create MongoDB client
client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    db = client["reports"]
    collection = db["report_data"]
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")

# Test 
@app.get("/")
def root():
    return {"message": "Hello World"}

# Test
@app.get("/health-check")
def health_check():
    return {"status": "ok"}


@app.get("/record/{report_name}")
def get_record(report_name: str):
    """ Retrieve a record from the database based on the report name. """
    record = collection.find_one({"reportName": report_name})
    if record:
        record["_id"] = str(record["_id"])
        return record
    raise HTTPException(status_code=404, detail="Record not found")

@app.post("/record", status_code=status.HTTP_201_CREATED)
async def create_record(report: Report):
    """ Create a new record in the database. """
    try:
        result = collection.insert_one(report.dict())
        return {"id": str(result.inserted_id)}
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
