# 🚀 AWS Free Tier Deployment Guide

## 📋 Prerequisites

### Local Testing First
Before deploying to AWS, test locally:

```bash
# 1. Start Docker Desktop (Windows)
# Open Docker Desktop application

# 2. Run the application
docker-compose up

# 3. Test in browser
# API: http://localhost:8000/docs
# Frontend: http://localhost:8501

# 4. Stop when done
docker-compose down
```

---

## 🆓 AWS Free Tier Deployment (100% FREE for 12 Months)

### **What You Get FREE:**
- ✅ **EC2 t2.micro instance** - 750 hours/month (24/7 for 1 instance)
- ✅ **30 GB storage** - More than enough for Docker images
- ✅ **15 GB bandwidth** - Plenty for testing/small projects
- ✅ **1 year free** - Starting from account creation

### **Cost After Free Tier:**
- t2.micro instance: ~$8-10/month (if you keep it running 24/7)
- **Tip:** Stop instance when not in use = $0 cost

---

## 🛠️ Step-by-Step AWS Deployment

### **STEP 1: Create AWS Account**

1. **Go to:** https://aws.amazon.com/free/
2. **Click:** "Create a Free Account"
3. **Provide:**
   - Email address
   - Password
   - AWS account name
4. **Verify email**
5. **Enter payment information** (required but won't be charged)
6. **Select:** Basic Support (Free)

**⚠️ Important:** You need a credit/debit card for verification, but won't be charged if you stay within free tier limits.

---

### **STEP 2: Launch EC2 Instance**

#### A. Access EC2 Dashboard
1. Login to AWS Console: https://console.aws.amazon.com/
2. Search for "EC2" in the top search bar
3. Click "EC2" to open the dashboard
4. Click **"Launch Instance"** button

#### B. Configure Instance

**1. Name and Tags**
```
Name: mlops-bank-marketing
```

**2. Application and OS Images (Amazon Machine Image)**
- **Select:** Amazon Linux 2023 AMI
- **Architecture:** 64-bit (x86)
- ✅ **Free tier eligible** label should be visible

**3. Instance Type**
- **Select:** `t2.micro`
- ✅ **Free tier eligible**
- Specs: 1 vCPU, 1 GB RAM

**4. Key Pair (login)**
- Click **"Create new key pair"**
- **Name:** `mlops-saylani-key`
- **Key pair type:** RSA
- **Private key format:** .pem
- Click **"Create key pair"**
- ⚠️ **IMPORTANT:** Download will start automatically - **SAVE THIS FILE!** You can't download it again.
- Save to: `C:\Users\YourName\Downloads\mlops-saylani-key.pem`

**5. Network Settings**
- Click **"Edit"**
- **Allow SSH traffic from:** My IP (automatic)
- Click **"Add security group rule"**
  - **Type:** Custom TCP
  - **Port range:** 8000
  - **Source:** Anywhere (0.0.0.0/0)
  - **Description:** FastAPI
- Click **"Add security group rule"** again
  - **Type:** Custom TCP
  - **Port range:** 8501
  - **Source:** Anywhere (0.0.0.0/0)
  - **Description:** Streamlit

**Security Group Summary:**
```
Port 22   (SSH)        → My IP only
Port 8000 (API)        → Anywhere (0.0.0.0/0)
Port 8501 (Frontend)   → Anywhere (0.0.0.0/0)
```

**6. Configure Storage**
- **Size:** 20 GB (Free tier allows up to 30 GB)
- **Volume type:** gp3 (General Purpose SSD)
- ✅ Free tier eligible

**7. Advanced Details**
- Leave as default

**8. Summary**
- Review: Should show "Free tier eligible"
- Click **"Launch instance"**

#### C. Get Instance IP
1. Click **"View all instances"**
2. Wait for **Instance State** to show "Running" (1-2 minutes)
3. Select your instance
4. Copy **"Public IPv4 address"** (e.g., 18.223.xx.xx)
5. **Save this IP** - you'll need it!

---

### **STEP 3: Connect to EC2 and Setup**

#### A. Move Key File (Windows)
```bash
# Open PowerShell
cd ~
mkdir .ssh
move C:\Users\YourName\Downloads\mlops-saylani-key.pem .ssh\
```

#### B. Set Key Permissions (Windows)
```bash
# Right-click on mlops-saylani-key.pem
# Properties → Security → Advanced
# Click "Disable inheritance" → "Remove all inherited permissions"
# Click "Add" → "Select a principal" → Enter your username
# Check "Full control" → OK → Apply → OK
```

#### C. Connect via SSH
```bash
# Open PowerShell or Windows Terminal
cd ~/.ssh
ssh -i mlops-saylani-key.pem ec2-user@YOUR_EC2_IP

# Example:
# ssh -i mlops-saylani-key.pem ec2-user@18.223.45.67

# Type 'yes' when asked about fingerprint
```

You should now be connected to your EC2 instance!

---

### **STEP 4: Install Docker on EC2**

Run these commands one by one:

```bash
# Update system packages
sudo yum update -y

# Install Docker
sudo yum install docker -y

# Start Docker service
sudo service docker start

# Add ec2-user to docker group (so you don't need sudo)
sudo usermod -a -G docker ec2-user

# Verify Docker is running
docker --version

# Enable Docker to start on boot
sudo systemctl enable docker

# Log out and log back in for group changes
exit
```

Then reconnect:
```bash
ssh -i ~/.ssh/mlops-saylani-key.pem ec2-user@YOUR_EC2_IP
```

---

### **STEP 5: Install Docker Compose**

```bash
# Download Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make it executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
# Should show: Docker Compose version v2.24.0
```

---

### **STEP 6: Deploy Application**

```bash
# Create directory
mkdir -p ~/mlops-saylani
cd ~/mlops-saylani

# Clone your repository
git clone https://github.com/hammadAsher100/Bank-Marketing-Customer-Subscription-Prediction-MLOps.git .

# Pull Docker images from Docker Hub
docker-compose pull

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
# Press Ctrl+C to exit logs
```

---

### **STEP 7: Test Your Deployment**

#### From Your Local Browser:
```
API Documentation:  http://YOUR_EC2_IP:8000/docs
API Health Check:   http://YOUR_EC2_IP:8000/health
Streamlit Frontend: http://YOUR_EC2_IP:8501
```

Example:
```
http://18.223.45.67:8000/docs
http://18.223.45.67:8000/health
http://18.223.45.67:8501
```

#### Test Health Check:
```bash
# From your local machine
curl http://YOUR_EC2_IP:8000/health

# Should return:
# {"status":"ok","lgbm_loaded":true,"xgb_loaded":true,"mlflow_db":false}
```

---

## 🔧 Management Commands

### **On EC2 Instance (via SSH):**

```bash
# View running containers
docker-compose ps

# View logs
docker-compose logs -f api        # API logs
docker-compose logs -f frontend   # Frontend logs
docker-compose logs -f            # All logs

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Update application (after code changes)
cd ~/mlops-saylani
git pull origin main
docker-compose pull
docker-compose up -d

# Check Docker stats
docker stats
```

---

## 💰 Cost Management (Stay FREE!)

### **Monitor Your Usage**
1. Go to AWS Console → Billing Dashboard
2. Check **"Free Tier Usage"**
3. Monitor EC2 hours (should stay under 750 hrs/month)

### **Stop Instance When Not Using**
```bash
# AWS Console → EC2 → Instances
# Select your instance → Instance State → Stop

# To restart later:
# Instance State → Start
```

**Cost Savings:**
- Running 24/7: $0/month (free tier)
- Stop when not needed: Still $0, saves free hours for later

### **Free Tier Alerts**
1. AWS Console → Billing → Billing Preferences
2. Enable **"Receive Free Tier Usage Alerts"**
3. Enter your email
4. You'll get alerts when approaching limits

---

## 🛡️ Security Best Practices

### **1. Update Security Group (Restrict SSH)**
After initial setup:
```
Port 22 (SSH) → Change from "Anywhere" to "My IP"
```

### **2. Regular Updates**
```bash
# Login to EC2
sudo yum update -y

# Update Docker images
cd ~/mlops-saylani
docker-compose pull
docker-compose up -d
```

### **3. Use Environment Variables**
```bash
# Create .env file on EC2
cd ~/mlops-saylani
nano .env

# Add:
API_URL=http://YOUR_EC2_IP:8000
```

---

## 🔄 Continuous Deployment (Automated Updates)

### **Option 1: Manual Update Script**

Create on EC2:
```bash
nano ~/update-app.sh
```

Add:
```bash
#!/bin/bash
cd ~/mlops-saylani
echo "Pulling latest code..."
git pull origin main
echo "Pulling Docker images..."
docker-compose pull
echo "Restarting services..."
docker-compose up -d
echo "Deployment complete!"
docker-compose ps
```

Make executable:
```bash
chmod +x ~/update-app.sh
```

Use:
```bash
~/update-app.sh
```

### **Option 2: Webhook (Advanced)**
Setup GitHub webhook to auto-deploy on push (requires additional setup).

---

## 📊 Monitoring & Logs

### **Check Application Health**
```bash
# API health
curl http://YOUR_EC2_IP:8000/health

# Check if containers are running
docker-compose ps

# View resource usage
docker stats

# Check disk space
df -h
```

### **View Logs**
```bash
# Last 100 lines
docker-compose logs --tail=100

# Follow logs in real-time
docker-compose logs -f

# Specific service
docker-compose logs -f api
```

---

## 🐛 Troubleshooting

### **Problem: Can't connect to EC2**
```bash
# Check security group allows your IP
# AWS Console → EC2 → Security Groups → Edit inbound rules

# Verify instance is running
# AWS Console → EC2 → Instances → Check "Instance State"

# Check SSH key permissions
# Windows: Right-click key file → Properties → Security
```

### **Problem: Containers won't start**
```bash
# Check logs
docker-compose logs

# Check disk space
df -h

# Restart Docker
sudo service docker restart
docker-compose up -d
```

### **Problem: Out of memory**
```bash
# Check memory usage
free -h

# t2.micro has only 1GB RAM
# Solution: Stop instance, change to t3.micro (still free tier eligible)
```

### **Problem: Can't access website**
```bash
# Verify security group rules:
# Port 8000 and 8501 must be open to 0.0.0.0/0

# Check if services are running:
docker-compose ps

# Check logs for errors:
docker-compose logs
```

---

## 📱 Quick Reference

### **Your URLs (After Deployment):**
```
Replace YOUR_EC2_IP with your actual IP (e.g., 18.223.45.67)

API Docs:    http://YOUR_EC2_IP:8000/docs
Health:      http://YOUR_EC2_IP:8000/health
Frontend:    http://YOUR_EC2_IP:8501
```

### **Common Commands:**
```bash
# Connect to EC2
ssh -i ~/.ssh/mlops-saylani-key.pem ec2-user@YOUR_EC2_IP

# Update app
cd ~/mlops-saylani && git pull && docker-compose pull && docker-compose up -d

# View logs
docker-compose logs -f

# Stop app
docker-compose down

# Start app
docker-compose up -d

# Check status
docker-compose ps
```

---

## ✅ Deployment Checklist

- [ ] AWS account created
- [ ] EC2 instance launched (t2.micro)
- [ ] Key pair downloaded and saved
- [ ] Security groups configured (ports 22, 8000, 8501)
- [ ] SSH connection successful
- [ ] Docker installed on EC2
- [ ] Docker Compose installed
- [ ] Application cloned from GitHub
- [ ] Docker images pulled
- [ ] Services started with docker-compose
- [ ] Health check returns OK
- [ ] Frontend accessible in browser
- [ ] Free tier usage alerts enabled

---

## 🎓 Learning Resources

- **AWS Free Tier:** https://aws.amazon.com/free/
- **EC2 Documentation:** https://docs.aws.amazon.com/ec2/
- **Docker Documentation:** https://docs.docker.com/
- **Your GitHub Repo:** https://github.com/hammadAsher100/Bank-Marketing-Customer-Subscription-Prediction-MLOps

---

## 🆘 Need Help?

### **Check These First:**
1. AWS Free Tier Dashboard - Monitor usage
2. EC2 Instance State - Should be "running"
3. Security Groups - Ports must be open
4. Docker logs - `docker-compose logs`

### **Common Issues:**
- **Can't SSH:** Check key file permissions and security group
- **App not accessible:** Verify ports 8000/8501 are open
- **Out of memory:** t2.micro has only 1GB, may need to optimize
- **Free tier exceeded:** Check AWS billing dashboard

---

## 🎉 Success!

If you can access:
- ✅ `http://YOUR_EC2_IP:8000/health` - Returns OK
- ✅ `http://YOUR_EC2_IP:8501` - Shows Streamlit UI

**Congratulations! Your MLOps application is live on AWS Free Tier!** 🚀

---

**Created:** 2026-06-19  
**Updated:** 2026-06-19  
**Valid for:** AWS Free Tier (12 months from account creation)
