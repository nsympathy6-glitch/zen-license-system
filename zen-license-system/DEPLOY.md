# Zen License System - Deploy Guide

## Quick Start (Oracle Cloud Free)

### 1. Create GitHub Repo
1. Go to github.com → New repo → name it `zen-license-system`
2. Upload all files from this folder

### 2. Set Up Oracle Cloud
1. Go to cloud.oracle.com/free
2. Create account (use same email/password carefully)
3. Create VM instance:
   - Shape: VM.Standard.E1.Flex.ARM (ARM, 4 CPU, 24GB)
   - Image: Ubuntu 22.04
   - Add SSH key (or use cloud shell)
   - Open port 8000 in firewall rules

### 3. SSH Into Server
```bash
ssh -i your_key.pem ubuntu@YOUR_SERVER_IP
```

### 4. Install & Run
```bash
sudo apt update && sudo apt install -y python3-pip git
git clone https://github.com/YOUR_USERNAME/zen-license-system.git
cd zen-license-system
chmod +x start.sh
./start.sh
```

### 5. Update Launcher
Edit `zen-license-system/.env`:
```
LICENSE_SERVER_URL=http://YOUR_SERVER_IP:8000
```

### 6. Test
- Open launcher → Login with Discord → Should work
- Server runs 24/7 on Oracle Cloud
- Your PC can be off
