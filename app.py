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
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>VidSnap - YouTube Downloader</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
            body { background: #0f172a; color: #f8fafc; display: flex; flex-direction: column; align-items: center; min-height: 100vh; padding: 20px; }
            .container { width: 100%; max-width: 600px; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); margin-top: 40px; text-align: center; }
            h1 { color: #f43f5e; margin-bottom: 10px; font-size: 28px; }
            p.subtitle { color: #94a3b8; margin-bottom: 25px; font-size: 14px; }
            input[type="text"] { width: 100%; padding: 14px; font-size: 16px; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: #fff; margin-bottom: 15px; outline: none; transition: border-color 0.3s; }
            input[type="text"]:focus { border-color: #f43f5e; }
            button { width: 100%; background: #f43f5e; color: white; padding: 14px; font-size: 16px; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; transition: background 0.3s; }
            button:hover { background: #e11d48; }
            
            /* Ad Box Styling */
            .ad-box { width: 100%; background: #334155; border: 2px dashed #475569; padding: 20px; border-radius: 8px; margin-top: 25px; color: #94a3b8; font-size: 14px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>VidSnap</h1>
            <p class="subtitle">Download your favorite YouTube videos instantly</p>
            
            <form action="/download" method="POST">
                <input type="text" name="url" placeholder="Paste YouTube Video URL here..." required>
                <button type="submit">Download Video</button>
            </form>

            <!-- Ad Box Space -->
            <div class="ad-box">
                📢 Advertisement / Ad Space <br>
                <small>You can place your Google AdSense or Banner Ad code here</small>
            </div>
        </div>
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
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info_dict)
            
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
