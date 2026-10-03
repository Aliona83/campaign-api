# Skin Clinic Campaign Analysis – FastAPI + Render

## Project files
```
campaign-api/
├── main.py            # FastAPI app (analysis + /campaign-analysis endpoint)
├── data.csv           # skin_clinic_campaign.csv (10,000 customers)
├── requirements.txt   # Python packages
├── render.yaml        # Render deployment config
└── .gitignore
```

## Step 1 – Data (already set up)
`data.csv` is your `skin_clinic_campaign.csv`, and the column names in the
**CONFIG** block of `main.py` already match it. Nothing to change.

## Step 2 – Run it in Visual Studio Code
1. Install **Python** (3.10+) and the VS Code **Python** extension.
2. `File → Open Folder…` → choose `campaign-api`.
3. Open the terminal: `Terminal → New Terminal`, then run:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate

   pip install -r requirements.txt
   uvicorn main:app --reload
   ```
   (Windows PowerShell blocks activation? Run
   `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.)
4. Open in your browser:
   - http://127.0.0.1:8000/campaign-analysis → tables
   - http://127.0.0.1:8000/campaign-analysis?format=json → JSON
   - http://127.0.0.1:8000/docs → Swagger UI

## Step 3 – Push to GitHub
1. Create an empty repository on github.com (e.g. `campaign-api`).
2. In the VS Code terminal:
   ```bash
   git init
   git add .
   git commit -m "Campaign analysis FastAPI app"
   git branch -M main
   git remote add origin https://github.com/<your-username>/campaign-api.git
   git push -u origin main
   ```
   (Or use the **Source Control** tab → *Publish to GitHub*.)

## Step 4 – Deploy on Render
1. Sign in at https://render.com with GitHub.
2. **New + → Web Service** → select your `campaign-api` repo.
3. Settings:
   | Field | Value |
   |---|---|
   | Runtime | Python 3 |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
   | Instance Type | Free |
4. Click **Create Web Service** and wait for "Live" (2–5 min).
5. Your link is shown at the top, e.g.
   `https://campaign-analysis-api.onrender.com`

## Step 5 – Share the link
```
https://<your-service-name>.onrender.com/campaign-analysis
```
Note: free Render services sleep after inactivity – the first visit may take
~30–50 seconds to wake up.
