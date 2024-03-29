from fastapi import APIRouter, File, UploadFile, FileResponse
import shutil
import os

router = APIRouter(
    tags=["artifacts"],
    responses={404: {"description": "Not found"}},
)

@router.get("/artifacts/")
async def get_artifact():
    files = []
    for filename in os.listdir("."):
        if os.path.isfile(filename):
            files.append(filename)
    return {"documents": files}

@router.get("/artifacts/{artifact_id}")
async def get_artifact(artifact_id: str):
    if os.path.isfile(artifact_id):
        return FileResponse(artifact_id)
    else:
        return {"error": "File not found"}

@router.post("/artifacts")
async def create_upload_file(file: UploadFile = File(...)):
    try:
        with open(file.filename, "wb") as buffer:
          shutil.copyfileobj(file.file, buffer)
        return {"filename": file.filename}
    except Exception as e:
        return {"error": str(e)}
