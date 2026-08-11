# Upstate Command Analysis Backend

This is the starter backend for the heavier OpenCommand-style workflow.

The current Netlify app can already make a semi-automatic command card in the browser. This backend is the next step: a Python service that can accept command calibration data now, and later grow into video/computer-vision processing with OpenCV/OpenCommand-style pipelines.

## Local Run

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

Open:

```text
http://localhost:8080/health
```

## Deploy Target

Good first hosts:

- Render Web Service
- Railway service
- Fly.io app
- Azure App Service or Container Apps if school Microsoft permissions/storage become part of it

## Render Deploy

This project includes a root-level `render.yaml` blueprint. Once the folder is in GitHub:

1. Open Render.
2. Choose **New +**.
3. Choose **Blueprint**.
4. Connect the GitHub repo.
5. Render should detect `render.yaml`.
6. Create the `upstate-command-analysis` web service.
7. After deploy, test:

```text
https://YOUR-RENDER-SERVICE.onrender.com/health
```

When that returns `{"status":"ok"}`, the backend is live.

## API

`POST /analyze/command`

```json
{
  "player": "Pitcher Name",
  "date": "2026-08-11",
  "pitch_type": "Fastball",
  "target_x": 1.2,
  "target_z": 32.5,
  "actual_x": -4.1,
  "actual_z": 29.4,
  "velocity": 88.6
}
```

Returns command miss in inches plus an SVG command card. A future version can accept video URLs/jobs and return analyzed overlays.
