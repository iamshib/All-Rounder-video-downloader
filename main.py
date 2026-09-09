from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os
import yt_dlp

app = FastAPI()
templates = Jinja2Templates(directory="templates")

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/get-info")
async def get_info(url: str = Form(...)):
    try:
        ydl_opts = {'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown Video')
            thumbnail = info.get('thumbnail', '')
        return JSONResponse({"success": True, "title": title, "thumbnail": thumbnail})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)})

@app.post("/download")
async def download_video(url: str = Form(...), quality: str = Form(...)):
    try:
        ydl_opts = {
            'format': quality,
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'restrictfilenames': True,
            'merge_output_format': 'mp4',
        }
        
        if 'bestaudio' in quality and 'bestvideo' not in quality:
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if 'bestaudio' in quality and 'bestvideo' not in quality:
                filename = os.path.splitext(filename)[0] + '.mp3'
            
        return FileResponse(filename, media_type='application/octet-stream', filename=os.path.basename(filename))
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)})