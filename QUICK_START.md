# ⚡ Quick Start Guide

## 🏠 Local Testing (5 Minutes)

### Step 1: Start Docker Desktop
- Open Docker Desktop app
- Wait for it to start (green icon)

### Step 2: Start Application
```bash
docker-compose up -d
```

### Step 3: Access
- **API:** http://localhost:8000/docs
- **Frontend:** http://localhost:8501

### Step 4: Test
```bash
curl http://localhost:8000/health
python test_api_quick.py
```

### Step 5: Stop
```bash
docker-compose down
```

**📖 Full Guide:** See `LOCAL_TESTING.md`

---

## ☁️ AWS Free Tier Deployment (30 Minutes)

### Quick Overview:
1. **Create AWS account** → https://aws.amazon.com/free/
2. **Launch EC2 t2.micro** (FREE for 12 months)
3. **Download key pair** (.pem file)
4. **Open ports:** 22, 8000, 8501
5. **SSH to EC2:** `ssh -i key.pem ec2-user@YOUR_IP`
6. **Install Docker & Docker Compose**
7. **Clone & Run:** 
   ```bash
   git clone <your-repo>
   docker-compose up -d
   ```
8. **Access:** http://YOUR_EC2_IP:8501

**📖 Full Guide:** See `AWS_FREE_TIER_DEPLOYMENT.md`

---

## 📚 Documentation Index

| File | Description |
|------|-------------|
| **LOCAL_TESTING.md** | Complete local testing guide |
| **AWS_FREE_TIER_DEPLOYMENT.md** | Step-by-step AWS deployment |
| **PYSPARK_REMOVAL_SUMMARY.md** | Technical changes made |
| **DEPLOYMENT_CHECKLIST.md** | Deployment checklist |
| **GITHUB_DEPLOYMENT_STATUS.md** | GitHub sync status |
| **FINAL_STATUS.md** | Overall project status |

---

## 🆘 Quick Help

### Local Issues:
- **Docker not starting?** Restart Docker Desktop
- **Port busy?** Check `netstat -ano | findstr :8000`
- **Containers won't start?** Check logs: `docker-compose logs`

### AWS Issues:
- **Can't connect?** Check security group (ports 22, 8000, 8501)
- **SSH fails?** Verify key file permissions
- **Website not loading?** Check EC2 instance is running

---

## ✅ Success Checklist

### Local Testing:
- [ ] Docker Desktop running
- [ ] `docker-compose ps` shows 2 containers
- [ ] Health check returns OK
- [ ] Can access http://localhost:8501

### AWS Deployment:
- [ ] EC2 instance launched (t2.micro)
- [ ] Security groups configured
- [ ] Can SSH to instance
- [ ] Docker installed
- [ ] Application running
- [ ] Can access http://YOUR_EC2_IP:8501

---

## 🎯 What You Get

### Features:
- ✅ **2 ML Models:** LightGBM & XGBoost
- ✅ **REST API:** FastAPI with Swagger docs
- ✅ **Web UI:** Streamlit dashboard
- ✅ **MLflow Integration:** Experiment tracking
- ✅ **Production Ready:** Docker containers
- ✅ **Free Hosting:** AWS free tier eligible

### Performance:
- **Startup Time:** <5 seconds
- **Memory Usage:** ~1.5 GB
- **Docker Image:** ~1.5 GB total
- **Models:** LightGBM (fast), XGBoost (accurate)

---

## 🚀 Next Steps

1. **Test Locally:**
   ```bash
   docker-compose up -d
   ```

2. **Deploy to AWS:**
   - Follow `AWS_FREE_TIER_DEPLOYMENT.md`
   - Get your public IP
   - Share with the world!

3. **Monitor:**
   - Check AWS Free Tier usage
   - View logs: `docker-compose logs`
   - Stop when not needed to save resources

---

## 📱 Quick Commands

```bash
# Local
docker-compose up -d              # Start
docker-compose down               # Stop
docker-compose logs -f            # View logs
curl http://localhost:8000/health # Test

# AWS
ssh -i key.pem ec2-user@IP        # Connect
cd ~/mlops-saylani                # Go to app
docker-compose up -d              # Start
docker-compose logs -f            # View logs
```

---

## 🎉 You're Ready!

- 📖 Read the detailed guides
- 🏠 Test locally first
- ☁️ Deploy to AWS free tier
- 🌐 Share your ML app with the world!

**Good luck! 🚀**

---

**Repository:** https://github.com/hammadAsher100/Bank-Marketing-Customer-Subscription-Prediction-MLOps
