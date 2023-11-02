from fastapi import FastAPI
from functions import *

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/dockercheck")
async def test():
    test = runTraefik()
    return {"message": test}

@app.get("/apache")
async def debug():
    setupUserApache("ilies")
    return {"message": "toto"}

@app.get("/iliesenv")
async def debug():
    prepareUserEnv("ilies")
    return {"message": "toto"}

@app.get("/iliesdb")
async def debug():
    setUserMariaDB("ilies") 
    return {"message": "toto"}


@app.get("/traefik")
async def traefik():
    runTraefik()
    return {"message": "toto"}

@app.get("/php")
async def traefik():
    setUserPhp("ilies","8.1")
    return {"message": "toto"}

@app.get("/getarchive")
async def traefik():
    getDolibarrArchive("18.0.2")
    return {"message": "toto"}

@app.get("/getdolibarr")
async def traefik():
    getDolibarr("ilies", "18.0.2","totibar")
    return {"message": "toto"}