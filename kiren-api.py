from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from abstracts import PaperMetadata, fetch_paper_metadata

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/get")
def get_abstract(url: str) -> PaperMetadata:
    metadata = fetch_paper_metadata(url)
    return metadata


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)