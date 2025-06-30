from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import sqlite3
import shutil

DB_PATH = "videos.db"
UPLOAD_DIR = "uploads"
CLIPS_DIR = "clips"

app = FastAPI()

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CLIPS_DIR, exist_ok=True)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            status TEXT NOT NULL,
            result TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS clips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER NOT NULL,
            label TEXT NOT NULL,
            filepath TEXT NOT NULL,
            FOREIGN KEY(video_id) REFERENCES videos(id)
        )
        """
    )
    conn.commit()
    conn.close()


init_db()


@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO videos (filename, status) VALUES (?, ?)",
        (file.filename, "uploaded"),
    )
    video_id = cur.lastrowid
    conn.commit()
    conn.close()

    return {"id": video_id, "filename": file.filename}


def run_pipeline(video_path: str):
    """Placeholder pipeline that copies video into a label directory."""
    label = "processed"
    label_dir = os.path.join(CLIPS_DIR, label)
    os.makedirs(label_dir, exist_ok=True)
    output_path = os.path.join(label_dir, os.path.basename(video_path))
    shutil.copy(video_path, output_path)
    return {label: output_path}


@app.post("/process")
def process_video(video_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT filename FROM videos WHERE id=?", (video_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Video not found")

    filename = row[0]
    video_path = os.path.join(UPLOAD_DIR, filename)

    results = run_pipeline(video_path)

    for label, path in results.items():
        cur.execute(
            "INSERT INTO clips (video_id, label, filepath) VALUES (?, ?, ?)",
            (video_id, label, path),
        )

    cur.execute(
        "UPDATE videos SET status=?, result=? WHERE id=?",
        ("processed", str(results), video_id),
    )
    conn.commit()
    conn.close()
    return {"id": video_id, "results": results}


@app.get("/clips")
def get_clips(label: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT filepath FROM clips WHERE label=?",
        (label,),
    )
    rows = cur.fetchall()
    conn.close()
    if not rows:
        raise HTTPException(status_code=404, detail="No clips for this label")

    files = [r[0] for r in rows]
    return {"label": label, "clips": files}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
