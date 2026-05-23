# 🚀 Deployment Guide — Streamlit + Render

## Option 1: Deploy on Streamlit Cloud (Free, Easy) + Render (Backend)

### Step 1: Deploy Backend on Render

1. **Create Render Account**
   - Go to https://render.com
   - Sign up with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Select this repository

3. **Configure Backend Service**
   - **Name**: `bank-marketing-api`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app_render.py`
   - **Plan**: Free (or Starter for production)

4. **Add Environment Variables** (Settings → Environment)
   - `PORT`: `8000` (auto-set by Render)

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (~3-5 minutes)
   - Copy your backend URL: `https://bank-marketing-api-xxx.onrender.com`

### Step 2: Deploy Frontend on Streamlit Cloud

1. **Push Code to GitHub**
   ```bash
   git add .
   git commit -m "Add deployment configuration"
   git push origin main
   ```

2. **Create Streamlit Cloud Account**
   - Go to https://share.streamlit.io
   - Sign in with GitHub

3. **Deploy New App**
   - Click "New app"
   - Select your repository
   - Branch: `main`
   - Main file path: `streamlit_app.py`

4. **Add Secrets** (App settings → Secrets)
   ```toml
   API_URL = "https://bank-marketing-api-xxx.onrender.com"
   ```
   (Replace with your actual Render backend URL)

5. **Deploy**
   - Click "Deploy"
   - Wait for deployment (~2-3 minutes)
   - Your app is live! 🎉

---

## Option 2: Deploy Both on Render Using render.yaml

### Step 1: Create Render Account & Connect GitHub
- Go to https://render.com
- Sign up with GitHub

### Step 2: Deploy Using Blueprint
1. Click "New +" → "Blueprint"
2. Select your GitHub repository
3. Render will read `render.yaml` automatically
4. Configure settings and deploy both services at once

---

## Option 3: Deploy on Docker (Production)

### Using Docker Compose

```bash
docker-compose up --build
```

This runs:
- FastAPI Backend: `http://localhost:8000`
- Streamlit Frontend: `http://localhost:8501`

---

## Testing After Deployment

1. **Check Backend Health**
   ```
   https://bank-marketing-api-xxx.onrender.com/health
   ```
   Should return: `{"status": "healthy", "models": {"lgbm": true, "xgb": true}}`

2. **Check Streamlit Dashboard**
   ```
   https://bank-marketing-frontend-xxx.streamlit.app/
   ```

3. **Test Prediction**
   - Go to Streamlit dashboard
   - Fill in customer data
   - Click "Predict"
   - Should return prediction from backend ✅

---

## Troubleshooting

### Streamlit says "API is not connected"
- ❌ **Check 1**: Wrong API_URL in Streamlit secrets
  - Go to Streamlit Cloud → Settings → Secrets
  - Verify API_URL matches your Render backend URL
  - Format: `https://service-name-xxx.onrender.com` (no trailing slash)

- ❌ **Check 2**: Backend is not running
  - Go to Render dashboard
  - Check backend service status
  - Look at deployment logs for errors

- ❌ **Check 3**: CORS issue
  - The backend should have `CORS` enabled for all origins
  - Check `src/serving/api.py` line with `CORSMiddleware`

### Render says "Can't find main.py"
- ✅ **Solution**: Use `app_render.py` as start command
  - This file is in the project root
  - Render will find it automatically

### Models not loading
- Check if `data_and_model/models/` folder exists in git
- Models might need to be pushed with DVC:
  ```bash
  dvc push
  git push origin main
  ```

---

## Environment Variables Summary

| Variable | Local | Streamlit | Render |
|---|---|---|---|
| `API_URL` | `http://localhost:8000` | ✅ Set in Secrets | Auto-configured |
| `PORT` | `8000` | Auto | Auto (via app_render.py) |

---

## Next Steps After Deployment

1. ✅ Monitor logs in Render dashboard
2. ✅ Set up automatic redeployment on GitHub push
3. ✅ Add custom domain (optional, Render provides free subdomain)
4. ✅ Set up alerts for service downtime
5. ✅ Regular model retraining with GitHub Actions
