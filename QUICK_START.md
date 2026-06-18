# MLOps Saylani - Quick Start Guide

## 🚀 Fastest Deployment Path (Recommended)

### Option A: Build on EC2 (5-10 minutes)

**Best for:** Large images, slow internet, or first-time deployment

1. **Setup AWS** (one-time):
   ```bash
   aws configure  # Enter your AWS credentials
   bash aws-setup.sh
   ```

2. **SSH into EC2**:
   ```bash
   ssh -i mlops-saylani-key.pem ec2-user@YOUR_EC2_IP
   ```

3. **Install Docker** (one-time):
   ```bash
   sudo yum update -y && sudo yum install -y docker git
   sudo service docker start
   sudo usermod -a -G docker ec2-user
   sudo mkdir -p /usr/local/lib/docker/cli-plugins
   sudo curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
     -o /usr/local/lib/docker/cli-plugins/docker-compose
   sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
   exit && ssh -i mlops-saylani-key.pem ec2-user@YOUR_EC2_IP
   ```

4. **Deploy**:
   ```bash
   git clone https://github.com/hammadAsher100/MLOps-Saylani.git
   cd MLOps-Saylani
   docker build -f Dockerfile.api -t hammadasher/mlops-saylani-api:latest .
   docker build -f Dockerfile.frontend -t hammadasher/mlops-saylani-frontend:latest .
   docker compose up -d
   ```

5. **Access**:
   - API: `http://YOUR_EC2_IP:8000/docs`
   - Frontend: `http://YOUR_EC2_IP:8501`

---

### Option B: Via DockerHub (10-30 minutes)

**Best for:** Fast internet, reusable images across multiple servers

1. **Push to DockerHub** (locally):
   ```cmd
   push-images.cmd
   ```
   Wait for completion (API image is 2.69GB)

2. **Setup AWS**:
   ```bash
   aws configure
   bash aws-setup.sh
   ```

3. **Deploy on EC2**:
   ```bash
   ssh -i mlops-saylani-key.pem ec2-user@YOUR_EC2_IP
   
   # Install Docker (see Option A step 3)
   
   # Deploy from DockerHub
   mkdir mlops-saylani && cd mlops-saylani
   curl -O https://raw.githubusercontent.com/hammadAsher100/MLOps-Saylani/main/docker-compose.prod.yml
   mv docker-compose.prod.yml docker-compose.yml
   docker compose pull
   docker compose up -d
   ```

---

## 📊 Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| Docker Images | ✅ Built | Both images ready locally |
| Frontend on DockerHub | ✅ Pushed | 1.15GB |
| API on DockerHub | ⏳ Pushing | 2.69GB - in progress |
| AWS CLI | ✅ Installed | Needs configuration |
| Deployment Scripts | ✅ Ready | All scripts created |

---

## 🛠️ Available Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `push-images.cmd` | Push to DockerHub | Option B deployment |
| `aws-setup.sh` | Create AWS infrastructure | First-time AWS setup |
| `build-on-ec2.sh` | Build on EC2 | Option A deployment |
| `deploy.sh` | Redeploy updates | After code changes |

---

## 📁 Key Files

- `AWS_DEPLOYMENT.md` - Complete deployment guide
- `DOCKERHUB_PUSH_FIX.md` - Solutions for push issues
- `DEPLOYMENT_STATUS.md` - Detailed progress tracker
- `docker-compose.yml` - Local development
- `docker-compose.prod.yml` - Production (pulls from DockerHub)

---

## 🔍 Troubleshooting

### Docker push timing out?
→ Use **Option A** (Build on EC2)

### AWS credentials not configured?
```bash
aws configure
```

### Can't SSH into EC2?
```bash
chmod 400 mlops-saylani-key.pem
```

### Services not starting?
```bash
docker compose logs
```

---

## 💡 Recommendations

1. **First deployment?** → Use Option A (Build on EC2)
2. **Multiple servers?** → Use Option B (DockerHub)
3. **Development?** → Use local `docker compose up`
4. **Production?** → Use EC2 with proper security groups

---

## 📞 Next Steps

1. Choose your deployment option (A or B)
2. Follow the steps above
3. Access your application
4. Monitor with `docker compose logs -f`

**Estimated Total Time:**
- Option A: 15-20 minutes
- Option B: 30-45 minutes (if push completes)
