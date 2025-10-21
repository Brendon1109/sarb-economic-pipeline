# 🔧 Google Cloud CLI Installation Guide

## 🚨 **Current Issue**: `gcloud` command not recognized

### **Solution Steps:**

#### **1. Complete the Installation** (GUI Installer Running)
- Accept license agreement
- Keep default installation path: `C:\Program Files (x86)\Google\Cloud SDK\`
- **IMPORTANT**: Check these boxes:
  - ✅ Install bundled Python
  - ✅ Add gcloud to PATH  
  - ✅ Run `gcloud init`

#### **2. After Installation - Restart Terminal**
```powershell
# Close this PowerShell window and open a new one
exit
```

#### **3. Verify Installation**
```powershell
# Test if gcloud is now available
gcloud --version

# Should show something like:
# Google Cloud SDK 450.0.0
# bq 2.0.97
# core 2023.10.11
# gsutil 5.25
```

#### **4. If Still Not Working - Manual PATH Fix**
```powershell
# Add to PATH manually if installer didn't do it
$env:PATH += ";C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin"

# Verify
gcloud --version
```

#### **5. Alternative: Install via PowerShell** (If GUI installer fails)
```powershell
# Install using Chocolatey (if you have it)
choco install gcloudsdk

# OR install using winget
winget install Google.CloudSDK
```

## ✅ **Once gcloud Works - Continue Demo Setup**

```powershell
# 1. Authenticate
gcloud auth login

# 2. Set application credentials  
gcloud auth application-default login

# 3. Set project
gcloud config set project brendon-presentation

# 4. Verify setup
gcloud auth list
gcloud config get-value project

# 5. Run assessment setup
.\setup-assessment.ps1
```

## 🆘 **Troubleshooting**

### **If gcloud still not recognized after restart:**
1. Check installation directory exists:
   ```powershell
   Test-Path "C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
   ```

2. Manually add to PATH:
   ```powershell
   [Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin", [EnvironmentVariableTarget]::Machine)
   ```

3. Restart PowerShell as Administrator and try again

### **Alternative Installation Locations:**
- `C:\Users\%USERNAME%\AppData\Local\Google\Cloud SDK\`
- `C:\Program Files\Google\Cloud SDK\`

## 📞 **Need Help?**
Contact: mapindabrendon@gmail.com  
This is a common setup issue - don't worry, we'll get it working! 🚀