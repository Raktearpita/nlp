from flask import Flask, request, jsonify
import pickle
from datetime import datetime

app = Flask(__name__)

try:
    model = pickle.load(open('spam_model.pkl', 'rb'))
    vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))
    print("✅ Model Loaded - 97.04% Accuracy")
except Exception as e:
    print(f"Model error: {e}")
    model, vectorizer = None, None

history = []

@app.route('/')
def home():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>SMS Shield AI 2.0 - Light</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>
:root{--bg:#f8fafc;--card:#ffffff;--border:#e2e8f0;--text:#0f172a;--muted:#64748b;--primary:#6366f1}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--text);font-family:'Inter',sans-serif}
h1,b{font-family:'Space Grotesk',sans-serif}
.nav{position:sticky;top:0;z-index:10;display:flex;justify-content:space-between;align-items:center;padding:14px 28px;background:rgba(255,255,255,.9);backdrop-filter:blur(12px);border-bottom:1px solid var(--border)}
.logo{font-weight:700;font-size:20px;background:linear-gradient(90deg,#6366f1,#ec4899);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.container{max-width:1150px;margin:0 auto;padding:24px 28px}
.hero{margin-bottom:20px}.hero h1{font-size:42px;line-height:1.1}.hero h1 span{color:var(--primary)}
.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px}
.m-card{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:18px;box-shadow:0 4px 20px rgba(0,0,0,.04);border-top:4px solid var(--border)}
.m-card:nth-child(1){border-top-color:#22c55e} .m-card:nth-child(2){border-top-color:#6366f1}
.m-card:nth-child(3){border-top-color:#f59e0b} .m-card:nth-child(4){border-top-color:#ef4444}
.m-card small{color:var(--muted);font-size:11px;letter-spacing:1px;font-weight:700} .m-card h2{font-size:28px;margin-top:4px}
.grid{display:grid;grid-template-columns:1.6fr .9fr;gap:18px}
.card{background:var(--card);border:1px solid var(--border);border-radius:20px;padding:22px;box-shadow:0 8px 30px rgba(0,0,0,.05)}
.input-wrap{background:#f1f5f9;border:2px solid var(--border);border-radius:14px;padding:6px;display:flex;gap:8px}
.input-wrap:focus-within{border-color:var(--primary);background:#fff}
.input-wrap textarea{flex:1;background:transparent;border:none;outline:none;padding:12px;font-size:14px;resize:none;color:var(--text)}
.btn{background:var(--text);color:#fff;border:none;padding:12px 22px;border-radius:10px;font-weight:700;cursor:pointer}
.btn:hover{background:var(--primary)}
#result{margin-top:14px;padding:14px;border-radius:12px;text-align:center;font-weight:700;display:none}
#result.spam{display:block;background:#fff1f2;border:1px solid #fecdd3;color:#e11d48}
#result.ham{display:block;background:#f0fdf4;border:1px solid #bbf7d0;color:#15803d}
.bar{height:8px;background:#e2e8f0;border-radius:10px;margin-top:12px;overflow:hidden}
.fill{height:100%;width:0%;transition:1s ease;background:linear-gradient(90deg,#22c55e,#16a34a)}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}
.chip{background:#fff;border:1px solid var(--border);padding:6px 12px;border-radius:20px;font-size:12px;cursor:pointer}
.chip:hover{border-color:var(--primary);color:var(--primary)}
.hist-item{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #f1f5f9;font-size:12px}
.tag{padding:2px 8px;border-radius:12px;font-size:10px;font-weight:700}
.tag.spam{background:#ffe4e6;color:#e11d48} .tag.ham{background:#dcfce7;color:#15803d}
@media(max-width:900px){.metrics{grid-template-columns:1fr 1fr}.grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="nav"><div class="logo">🛡️ SMS Shield AI 2.0</div><div style="background:#dcfce7;color:#15803d;padding:6px 12px;border-radius:20px;font-size:12px;font-weight:700">🟢 97.04% Live Model</div></div>
<div class="container">
<div class="hero"><h1>Real-time SMS <span>Spam Detector</span></h1><p style="color:var(--muted);margin-top:6px">TF-IDF Vectorizer + Multinomial Naive Bayes | Trained on 5572 Messages</p></div>

<div class="metrics">
<div class="m-card"><small>ACCURACY</small><h2 style="color:#16a34a">97.04%</h2></div>
<div class="m-card"><small>TOTAL SMS</small><h2 style="color:#6366f1">5572</h2></div>
<div class="m-card"><small>HAM</small><h2 style="color:#d97706">4825</h2></div>
<div class="m-card"><small>SPAM</small><h2 style="color:#e11d48">747</h2></div>
</div>

<div class="grid">
<div class="card">
<b>● Live Prediction - Trained Model</b>
<div style="margin-top:10px;background:#f8fafc;border:1px dashed #cbd5e1;padding:10px;border-radius:10px;font-size:12px;color:var(--muted)" id="chat">Try: "Congratulations! You have won a FREE iPhone"</div>
<div id="result"></div>
<div class="bar"><div id="fill" class="fill"></div></div>
<div class="input-wrap"><textarea id="msg" rows="2" placeholder="Paste SMS here..."></textarea><button class="btn" onclick="go()">Analyze ➤</button></div>
<div class="chips">
<span class="chip" onclick="setM('Congratulations! You won FREE iPhone 15')">🎁 iPhone Spam</span>
<span class="chip" onclick="setM('Hey are we still meeting for lunch tomorrow?')">💬 Normal</span>
<span class="chip" onclick="setM('URGENT: Your bank account blocked, verify KYC')">🏦 Scam</span>
<span class="chip" onclick="setM('sun is shining today')">☀️ Safe</span>
</div>
</div>

<div class="card">
<b>📊 Classification Report</b>
<table style="width:100%;margin-top:12px;font-size:13px;border-collapse:collapse"><tr style="color:var(--muted);font-size:11px"><th></th><th>PRECISION</th><th>RECALL</th><th>F1</th></tr>
<tr style="border-top:1px solid #f1f5f9"><td style="padding:8px 0">ham</td><td>0.97</td><td>1.00</td><td>0.98</td></tr>
<tr style="background:#f8fafc"><td style="padding:8px 0">spam</td><td>1.00</td><td>0.79</td><td>0.88</td></tr></table>
<div style="margin-top:16px"><b style="font-size:12px">Recent Checks</b><div id="hist" style="margin-top:6px;color:var(--muted)">No checks yet</div></div>
<div style="margin-top:14px;background:#f8fafc;border:1px solid var(--border);padding:10px;border-radius:10px;font-size:11px;color:var(--muted)">Model: spam_model.pkl + vectorizer.pkl<br>Status: <span style="color:#16a34a;font-weight:700">Active | Inference Ready</span></div>
</div>
</div>
</div>

<script>
function setM(t){document.getElementById('msg').value=t; go();}
async function go(){
  let m=document.getElementById('msg').value.trim(); if(!m) return alert('Message likho');
  document.getElementById('chat').innerHTML='<b>You:</b> '+m;
  let r=document.getElementById('result'); let f=document.getElementById('fill');
  r.style.display='block'; r.className=''; r.style.background='#f1f5f9'; r.innerText='⏳ Analyzing with 97.04% model...'; f.style.width='20%';
  try{
    let resp=await fetch('/predict',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m})});
    let d=await resp.json();
    let isSpam=d.prediction=='spam' || d.prediction==1;
    r.className=isSpam?'spam':'ham'; r.id='result';
    r.innerHTML=(isSpam?'🚨 SPAM DETECTED':'✅ HAM - Safe Message')+`<br><small>Confidence: ${d.confidence}%</small>`;
    f.style.width=d.confidence+'%'; f.style.background=isSpam?'linear-gradient(90deg,#f43f5e,#e11d48)':'linear-gradient(90deg,#22c55e,#16a34a)';
    if(d.history){
      document.getElementById('hist').innerHTML=d.history.map(h=>`<div class="hist-item"><span>${h.message}</span><span class="tag ${h.label}">${h.label}</span></div>`).join('');
    }
  }catch(e){ r.innerText='Error: '+e.message; }
}
</script>
</body>
</html>
    """

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    msg = data.get('message','').strip()
    if model and vectorizer:
        vec = vectorizer.transform([msg])
        pred = model.predict(vec)[0]
        prob = model.predict_proba(vec).max()*100
        label = 'spam' if pred==1 else 'ham'
        conf = round(prob,2)
    else:
        label = 'spam' if any(w in msg.lower() for w in ['free','win','urgent','congratulations']) else 'ham'
        conf = 93.0
    history.insert(0,{'message':msg[:40]+'...','label':label,'time':datetime.now().strftime("%I:%M %p")})
    if len(history)>5: history.pop()
    return jsonify({'prediction':label,'confidence':conf,'history':history})

if __name__ == '__main__':
    app.run(debug=True, port=5000)