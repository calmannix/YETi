# 👹 START HERE - YETi Setup Guide

Welcome! You now have owner access to your YouTube channel. This guide will get you up and running with **YETi** (YouTube Experiment Testing intelligence).

---

## 📋 What You'll Set Up (5-10 minutes)

You need to connect this tool to YouTube's API so it can fetch analytics data from your channel.

**What you'll get:**
- ✅ Access to your YouTube Analytics data
- ✅ Ability to run A/B tests on videos
- ✅ Statistical analysis of your experiments
- ✅ Beautiful reports and charts

---

## 🚀 Quick Setup Process

### Option 1: Detailed Step-by-Step (Recommended for First-Time Users)

**📖 Follow: `YOUTUBE_API_SETUP.md`**

This guide includes:
- Detailed explanations for each step
- What to click and where
- Troubleshooting for common issues
- Security best practices

**Estimated time:** 10 minutes

---

### Option 2: Quick Reference (For Experienced Users)

**📄 Follow: `SETUP_QUICK_REFERENCE.md`**

This is a condensed version with:
- Just the essential steps
- Quick commands
- Common issues table
- Verification checklist

**Estimated time:** 5 minutes

---

### Option 3: Printable Checklist

**📝 Use: `SETUP_CHECKLIST.txt`**

Print or keep on screen while following the detailed guide:
- Track your progress step-by-step
- Check off completed items
- Take notes on any issues

---

## 🎯 The Setup Process (Overview)

Here's what you'll be doing:

```
1. Google Cloud Console
   ↓
2. Create Project
   ↓
3. Enable YouTube APIs
   ↓
4. Configure OAuth
   ↓
5. Download credentials.json
   ↓
6. Authorize in Browser
   ↓
7. ✓ Ready to Use!
```

**Cost:** Free (YouTube API is free within quota limits)

---

## ✅ Verify Your Setup

After completing setup, run the verification script:

```bash
# Make sure you're in the project directory
cd path/to/YETi

# Activate virtual environment
source venv/bin/activate

# Run verification
python verify_setup.py
```

This will check:
- ✓ All required packages installed
- ✓ credentials.json in correct location
- ✓ API connection working
- ✓ Channel access confirmed

---

## 📚 Documentation Index

| Document | Purpose | When to Use |
|----------|---------|-------------|
| **START_HERE.md** | You are here! | First stop |
| **YOUTUBE_API_SETUP.md** | Detailed setup guide | Setting up API access |
| **SETUP_QUICK_REFERENCE.md** | Quick setup steps | If you know what you're doing |
| **SETUP_CHECKLIST.txt** | Track progress | Print and follow along |
| **verify_setup.py** | Test everything works | After setup completion |
| **QUICKSTART_V2.md** | Using the tool | After API setup is done |
| **README_v2.md** | Complete documentation | Reference and deep dive |

---

## 🎓 Your Learning Path

### Step 1: Setup (You Are Here)
1. Read this document ✓
2. Follow `YOUTUBE_API_SETUP.md`
3. Run `verify_setup.py`

### Step 2: First Run
1. Read `QUICKSTART_V2.md`
2. Start the dashboard: `python start_server.py`
3. Create your first experiment

### Step 3: Master It
1. Read full `README_v2.md`
2. Understand statistical significance
3. Run advanced experiments

---

## 🚨 Before You Start - Prerequisites

Make sure you have:

- ✅ **Owner access** to a YouTube channel
  - Not just manager or editor - must be OWNER
  - Check at: [YouTube Studio](https://studio.youtube.com) → Settings → Permissions

- ✅ **Google account** that owns the channel
  - Know the email and password
  - You'll need to sign in during setup

- ✅ **This project already set up**
  - Virtual environment activated
  - Dependencies installed
  - (Looks like this is already done!)

---

## ⏱️ Time Commitment

**Initial Setup:**
- First time: 10-15 minutes
- Follow-up: Never (unless you revoke access)

**Creating an Experiment:**
- 2-5 minutes

**Analyzing Results:**
- 30 seconds (automatic)

---

## 💡 What Happens During Setup

### You will:
1. Create a Google Cloud project (free)
2. Enable two YouTube APIs (free)
3. Create OAuth credentials (sounds scary, but easy!)
4. Download a file called `credentials.json`
5. Authorize in browser (click "Allow")
6. Done!

### The tool will:
1. Use your credentials to connect to YouTube
2. Fetch analytics data for your channel
3. Never modify or upload anything
4. Only READ your analytics (safe!)

---

## 🔒 Security & Privacy

**What you're giving access to:**
- ✅ Read-only access to YouTube Analytics
- ✅ Read-only access to channel info

**What you're NOT giving:**
- ❌ Cannot upload videos
- ❌ Cannot modify videos
- ❌ Cannot delete anything
- ❌ Cannot change settings

**The credentials are:**
- 🔐 Stored locally on your computer only
- 🔐 Never shared with anyone
- 🔐 Never uploaded to internet
- 🔐 Can be revoked anytime in Google Cloud Console

---

## 🆘 Need Help?

### Common Questions

**Q: Do I need a credit card?**
A: No! The YouTube APIs are completely free within quota limits (which are generous).

**Q: Will this modify my channel?**
A: No! This tool only READS data. It cannot change anything on your channel.

**Q: What if I make a mistake?**
A: No worries! You can delete the project and start over. Nothing on your channel will be affected.

**Q: Is this safe?**
A: Yes! The credentials you create are for YOUR OWN USE ONLY. You're not giving access to any third party.

**Q: How do I revoke access later?**
A: Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials) and delete the project.

---

## 🎯 Ready to Start?

Choose your setup guide:

**👉 Recommended:** Open `YOUTUBE_API_SETUP.md` now!

```bash
# If using macOS
open YOUTUBE_API_SETUP.md

# Or read in terminal
cat YOUTUBE_API_SETUP.md
```

**Quick path:** Open `SETUP_QUICK_REFERENCE.md`

**Track progress:** Print `SETUP_CHECKLIST.txt`

---

## ✨ After Setup

Once you see ✓ ALL CHECKS PASSED from `verify_setup.py`:

**Start using the tool:**

```bash
# Start the web dashboard
python start_server.py
```

Your browser will open to a beautiful dashboard where you can:
- 📊 Create experiments
- 📈 Track results
- 🎯 See statistical significance
- 📄 Generate PDF reports

**Follow the quickstart guide:**
→ See `QUICKSTART_V2.md` for your first A/B test!

---

## 🎉 You Got This!

Setting up APIs sounds intimidating, but I promise it's straightforward. Just follow the guide step-by-step, and you'll be running experiments in 10 minutes.

**Let's go! Open `YOUTUBE_API_SETUP.md` and get started! 🚀**

---

**Questions?** Check the troubleshooting section in any of the setup guides.

