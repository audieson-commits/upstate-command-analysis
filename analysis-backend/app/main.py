from math import hypot
from xml.sax.saxutils import escape

from fastapi import FastAPI
from pydantic import BaseModel, Field


app = FastAPI(title="Upstate Command Analysis Backend")


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
