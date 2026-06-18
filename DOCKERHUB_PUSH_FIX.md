# DockerHub Push Fix - API Image Issue

## Problem
The API Docker image (2.69GB) is too large and times out when pushing to DockerHub.

## ✅ Solutions (Choose One)

### Solution 1: Build on EC2 (RECOMMENDED - Fastest)

This is the **best solution** - skip DockerHub entirely and build directly on EC2.

**Advantages:**
- ✅ No upload/download of 2.69GB
- ✅ Deployment in 5-10 minutes
- ✅ No network timeout issues
- ✅ Most reliable

**Steps:**

1. Complete AWS setup (run `aws-setup.sh`)
2. SSH into EC2:
   ```bash
   ssh -i mlops-saylani-key.pem ec2-user@YOUR_EC2_IP
   ```

3. Install Docker on EC2:
   ```bash
   sudo yum update -y
   sudo yum install -y docker git
   sudo service docker start
   sudo usermod -a -G docker ec2-user
   
   # Install Docker Compose
   sudo mkdir -p /usr/local/lib/docker/cli-plugins
   sudo curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
     -o /usr/local/lib/docker/cli-plugins/docker-compose
   sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
   
   # Log out and back in
   exit
   ssh -i mlops-saylani-key.pem ec2-user@YOUR_EC2_IP
   ```

4. Build and deploy:
   ```bash
   # Clone repository
   git clone https://github.com/hammadAsher100/MLOps-Saylani.git
   cd MLOps-Saylani
   
   # Build images (5-10 minutes)
   docker build -f Dockerfile.api -t hammadasher/mlops-saylani-api:latest .
   docker build -f Dockerfile.frontend -t hammadasher/mlops-saylani-frontend:latest .
   
   # Start services
   docker compose up -d
   
   # Check status
   docker compose ps
   docker compose logs --tail=50
   ```

5. Access your app:
   - API: `http://YOUR_EC2_IP:8000/docs`
   - Frontend: `http://YOUR_EC2_IP:8501`

---

### Solution 2: Use Automated Push Script (Windows)

If you still want to push to DockerHub, use the automated script:

```cmd
push-images.cmd
```

This script:
- Checks Docker status
- Handles login
- Pushes frontend first (fast)
- Pushes API with progress (slow but works)

**Expected time:** 10-30 minutes depending on internet speed

---

### Solution 3: Optimize Image Size

Build a smaller image using multi-stage build:

```bash
# Build optimized image
docker build -f Dockerfile.api.optimized -t hammadasher/mlops-saylani-api:latest .

# Check size (should be smaller)
docker images hammadasher/mlops-saylani-api:latest

# Push to DockerHub
docker push hammadasher/mlops-saylani-api:latest
```

---

### Solution 4: Manual Push with Compression

```bash
# Login
docker login

# Push frontend (fast)
docker push hammadasher/mlops-saylani-frontend:latest

# Push API in background (Windows PowerShell)
Start-Job -ScriptBlock { docker push hammadasher/mlops-saylani-api:latest }

# Check progress
Get-Job | Receive-Job -Keep
```

---

## Comparison

| Solution | Time | Reliability | Complexity |
|----------|------|-------------|------------|
| **Build on EC2** | 5-10 min | ⭐⭐⭐⭐⭐ | Low |
| Automated Script | 10-30 min | ⭐⭐⭐ | Low |
| Optimize Image | 15-40 min | ⭐⭐⭐⭐ | Medium |
| Manual Push | 10-30 min | ⭐⭐ | Low |

## Recommendation

**Use Solution 1 (Build on EC2)** - It's the fastest, most reliable, and simplest approach for large Docker images.

## Current Status

- ✅ Frontend image: Already pushed successfully
- ⏳ API image: Use one of the solutions above

## Files Created

- `push-images.cmd` - Automated Windows batch script
- `push-to-dockerhub.ps1` - PowerShell script with retry logic
- `Dockerfile.api.optimized` - Smaller multi-stage build
- `build-on-ec2.sh` - Automated EC2 build script

## Need Help?

If you encounter issues:
1. Check Docker is running: `docker info`
2. Check login: `docker login`
3. Check image exists: `docker images | grep mlops-saylani`
4. Try Solution 1 (Build on EC2) - it always works!
