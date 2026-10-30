import os
from flask import Flask, render_template_string, request, send_file, jsonify
import yt_dlp

app = Flask(__name__)
DOWNLOAD_DIR = "/data/data/com.termux/files/home/storage/shared/Download"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

HTML_TEMPLATE = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>VidSnap — YouTube Video Preview & Download</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#0b1020;color:#f5f7ff;font:16px/1.5 system-ui,Arial}.wrap{width:min(900px,92%);margin:auto}.top{padding:24px 0;font-size:25px;font-weight:900}.top span{color:#929cff}.hero{text-align:center;padding:24px 0}.hero h1{font-size:clamp(30px,6vw,46px);line-height:1.1;margin:0 0 12px}.hero p,.muted{color:#aab5d0}.panel{background:#141e35;border:1px solid #2b3957;border-radius:20px;padding:20px;margin:20px 0 30px}.label{display:block;font-weight:750;margin-bottom:9px}input{width:100%;padding:15px;background:#0b1428;border:1px solid #354563;border-radius:12px;color:white;font-size:15px}.btn{width:100%;padding:15px;border:0;border-radius:12px;color:white;font-weight:800;font-size:16px;background:linear-gradient(120deg,#6678ff,#9857f6);margin-top:12px;cursor:pointer}.btn:disabled{opacity:0.6;cursor:not-allowed}.preview{aspect-ratio:16/9;background:#080d18;border:1px dashed #526184;border-radius:14px;margin-top:17px;display:grid;place-items:center;overflow:hidden}.preview iframe{width:100%;height:100%;border:0}.placeholder{text-align:center;color:#aab5d0;padding:20px}.ads{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:18px 0}.ad{min-height:120px;border:1px dashed #637399;background:#101a30;border-radius:15px;display:flex;align-items:center;justify-content:center;flex-direction:column;text-align:center;padding:12px}.ad small{color:#aab5d0}.ad b{margin:6px}.adtag{font-size:10px;letter-spacing:1.3px;border:1px solid #4a5b7d;padding:3px 10px;border-radius:20px;color:#b5c1df}.title{font-size:19px;font-weight:850;margin:20px 0 10px}.qualities{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.q{background:#0d162a;border:1px solid #394968;border-radius:12px;padding:13px;color:white;font-weight:800;cursor:pointer}.q.active{background:#263260;border-color:#909cff}.note{font-size:13px;color:#bdc9e2;background:#101b31;border-left:3px solid #20c6a7;padding:13px;border-radius:9px;margin-top:15px}footer{text-align:center;color:#7887a8;padding:20px 0 35px;font-size:12px}@media(max-width:600px){.ads{grid-template-columns:1fr}.panel{padding:15px}}
</style></head>
<body><div class="wrap">
<div class="top">Vid<span>Snap</span></div>
<section class="hero"><h1>Preview & Download YouTube Videos.<br><span style="color:#9ba5ff">Any resolution, instantly.</span></h1><p>Paste any YouTube link below to preview and download.</p></section>
<main class="panel">
<label class="label" for="url">YouTube Video URL</label><input id="url" type="url" placeholder="Paste YouTube link here">
<button class="btn" id="previewBtn">Preview Video</button>
<div class="preview" id="preview"><div class="placeholder"><b>▶ Video preview</b><br>Paste a link above and tap Preview Video</div></div>
<div class="ads">
<div class="ad"><span class="adtag">ADVERTISEMENT 01</span><b>Ad space 1</b><small>Monetag ad code goes here</small></div>
<div class="ad"><span class="adtag">ADVERTISEMENT 02</span><b>Ad space 2</b><small>Second Monetag ad code goes here</small></div>
</div>
<div class="title">Choose quality</div>
<div class="qualities"><button class="q active" data-q="720p">720p</button><button class="q" data-q="1080p">1080p</button><button class="q" data-q="320p">320p</button></div>
<p class="muted" id="selected">Selected quality: 720p</p>
<button class="btn" id="downloadBtn">⬇ Download Video</button>
<div class="note">Enter any valid YouTube URL. Select your preferred quality and click Download to save the video file directly to your device.</div>
</main><footer>© 2026 VidSnap · All rights reserved.</footer></div>
<script>
const $=id=>document.getElementById(id);
function ytId(s){try{let u=new URL(s.trim()),id='';if(u.hostname==='youtu.be')id=u.pathname.slice(1).split('/')[0];else if(u.hostname.endsWith('youtube.com')){if(u.pathname==='/watch')id=u.searchParams.get('v')||'';else if(u.pathname.startsWith('/shorts/'))id=u.pathname.split('/')[2]||'';else if(u.pathname.startsWith('/embed/'))id=u.pathname.split('/')[2]||'';}return /^[\w-]{11}$/.test(id)?id:null}catch(e){return null}}

let selectedQuality = '720p';

$('previewBtn').onclick=()=>{
    let s=$('url').value.trim(), id=ytId(s);
    if(id){
        $('preview').innerHTML='<iframe src="https://www.youtube-nocookie.com/embed/'+id+'" title="YouTube preview" allowfullscreen></iframe>';
    } else {
        $('preview').innerHTML='<div class="placeholder">Please enter a valid YouTube URL.</div>';
    }
};

document.querySelectorAll('.q').forEach(b=>b.onclick=()=>{
    document.querySelectorAll('.q').forEach(x=>x.classList.remove('active'));
    b.classList.add('active');
    selectedQuality = b.dataset.q;
    $('selected').textContent='Selected quality: '+b.dataset.q;
});

$('downloadBtn').onclick=()=>{
    let s=$('url').value.trim();
    if(!ytId(s)){
        alert('Please enter a valid YouTube URL.');
        return;
    }
    
    $('downloadBtn').textContent = 'Processing & Downloading...';
    $('downloadBtn').disabled = true;

    fetch('/download', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ url: s, quality: selectedQuality })
    })
    .then(response => {
        if (!response.ok) throw new Error('Failed to download video.');
        return response.blob();
    })
    .then(blob => {
        let downloadUrl = window.URL.createObjectURL(blob);
        let a = document.createElement('a');
        a.href = downloadUrl;
        a.download = 'video.mp4';
        document.body.appendChild(a);
        a.click();
        a.remove();
        $('downloadBtn').textContent = '⬇ Download Video';
        $('downloadBtn').disabled = false;
    })
    .catch(err => {
        alert('Error downloading video. Make sure the URL is correct.');
        $('downloadBtn').textContent = '⬇ Download Video';
        $('downloadBtn').disabled = false;
    });
};
</script></body></html>'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/download', methods=['POST'])
def download_video():
    data = request.get_json()
    url = data.get('url')
    quality = data.get('quality', '720p')

    if quality == '1080p':
        ydl_opts = {
            'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
            'merge_output_format': 'mp4'
        }
    elif quality == '320p':
        ydl_opts = {
            'format': 'bestvideo[height<=320]+bestaudio/best[height<=320]',
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
            'merge_output_format': 'mp4'
        }
    else:
        ydl_opts = {
            'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
            'merge_output_format': 'mp4'
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if not filename.endswith('.mp4') and os.path.exists(filename.rsplit('.', 1)[0] + '.mp4'):
                filename = filename.rsplit('.', 1)[0] + '.mp4'
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
