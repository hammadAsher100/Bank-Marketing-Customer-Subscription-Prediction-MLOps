# 🏠 Local Testing Guide

## Prerequisites

- ✅ Docker Desktop installed and running
- ✅ Git installed
- ✅ At least 4GB RAM available
- ✅ 5GB free disk space

---

## 🚀 Quick Start (5 Minutes)

### **Step 1: Start Docker Desktop**
1. Open Docker Desktop application (Windows)
2. Wait for Docker to start (green icon in system tray)
3. Verify: Open PowerShell and run `docker --version`

### **Step 2: Clone Repository (If not already done)**
```bash
cd "D:\Projects\Website Projects"
cd BankMarketingTermDeposit_Prediction
```

### **Step 3: Start Application**
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

Expected output:
```
NAME            IMAGE                                       STATUS
mlops-api       hammadasher/mlops-saylani-api:latest       Up 10 seconds
mlops-frontend  hammadasher/mlops-saylani-frontend:latest  Up 10 seconds
```

### **Step 4: Access Application**

Open in your browser:
- **API Documentation:** http://localhost:8000/docs
- **API Health Check:** http://localhost:8000/health
- **Streamlit Frontend:** http://localhost:8501

---

## ✅ Test the Application

### **1. Health Check**
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "lgbm_loaded": true,
  "xgb_loaded": true,
  "mlflow_db": false
}
```

### **2. Quick API Test**
```bash
# Run the test script
python test_api_quick.py
```

Expected output:
```
Testing health endpoint...
Status: 200
Response: {'status': 'ok', 'lgbm_loaded': True, ...}

Testing prediction with LightGBM...
Status: 200
Response: {'prediction': 0, 'probability': 0.0515, ...}
```

### **3. Test in Browser**

#### API Documentation (Swagger UI)
1. Go to: http://localhost:8000/docs
2. Expand `/predict` endpoint
3. Click "Try it out"
4. Use sample data:
```json
{
  "age": 35,
  "job": "management",
  "marital": "married",
  "education": "tertiary",
  "default": "no",
  "balance": 1500,
  "housing": "yes",
  "loan": "no",
  "contact": "cellular",
  "day": 15,
  "month": "may",
  "duration": 300,
  "campaign": 2,
  "pdays": -1,
  "previous": 0,
  "poutcome": "unknown",
  "model_type": "lgbm"
}
```
5. Click "Execute"
6. Check response shows prediction

#### Streamlit Frontend
1. Go to: http://localhost:8501
2. Navigate to "🔮 Predict" page
3. Fill in customer details
4. Click "🔮 Get Prediction"
5. Verify prediction result shows

---

## 📊 View Logs

### **All Logs**
```bash
docker-compose logs
```

### **API Logs Only**
```bash
docker-compose logs api
```

### **Frontend Logs Only**
```bash
docker-compose logs frontend
```

### **Follow Logs (Real-time)**
```bash
docker-compose logs -f
# Press Ctrl+C to stop
```

---

## 🛑 Stop Application

```bash
# Stop services (containers remain)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove everything (including volumes)
docker-compose down -v
```

---

## 🔄 Update and Restart

### **After Code Changes**
```bash
# Rebuild images
docker-compose build

# Restart services
docker-compose up -d
```

### **Pull Latest Images from Docker Hub**
```bash
# Pull latest images
docker-compose pull

# Restart with new images
docker-compose up -d
```

---

## 🐛 Troubleshooting

### **Problem: Docker Desktop not starting**
- **Solution 1:** Restart Docker Desktop
- **Solution 2:** Restart your computer
- **Solution 3:** Check if WSL2 is installed (required for Docker Desktop)

### **Problem: Port already in use**
```bash
# Check what's using port 8000
netstat -ano | findstr :8000

# Kill the process (use PID from above)
taskkill /PID <PID> /F

# Or change ports in docker-compose.yml
```

### **Problem: Containers won't start**
```bash
# Check logs for errors
docker-compose logs

# Remove old containers
docker-compose down
docker-compose up -d

# Force recreate
docker-compose up -d --force-recreate
```

### **Problem: Can't access localhost:8000 or localhost:8501**
- Check if Docker containers are running: `docker-compose ps`
- Check if ports are mapped correctly: `docker ps`
- Try http://127.0.0.1:8000 or http://127.0.0.1:8501
- Check firewall settings

### **Problem: Models not loading**
```bash
# Check if model files exist
ls data_and_model/models/*.pkl

# Reinitialize models
python initialize_models.py

# Restart containers
docker-compose restart
```

---

## 💻 Development Mode

### **Run Without Docker (For Development)**

```bash
# Install dependencies
pip install -r requirements-backend.txt
pip install -r requirements-frontend.txt

# Terminal 1: Start API
python -m uvicorn src.serving.api:app --reload --port 8000

# Terminal 2: Start Streamlit
streamlit run streamlit_app.py --server.port 8501

# Access:
# API: http://localhost:8000/docs
# Frontend: http://localhost:8501
```

---

## 🔍 Verify Everything Works

### **Checklist:**
- [ ] Docker Desktop is running
- [ ] `docker-compose ps` shows 2 containers running
- [ ] http://localhost:8000/health returns OK
- [ ] http://localhost:8000/docs loads Swagger UI
- [ ] http://localhost:8501 loads Streamlit app
- [ ] Can make predictions via API
- [ ] Can make predictions via Streamlit UI
- [ ] No errors in `docker-compose logs`

---

## 📱 Quick Commands Reference

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Rebuild
docker-compose build

# Pull latest
docker-compose pull

# Test API
curl http://localhost:8000/health
python test_api_quick.py
```

---

## ✨ What's Next?

Once local testing is successful:
1. ✅ Everything works locally
2. 🚀 Deploy to AWS (see `AWS_FREE_TIER_DEPLOYMENT.md`)
3. 🌐 Share your public URL
4. 📊 Monitor usage and performance

---

## 🎯 Success Criteria

Your local deployment is successful if:
- ✅ Both containers running (`docker-compose ps`)
- ✅ Health endpoint returns 200 OK
- ✅ LightGBM and XGBoost models loaded
- ✅ Streamlit UI accessible and working
- ✅ Can make predictions successfully
- ✅ No error messages in logs

**If all checkmarks are green, you're ready to deploy to AWS!** 🚀

---

**Last Updated:** 2026-06-19
