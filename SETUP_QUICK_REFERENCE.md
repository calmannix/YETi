# YouTube API Setup - Quick Reference Card

## 🎯 What You Need

1. **Google Cloud Project** with YouTube APIs enabled
2. **OAuth credentials** saved as `credentials.json`
3. **Authorization** completed (creates `token.pickle`)

---

## ⚡ Quick Setup (5 Minutes)

### 1. Google Cloud Console Setup
```
→ Go to: https://console.cloud.google.com/
→ Create new project: "YouTube Experiment Manager"
→ Enable APIs:
  ✓ YouTube Analytics API
  ✓ YouTube Data API v3
```

### 2. OAuth Consent Screen
```
→ APIs & Services > OAuth consent screen
→ Choose "External"
→ Fill in:
  • App name: YouTube Experiment Manager
  • Support email: [your email]
  • Developer contact: [your email]
→ Scopes > Add:
  ✓ .../auth/yt-analytics.readonly
  ✓ .../auth/youtube.readonly
→ Test users > Add: [your email]
```

### 3. Create Credentials
```
→ APIs & Services > Credentials
→ + CREATE CREDENTIALS > OAuth client ID
→ Application type: Desktop app
→ Name: YouTube Experiment Manager Desktop Client
→ CREATE → Download JSON
```

### 4. Save & Test
```bash
# Rename and move the downloaded file
mv ~/Downloads/client_secret_*.json credentials.json

# Navigate to project (replace with your actual path)
cd path/to/YETi

# Activate environment
source venv/bin/activate

# Test (will open browser for authorization)
python cli.py list
```

### 5. Browser Authorization
```
→ Sign in with YouTube channel owner account
→ Click "Advanced" → "Go to YouTube Experiment Manager (unsafe)"
→ Click "Allow"
→ Close browser tab
→ Done! ✅
```

---

## 📁 Required Files After Setup

```
YETi/
├── credentials.json      ← Downloaded from Google Cloud
├── token.pickle         ← Auto-generated after authorization
└── [all other files]
```

---

## 🔧 Test Commands

```bash
# Activate environment
source venv/bin/activate

# List experiments (tests API connection)
python cli.py list

# Check channel info
python check_channel_info.py

# Start web dashboard
python start_server.py
```

---

## 🚨 Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| "credentials.json not found" | Check filename and location |
| "Access blocked" | Add your email to test users |
| "API not enabled" | Enable both YouTube APIs |
| "Insufficient scopes" | Delete `token.pickle` and re-authorize |
| Browser doesn't open | Copy URL from terminal to browser |

---

## 🔗 Quick Links

- [Google Cloud Console](https://console.cloud.google.com/)
- [APIs & Services](https://console.cloud.google.com/apis/)
- [API Library](https://console.cloud.google.com/apis/library)
- [Credentials](https://console.cloud.google.com/apis/credentials)
- [OAuth Consent](https://console.cloud.google.com/apis/credentials/consent)

---

## ✅ Verification Checklist

- [ ] Project created in Google Cloud
- [ ] Both YouTube APIs enabled
- [ ] OAuth consent screen configured
- [ ] Test user added (your email)
- [ ] OAuth credentials created
- [ ] credentials.json downloaded and renamed
- [ ] credentials.json in project root
- [ ] Browser authorization completed
- [ ] token.pickle file exists
- [ ] `python cli.py list` works

---

## 🔐 Security Reminders

**NEVER share:**
- ❌ credentials.json
- ❌ token.pickle

**These give access to your YouTube channel!**

---

## 📚 Full Documentation

For detailed instructions with screenshots and troubleshooting:
→ See `YOUTUBE_API_SETUP.md`

---

**Setup Time:** ~5 minutes  
**One-time setup:** Yes (re-authorize only if token expires)  
**Cost:** Free (within API quotas)

