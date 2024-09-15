from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Define allowed origins (you can restrict this to specific domains for security)
origins = [
    "http://localhost",  # For local development
    "http://localhost:9000",  # If you're working with a frontend on localhost:3000
    # Add other domains or IP addresses as needed
]

# Add the CORS middleware to the FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows the specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def read_root():
    return {"message": "CORS is working!"}
