# 🚀 Deployment Guide — Streamlit Cloud + Render

## ✅ Pre-Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] `app_render.py` exists in project root
- [ ] `requirements-frontend.txt` and `requirements-backend.txt` created
- [ ] `.streamlit/config.toml` and `.streamlit/secrets.toml` exist
- [ ] Render and Streamlit Cloud accounts created

---

## Option 1: Deploy Backend on Render (Recommended)

### Step 1: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub account
3. Authorize Render to access your repositories

### Step 2: Deploy Backend Service
1. Click **"New +"** → **"Web Service"**
2. Select your GitHub repository (BankMarketingTermDeposit_Prediction)
3. Configure settings:
   - **Name**: `bank-marketing-api`
   - **Environment**: Python 3
   - **Build Command**: `bash render-build.sh`
   - **Start Command**: `python app_render.py`
   - **Plan**: Free (upgradeable)

4. Click **"Create Web Service"**
5. Wait for deployment (5-10 minutes on first run - models are trained during build)
6. **Copy your backend URL** from the dashboard (e.g., `https://bank-marketing-api-xxx.onrender.com`)
7. Test it: Visit `https://bank-marketing-api-xxx.onrender.com/health`
   - Should return: `{"status": "healthy", "models": {"lgbm": true, "xgb": true}}`

---

## Option 2: Deploy Frontend on Streamlit Cloud

### Step 1: Create Streamlit Cloud Account
1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Authorize Streamlit to access your repositories

### Step 2: Deploy App
1. Click **"Create app"**
2. Configure:
   - **Repository**: Select your repo
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`

3. Click **"Deploy"**
4. Wait 2-3 minutes for deployment

### Step 3: Add Backend URL to Secrets
1. Go to your app on Streamlit Cloud
2. Click **"☰" (menu)** → **"Settings"** → **"Secrets"**
3. Add this exactly:
   ```
   API_URL = "https://bank-marketing-api-xxx.onrender.com"
   ```
   *(Replace `xxx` with your actual Render URL)*

4. Click **"Save"**
5. Your app will redeploy automatically ✅

---

## Option 3: Deploy Both on Render Using Blueprint (All-in-One)

### Step 1: Push Changes to GitHub
```bash
git add -A
git commit -m "Update deployment configuration"
git push origin main
```

### Step 2: Deploy on Render
1. Go to https://render.com/deploy
2. Paste your GitHub repo URL
3. Click **"Deploy"**
4. Render will read `render.yaml` and deploy both services automatically

---

## ✅ Testing After Deployment

### Test Backend
```bash
curl https://bank-marketing-api-xxx.onrender.com/health
```
Should return:
```json
{
  "status": "healthy",
  "models": {"lgbm": true, "xgb": true}
}
```

### Test Frontend
- Visit: `https://your-username-bank-marketing-frontend.streamlit.app`
- Fill in some customer data
- Click "Predict"
- Should see prediction result ✅

---

## ❌ Troubleshooting

### Issue: "API is not connected" on Streamlit
**Solution:**
1. Check Streamlit Secrets are set correctly
   - Go to Settings → Secrets
   - Verify API_URL matches your Render backend URL
   - No trailing slashes!

2. Check backend is running
   - Visit `https://bank-marketing-api-xxx.onrender.com/health`
   - If error, check Render dashboard logs

3. Check CORS is enabled
   - Backend (`src/serving/api.py`) should have CORSMiddleware
   - Should allow all origins for Streamlit Cloud

### Issue: Render build fails
**Solution:**
1. Check you're using correct requirements file:
   - Backend: `requirements-backend.txt`
   - Frontend: `requirements-frontend.txt` (on Streamlit Cloud)

2. Check `app_render.py` exists in root directory

3. View build logs in Render dashboard

### Issue: PySpark/DVC install fails
**Solution:**
- These are only needed for backend
- Frontend uses lightweight `requirements-frontend.txt`
- Ensure Streamlit Cloud uses correct requirements

---

## 📊 Environment Variables

| Service | Variable | Value |
|---|---|---|
| Streamlit Cloud | `API_URL` | `https://bank-marketing-api-xxx.onrender.com` |
| Render Backend | `PORT` | `8000` (auto) |
| Local Dev | `API_URL` | `http://localhost:8000` |

---

## 🔄 Updating After Deployment

### Update Backend
```bash
git add src/
git commit -m "Update backend logic"
git push origin main
```
Render will automatically rebuild and redeploy.

### Update Frontend
```bash
git add streamlit_app.py
git commit -m "Update dashboard UI"
git push origin main
```
Streamlit Cloud will automatically redeploy.

---

## 🚀 Next Steps After Live Deployment

1. **Monitor Services**
   - Set up email alerts in Render for downtime
   - Monitor response times

2. **Add Custom Domain** (Optional)
   - Render: Add domain in Settings
   - Streamlit: Premium feature

3. **Set Up Retraining** (Optional)
   - GitHub Actions: Create scheduled workflows
   - Auto-retrain model weekly/daily

4. **Add Authentication** (Optional)
   - Streamlit: Use `streamlit-authenticator`
   - Render: API key validation

---

## 📞 Support URLs

- Render Dashboard: https://dashboard.render.com
- Streamlit Cloud: https://share.streamlit.io
- Backend Health: `https://bank-marketing-api-xxx.onrender.com/health`
- Backend Docs: `https://bank-marketing-api-xxx.onrender.com/docs`
- Frontend: `https://your-username-bank-marketing-frontend.streamlit.app`

