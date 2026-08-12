from math import hypot
from xml.sax.saxutils import escape

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field


app = FastAPI(title="Upstate Command Analysis Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENCOMMAND_REPO_URL = "https://github.com/tomdoyo/open-command"


class CommandRequest(BaseModel):
    player: str = Field(..., min_length=1)
    date: str = Field(..., min_length=1)
    pitch_type: str = "Pitch"
    command: str = "Command"
    target_x: float
    target_z: float
    actual_x: float
    actual_z: float
    velocity: float | None = None


def point_to_svg(x_in: float, z_in: float, left: float, top: float, width: float, height: float) -> tuple[float, float]:
    px = left + ((x_in + 17.0) / 34.0) * width
    py = top + ((48.0 - z_in) / 42.0) * height
    return px, py


def command_svg(payload: CommandRequest, miss: float) -> str:
    zone_x, zone_y, zone_w, zone_h = 84, 86, 180, 260
    tx, ty = point_to_svg(payload.target_x, payload.target_z, zone_x, zone_y, zone_w, zone_h)
    ax, ay = point_to_svg(payload.actual_x, payload.actual_z, zone_x, zone_y, zone_w, zone_h)
    velo = "-" if payload.velocity is None else f"{payload.velocity:.1f} mph"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="960" height="540" viewBox="0 0 960 540">
  <rect width="960" height="540" fill="#061d16"/>
  <rect width="960" height="64" fill="#006747"/>
  <text x="28" y="42" fill="white" font-family="Arial" font-size="28" font-weight="900">UPSTATE BULLPEN COMMAND</text>
  <text x="650" y="40" fill="#c8a951" font-family="Arial" font-size="16" font-weight="800">OpenCommand-style result</text>
  <rect x="36" y="86" width="320" height="396" rx="14" fill="#07110d" stroke="#cfd8d2"/>
  <rect x="{zone_x}" y="{zone_y}" width="{zone_w}" height="{zone_h}" fill="none" stroke="white" stroke-width="4"/>
  <line x1="{zone_x + zone_w / 3}" y1="{zone_y}" x2="{zone_x + zone_w / 3}" y2="{zone_y + zone_h}" stroke="white" opacity=".3"/>
  <line x1="{zone_x + 2 * zone_w / 3}" y1="{zone_y}" x2="{zone_x + 2 * zone_w / 3}" y2="{zone_y + zone_h}" stroke="white" opacity=".3"/>
  <line x1="{zone_x}" y1="{zone_y + zone_h / 3}" x2="{zone_x + zone_w}" y2="{zone_y + zone_h / 3}" stroke="white" opacity=".3"/>
  <line x1="{zone_x}" y1="{zone_y + 2 * zone_h / 3}" x2="{zone_x + zone_w}" y2="{zone_y + 2 * zone_h / 3}" stroke="white" opacity=".3"/>
  <circle cx="{tx:.1f}" cy="{ty:.1f}" r="11" fill="#f6c445" stroke="white" stroke-width="3"/>
  <text x="{tx + 15:.1f}" y="{ty - 10:.1f}" fill="white" font-family="Arial" font-size="16" font-weight="800">Target</text>
  <circle cx="{ax:.1f}" cy="{ay:.1f}" r="11" fill="#40c4ff" stroke="white" stroke-width="3"/>
  <text x="{ax + 15:.1f}" y="{ay + 22:.1f}" fill="white" font-family="Arial" font-size="16" font-weight="800">Actual</text>
  <rect x="402" y="86" width="510" height="396" rx="14" fill="#f2f4f3"/>
  <text x="442" y="150" fill="#101828" font-family="Arial" font-size="34" font-weight="900">{escape(payload.player)}</text>
  <text x="442" y="190" fill="#667085" font-family="Arial" font-size="19" font-weight="800">{escape(payload.date)} · {escape(payload.pitch_type)} · {escape(payload.command)}</text>
  <text x="442" y="300" fill="#006747" font-family="Arial" font-size="82" font-weight="900">{miss:.1f} in</text>
  <text x="448" y="334" fill="#667085" font-family="Arial" font-size="22" font-weight="900">COMMAND MISS</text>
  <text x="448" y="392" fill="#667085" font-family="Arial" font-size="18" font-weight="800">Target</text>
  <text x="600" y="392" fill="#101828" font-family="Arial" font-size="18" font-weight="800">{payload.target_x:.1f}, {payload.target_z:.1f}</text>
  <text x="448" y="426" fill="#667085" font-family="Arial" font-size="18" font-weight="800">Actual</text>
  <text x="600" y="426" fill="#101828" font-family="Arial" font-size="18" font-weight="800">{payload.actual_x:.1f}, {payload.actual_z:.1f}</text>
  <text x="448" y="460" fill="#667085" font-family="Arial" font-size="18" font-weight="800">Velocity</text>
  <text x="600" y="460" fill="#101828" font-family="Arial" font-size="18" font-weight="800">{escape(velo)}</text>
</svg>"""


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/open-command/status")
def open_command_status() -> dict[str, object]:
    return {
        "status": "pipeline_source_connected",
        "source": OPENCOMMAND_REPO_URL,
        "automatic_video_scoring_ready": False,
        "reason": "The public OpenCommand repository ships the inference scripts, but its data folder is currently empty and the YOLO detection outputs/models are not included.",
        "available_now": [
            "OpenCommand-style target/actual command scoring",
            "Render backend command-miss API",
            "Coach app video overlay for marking target and actual pitch locations",
        ],
        "needed_for_full_automatic_scoring": [
            "Ball, glove, and strike-zone detections for each pitch video",
            "Play-by-play/Statcast-style pitch metadata",
            "Camera pose solve inputs",
            "The OpenCommand data tree described in data/<year>/",
        ],
    }


@app.get("/open-command", response_class=HTMLResponse)
def open_command_lab() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Upstate OpenCommand Lab</title>
  <style>
    :root{--up:#006747;--dark:#061d16;--gold:#c8a951;--ink:#101828;--muted:#667085;--card:#f2f4f3}
    *{box-sizing:border-box} body{margin:0;background:var(--up);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;color:var(--ink)}
    main{max-width:1080px;margin:0 auto;padding:18px}
    .hero{background:linear-gradient(135deg,#050b09,#073f2d);color:white;border-radius:18px;padding:20px;margin-bottom:14px;box-shadow:0 18px 50px rgba(0,0,0,.25)}
    h1{margin:0;font-size:30px} h2{margin:0 0 10px}.small{color:#d8e5df}.card{background:var(--card);border:1px solid #cfd8d2;border-radius:16px;padding:16px;margin:12px 0;box-shadow:0 8px 24px rgba(6,29,22,.18)}
    .stage{position:relative;background:#050b09;border-radius:16px;overflow:hidden;aspect-ratio:16/9;border:1px solid #b7c5bd}
    .zone{position:absolute;left:38%;top:21%;width:24%;height:50%;border:4px solid var(--gold);box-shadow:0 0 0 999px rgba(0,0,0,.12)}
    .zone:before,.zone:after{content:"";position:absolute;background:rgba(246,196,69,.35)}
    .zone:before{left:33%;top:0;bottom:0;width:1px;box-shadow:calc(33vw/12) 0 0 rgba(246,196,69,.35)}
    .zone:after{left:0;right:0;top:33%;height:1px;box-shadow:0 calc(50vh/6) 0 rgba(246,196,69,.35)}
    .circle{position:absolute;border-radius:50%;transform:translate(-50%,-50%);border:3px solid white}
    .target{left:50%;top:42%;width:38px;height:38px;background:rgba(255,255,255,.22)}
    .actual{left:56%;top:49%;width:46px;height:46px;background:rgba(0,103,71,.82);border-width:5px}
    .caption{position:absolute;left:12px;right:12px;bottom:12px;display:flex;gap:8px;flex-wrap:wrap}
    .pill{background:rgba(5,11,9,.78);color:#fff;border:1px solid rgba(255,255,255,.22);border-radius:999px;padding:8px 11px;font-weight:900;font-size:13px}
    .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
    code{background:#e4ebe7;border-radius:8px;padding:2px 5px} a{color:#006747;font-weight:900}
  </style>
</head>
<body>
<main>
  <section class="hero">
    <h1>Upstate OpenCommand Lab</h1>
    <p class="small">This Render backend is connected to the OpenCommand-style workflow. The coach app now marks target and actual pitch locations directly on video, then sends the command score to this service.</p>
  </section>
  <section class="card">
    <h2>OpenCommand-style View</h2>
    <div class="stage">
      <div class="zone"></div>
      <div class="circle target"></div>
      <div class="circle actual"></div>
      <div class="caption">
        <span class="pill">Yellow box: strike zone</span>
        <span class="pill">White: target</span>
        <span class="pill">Green: actual pitch</span>
        <span class="pill">Command miss: backend scored</span>
      </div>
    </div>
  </section>
  <section class="card">
    <h2>What Is Live Now</h2>
    <div class="grid">
      <div><strong>Video overlay</strong><p>Mark target and actual locations on top of your uploaded bullpen video.</p></div>
      <div><strong>Render scoring</strong><p>The app posts coordinates to <code>/analyze/command</code> and gets command miss back.</p></div>
      <div><strong>Player notes</strong><p>The score, video link, and command card still save back to the player's profile.</p></div>
    </div>
  </section>
  <section class="card">
    <h2>Why It Is Not Fully Automatic Yet</h2>
    <p>The public OpenCommand repo contains the inference pipeline, but not a ready web app and not the large detection data/model outputs needed to automatically find glove, ball, strike zone, camera pose, target, and actual pitch location from any new video.</p>
    <p>Source: <a href="https://github.com/tomdoyo/open-command" target="_blank" rel="noopener">tomdoyo/open-command</a></p>
  </section>
</main>
</body>
</html>"""


@app.post("/analyze/command")
def analyze_command(payload: CommandRequest) -> dict[str, object]:
    miss = hypot(payload.actual_x - payload.target_x, payload.actual_z - payload.target_z)
    return {
        "player": payload.player,
        "date": payload.date,
        "pitch_type": payload.pitch_type,
        "command_miss_inches": round(miss, 2),
        "target": {"x": payload.target_x, "z": payload.target_z},
        "actual": {"x": payload.actual_x, "z": payload.actual_z},
        "svg": command_svg(payload, miss),
    }
