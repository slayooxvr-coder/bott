from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

html = """
<!DOCTYPE html>
<html>
<head>
    <title>Discord Bot Panel</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #0b0d11; color: #e2e8f0; font-family: 'Segoe UI', Arial, sans-serif; padding: 30px; min-height: 100vh; }
        h1 { font-size: 20px; font-weight: 700; color: #a78bfa; margin-bottom: 24px; letter-spacing: 0.02em; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; max-width: 900px; }
        .card { background: #161b22; border: 1px solid #2d3748; border-radius: 10px; padding: 20px; display: flex; flex-direction: column; gap: 14px; }
        .section-label { font-size: 11px; font-weight: 700; color: #8892a4; text-transform: uppercase; letter-spacing: 0.08em; }
        .field { display: flex; flex-direction: column; gap: 5px; }
        .field label { font-size: 12px; color: #8892a4; font-weight: 500; }
        .field input, .field textarea, .field select {
            background: #111827; border: 1px solid #2d3748; border-radius: 6px;
            color: #e2e8f0; font-size: 13px; padding: 8px 10px; outline: none;
            font-family: inherit; transition: border-color 0.15s; width: 100%;
        }
        .field input:focus, .field textarea:focus { border-color: #7c3aed; }
        .field textarea { resize: vertical; min-height: 90px; }
        .grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        .color-row { display: flex; align-items: center; gap: 8px; }
        .color-row input[type=color] { width: 36px; height: 36px; padding: 2px; border-radius: 6px; cursor: pointer; flex-shrink: 0; background: #111827; border: 1px solid #2d3748; }
        .color-row input[type=text] { flex: 1; }
        .btn-send { width: 100%; padding: 11px; background: #7c3aed; border: none; border-radius: 7px; color: white; font-size: 14px; font-weight: 700; cursor: pointer; transition: background 0.15s; }
        .btn-send:hover { background: #6d28d9; }
        .btn-send:disabled { background: #4c1d95; cursor: not-allowed; }
        .log { background: #111827; border: 1px solid #2d3748; border-radius: 6px; padding: 10px; font-size: 12px; font-family: 'Courier New', monospace; min-height: 50px; color: #8892a4; }
        .ok { color: #22c55e; } .err { color: #ef4444; }
        .divider { height: 1px; background: #2d3748; }
        /* Preview */
        .dc-msg { background: #1e2430; border-radius: 8px; padding: 14px; display: flex; gap: 12px; }
        .dc-avatar { width: 38px; height: 38px; border-radius: 50%; background: #7c3aed; display: flex; align-items: center; justify-content: center; font-weight: 700; color: white; font-size: 15px; flex-shrink: 0; }
        .dc-body { flex: 1; min-width: 0; }
        .dc-user { font-size: 13px; font-weight: 700; color: #a78bfa; }
        .dc-embed { margin-top: 8px; border-left: 4px solid #7c3aed; border-radius: 4px; background: #1a1f2e; padding: 10px 12px; display: flex; flex-direction: column; gap: 6px; }
        .dc-embed-title { font-size: 14px; font-weight: 700; color: #c4b5fd; }
        .dc-embed-desc { font-size: 13px; color: #cbd5e1; line-height: 1.5; word-break: break-word; white-space: pre-wrap; }
        .dc-embed-img { width: 100%; border-radius: 4px; max-height: 150px; object-fit: cover; display: none; }
        .dc-embed-footer { font-size: 11px; color: #8892a4; display: none; }
        .dc-btn { display: none; align-items: center; gap: 5px; padding: 6px 14px; background: #2d3748; border-radius: 4px; font-size: 12px; font-weight: 600; color: #e2e8f0; margin-top: 4px; align-self: flex-start; border: none; cursor: pointer; }
    </style>
</head>
<body>
<h1>Discord Bot Panel</h1>
<div class="grid">
  <div class="card">
    <div class="section-label">Configuration</div>
    <div class="field"><label>Token du bot</label><input type="password" id="token" placeholder="MTxx..."></div>
    <div class="field"><label>Channel ID</label><input type="text" id="channel" placeholder="123456789012345678"></div>
    <div class="divider"></div>
    <div class="section-label">Message</div>
    <div class="field"><label>Titre</label><input type="text" id="title" oninput="updatePreview()" placeholder="Titre..."></div>
    <div class="field"><label>Description</label><textarea id="desc" oninput="updatePreview()" placeholder="Contenu..."></textarea></div>
    <div class="grid2">
      <div class="field"><label>Couleur</label>
        <div class="color-row">
          <input type="color" id="colorpicker" value="#7c3aed" oninput="syncColor(this)">
          <input type="text" id="colorhex" value="#7c3aed" oninput="syncHex(this)">
        </div>
      </div>
      <div class="field"><label>Footer / Date</label><input type="text" id="footer" oninput="updatePreview()" placeholder="Aujourd'hui"></div>
    </div>
    <div class="field"><label>Image URL</label><input type="text" id="image" oninput="updatePreview()" placeholder="https://..."></div>
    <div class="divider"></div>
    <div class="section-label">Bouton</div>
    <div class="grid2">
      <div class="field"><label>Texte du bouton</label><input type="text" id="btn_text" oninput="updatePreview()" placeholder="Buy Here"></div>
      <div class="field"><label>Lien du bouton</label><input type="text" id="btn_url" oninput="updatePreview()" placeholder="https://..."></div>
    </div>
    <button class="btn-send" id="sendbtn" onclick="sendMessage()">Envoyer</button>
    <div class="log" id="log">En attente...</div>
  </div>

  <div class="card">
    <div class="section-label">Aperçu</div>
    <div class="dc-msg">
      <div class="dc-avatar">B</div>
      <div class="dc-body">
        <div class="dc-user">Mon Bot</div>
        <div class="dc-embed" id="embed" style="border-left-color:#7c3aed">
          <div class="dc-embed-title" id="prev-title">Titre</div>
          <div class="dc-embed-desc" id="prev-desc">Description...</div>
          <img class="dc-embed-img" id="prev-img" alt="">
          <div class="dc-embed-footer" id="prev-footer"></div>
          <button class="dc-btn" id="prev-btn"><span id="prev-btn-text">Buy Here</span> ↗</button>
        </div>
      </div>
    </div>
  </div>
</div>

<script>
function syncColor(el){ document.getElementById('colorhex').value=el.value; updatePreview(); }
function syncHex(el){ if(/^#[0-9a-fA-F]{6}$/.test(el.value)){ document.getElementById('colorpicker').value=el.value; updatePreview(); } }

function updatePreview(){
  document.getElementById('prev-title').textContent = document.getElementById('title').value || 'Titre';
  document.getElementById('prev-desc').textContent = document.getElementById('desc').value || 'Description...';
  document.getElementById('embed').style.borderLeftColor = document.getElementById('colorhex').value || '#7c3aed';
  const img = document.getElementById('image').value;
  const imgEl = document.getElementById('prev-img');
  imgEl.src = img; imgEl.style.display = img ? 'block' : 'none';
  const footer = document.getElementById('footer').value;
  const fEl = document.getElementById('prev-footer');
  fEl.textContent = footer ? '📅 ' + footer : '';
  fEl.style.display = footer ? 'block' : 'none';
  const btnText = document.getElementById('btn_text').value;
  const btnEl = document.getElementById('prev-btn');
  btnEl.style.display = btnText.trim() ? 'inline-flex' : 'none';
  document.getElementById('prev-btn-text').textContent = btnText;
}

async function sendMessage(){
  const token = document.getElementById('token').value.trim();
  const channelId = document.getElementById('channel').value.trim();
  if(!token || !channelId){ setLog('Token et Channel ID requis !', 'err'); return; }

  const color = parseInt((document.getElementById('colorhex').value||'#7c3aed').replace('#',''), 16);
  const payload = {
    token, channel_id: channelId,
    title: document.getElementById('title').value,
    description: document.getElementById('desc').value,
    color,
    footer: document.getElementById('footer').value,
    image: document.getElementById('image').value,
    button_text: document.getElementById('btn_text').value,
    button_url: document.getElementById('btn_url').value
  };

  const btn = document.getElementById('sendbtn');
  btn.disabled = true; btn.textContent = 'Envoi...';
  setLog('Envoi en cours...', '');

  try {
    const r = await fetch('/send', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
    const data = await r.json();
    if(data.ok){ setLog('✓ Message envoyé ! ID: ' + data.id, 'ok'); }
    else { setLog('✗ Erreur ' + data.status + ': ' + data.message, 'err'); }
  } catch(e) {
    setLog('✗ Erreur: ' + e.message, 'err');
  }
  btn.disabled = false; btn.textContent = 'Envoyer';
}

function setLog(msg, type){
  const el = document.getElementById('log');
  el.innerHTML = '<span class="'+(type==='ok'?'ok':type==='err'?'err':'')+'">' + msg + '</span>';
}
updatePreview();
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(html)

@app.route("/send", methods=["POST"])
def send():
    data = request.json
    token = data.get("token", "")
    channel_id = data.get("channel_id", "")

    embed = {
        "title": data.get("title", ""),
        "description": data.get("description", ""),
        "color": data.get("color", 0x7c3aed)
    }

    if data.get("footer"):
        embed["footer"] = {"text": f"📅 {data['footer']}"}

    if data.get("image"):
        embed["image"] = {"url": data["image"]}

    payload = {"embeds": [embed]}

    btn_text = data.get("button_text", "").strip()
    btn_url = data.get("button_url", "").strip()
    if btn_text and btn_url:
        payload["components"] = [
            {
                "type": 1,
                "components": [
                    {
                        "type": 2,
                        "style": 5,
                        "label": btn_text,
                        "url": btn_url
                    }
                ]
            }
        ]

    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json"
    }

    r = requests.post(
        f"https://discord.com/api/v10/channels/{channel_id}/messages",
        json=payload,
        headers=headers
    )

    if r.status_code in (200, 201):
        msg_id = r.json().get("id", "")
        return jsonify({"ok": True, "id": msg_id})
    else:
        try:
            err = r.json().get("message", r.text)
        except:
            err = r.text
        return jsonify({"ok": False, "status": r.status_code, "message": err})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
