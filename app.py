import os
from flask import Flask, render_template, request, send_file, redirect, url_for
import yt_dlp

app = Flask(__name__)

DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>VidSnap - YouTube Downloader</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; background: #0f172a; color: #fff; text-align: center; padding: 50px; }
            input { width: 80%; max-width: 400px; padding: 12px; font-size: 16px; border-radius: 5px; border: none; margin-bottom: 10px; }
            button { background: #e11d48; color: white; padding: 12px 20px; font-size: 16px; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #be123c; }
        </style>
    </head>
    <body>
        <h1>VidSnap YouTube Downloader</h1>
        <form action="/download" method="POST">
            <input type="text" name="url" placeholder="Paste YouTube Video URL here..." required><br>
            <button type="submit">Download Video</button>
        </form>
    </body>
    </html>
    '''

@app.route('/download', methods=['POST'])
def download():
    video_url = request.form.get('url')
    if not video_url:
        return redirect(url_for('index'))
    
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = yd_opts and ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info_dict)
            
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
