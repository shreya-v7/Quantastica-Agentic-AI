from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

from .api.routes import prompt, testdata
from .api.sessions import session


#app.include_router(voice.router, prefix="/voice")
#app.include_router(finance.router, prefix="/finance")
#app.include_router(group.router, prefix="/group")
app.include_router(session.router, prefix="/sessions")
app.include_router(prompt.router, prefix="/prompt")
app.include_router(testdata.router, prefix="/data")

