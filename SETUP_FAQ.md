# YouTube API Setup - Frequently Asked Questions

Quick answers to common questions about setting up YouTube API access.

---

## 🎯 General Questions

### Q: Why do I need to do this setup?

**A:** To access your YouTube analytics data programmatically. YouTube requires OAuth authentication to ensure only you can access your channel's data. This is a security feature.

### Q: How long does setup take?

**A:** 5-10 minutes for first-time users. Once done, you never have to do it again (unless you revoke access).

### Q: Is this free?

**A:** Yes! YouTube APIs are completely free within generous quota limits. No credit card needed.

### Q: Is this safe?

**A:** Absolutely! You're creating credentials for YOUR OWN USE. The credentials stay on your computer and are never shared. The access is read-only.

---

## 🔐 Security & Privacy

### Q: What data can this tool access?

**A:** Only read-only access to:
- YouTube Analytics (views, watch time, CTR, etc.)
- Channel information
- Video metadata

### Q: Can this tool modify my channel?

**A:** No! The permissions are explicitly read-only. It cannot:
- Upload or delete videos
- Change channel settings
- Modify video details
- Post comments
- Do anything except READ data

### Q: Where are my credentials stored?

**A:** Locally on your computer in two files:
- `credentials.json` - OAuth client credentials (like a username)
- `token.pickle` - Your authorization token (like a session)

These files NEVER leave your computer.

### Q: Who can see my credentials?

**A:** Only you! The files are stored locally. Unless you share them with someone or upload them somewhere, they remain private.

### Q: How do I revoke access later?

**A:** Two ways:
1. Delete `token.pickle` from your project folder (simple revocation)
2. Delete the entire project in [Google Cloud Console](https://console.cloud.google.com) (complete removal)

### Q: What if I lose these files?

**A:** Just delete them and go through setup again. Nothing on your YouTube channel will be affected.

---

## 🏢 Google Cloud Console

### Q: What is Google Cloud Console?

**A:** It's Google's platform for managing API access and cloud services. You're using it just for API credentials - you won't be using any paid cloud services.

### Q: Do I need to set up billing?

**A:** No! You're only using free APIs. No billing information required.

### Q: What if I already have a Google Cloud project?

**A:** You can use an existing project or create a new one just for this. Creating a new one keeps things organized.

### Q: Can I delete the project later?

**A:** Yes! Deleting the project revokes all API access. If you want to use the tool again, you'd need to go through setup again.

---

## 📱 YouTube Account

### Q: Which Google account should I use?

**A:** The account that OWNS your YouTube channel. Check at [YouTube Studio](https://studio.youtube.com) → Settings → Permissions.

### Q: I manage multiple channels. Which one will this access?

**A:** The default channel for the account you sign in with during authorization. If you have multiple channels, make sure you're signed in with the right account.

### Q: I have a Brand Account. Will this work?

**A:** Yes, but Brand Accounts can be tricky. See `BRAND_ACCOUNT_TROUBLESHOOTING.md` for specific help.

### Q: I'm a channel manager, not owner. Can I still use this?

**A:** You need owner permissions. Managers don't have API access. Ask the channel owner to either:
- Make you an owner, or
- Do the setup themselves and share the project

---

## 🔧 Technical Questions

### Q: What is OAuth?

**A:** OAuth is a security standard that lets applications access your data without sharing passwords. You authorize the app through Google's secure login, and Google gives the app a token.

### Q: What are "scopes"?

**A:** Scopes define what the app can do. This tool uses:
- `yt-analytics.readonly` - Read YouTube Analytics
- `youtube.readonly` - Read channel info

Both are read-only for safety.

### Q: What is credentials.json?

**A:** This file contains your OAuth client credentials. Think of it as your app's identity. It's like a username that identifies YOUR installation of this tool to Google.

### Q: What is token.pickle?

**A:** This file stores your authorization token after you click "Allow" in the browser. It's like a session cookie - it proves you already authorized the app.

### Q: Why does the browser warning say "Google hasn't verified this app"?

**A:** Because it's YOUR personal app, not a public one. This is normal and safe. Click "Advanced" → "Go to... (unsafe)" to proceed. It's only "unsafe" from Google's perspective because they didn't review it - but it's YOUR app!

---

## 🐛 Troubleshooting

### Q: Error: "credentials.json not found"

**A:** Check:
1. Is the file in the correct folder? (project root directory)
2. Is it named exactly `credentials.json`? (not `credentials (1).json` or `client_secret_xxx.json`)
3. Did you download it from the right place? (APIs & Services > Credentials)

### Q: Error: "Access blocked"

**A:** You forgot to add yourself as a test user!
1. Go to: OAuth consent screen in Google Cloud Console
2. Scroll to "Test users"
3. Click "ADD USERS"
4. Add your email
5. Try again

### Q: Error: "The OAuth client was not found"

**A:** Possible issues:
- Selected wrong project in Google Cloud Console
- Deleted credentials accidentally
- Used wrong credentials file

Solution: Create new credentials and download again.

### Q: Error: "API has not been used in project before"

**A:** You didn't enable the APIs!
1. Go to: APIs & Services > Library
2. Search: "YouTube Analytics API" → Enable
3. Search: "YouTube Data API v3" → Enable
4. Wait 5 minutes and try again

### Q: Browser doesn't open during authorization

**A:** 
1. Look in the terminal for a URL (starts with `https://accounts.google.com/o/oauth2/auth...`)
2. Copy it
3. Paste into your browser
4. Complete authorization
5. Copy the code back if prompted

### Q: Error: "invalid_grant" or token errors

**A:** Your token expired or was corrupted.
1. Delete `token.pickle`
2. Run the command again
3. Complete browser authorization again

### Q: "This site can't provide a secure connection"

**A:** This happens after clicking "Allow". It's normal! Just check the terminal - the tool should have received the authorization.

---

## 📊 Data & Analytics

### Q: How long does it take for YouTube data to appear?

**A:** YouTube Analytics has a delay:
- Regular videos: Usually available next day
- YouTube Shorts: Can take 24-72 hours
- Some metrics: Up to 2 days

### Q: Why don't I see any data for my recent videos?

**A:** See above - there's always a delay. Plan your experiments with this in mind.

### Q: Can I access data for other people's channels?

**A:** No! Only channels you own or have owner permissions for.

### Q: What if my channel is new and has no data?

**A:** The tool will still work, it just won't return any analytics. Upload some videos and wait for views, then try again.

### Q: Are there API limits?

**A:** Yes, YouTube has daily quota limits, but they're generous:
- 10,000 units per day for YouTube Data API v3
- 50,000+ per day for Analytics API

Normal use of this tool won't hit these limits.

---

## 🔄 Updates & Maintenance

### Q: Do I need to redo setup periodically?

**A:** No! Once set up, it works indefinitely. The token refreshes automatically.

### Q: What if my token expires?

**A:** The tool automatically refreshes it. You shouldn't need to do anything.

### Q: What if I change my YouTube channel name?

**A:** No action needed. Access is based on account, not channel name.

### Q: What if I transfer channel ownership?

**A:** You'll lose access (since you're no longer the owner). The new owner would need to do setup.

---

## 🚀 After Setup

### Q: Now what? How do I use the tool?

**A:** See `QUICKSTART_V2.md` for your first experiment!

Quick start:
```bash
python start_server.py  # Opens web dashboard
```

### Q: How do I create an experiment?

**A:** Two ways:
1. Web dashboard (easiest): http://localhost:5000
2. Command line: See `QUICKSTART_V2.md`

### Q: Do I need to keep the credentials files?

**A:** Yes! Don't delete `credentials.json` or `token.pickle`. The tool needs them every time it runs.

### Q: Can I use this on multiple computers?

**A:** Yes! Just copy both `credentials.json` and `token.pickle` to each computer. Or do the setup separately on each.

---

## 💰 Cost Questions

### Q: Is there any cost at all?

**A:** No! Completely free for:
- Google Cloud project (you're not using any paid services)
- YouTube APIs (free within quota)
- This tool (open source)

### Q: What if I exceed the API quota?

**A:** Very unlikely with normal use. If it happens:
- You'll get an error message
- Wait 24 hours for quota reset
- Or request quota increase (also free, just fill out form)

### Q: Will Google ask for payment info later?

**A:** No! You're only using free APIs. No surprises.

---

## 🤝 Collaboration

### Q: Can multiple people use the same credentials?

**A:** Technically yes (copy the files), but it's better for each person to do their own setup for security.

### Q: Can I share my credentials.json file?

**A:** You could, but don't! Each person should create their own for security. If someone malicious gets it, they could access your channel data.

### Q: How do I set this up for a team?

**A:** Each team member should:
1. Do their own setup
2. Use the same YouTube account during authorization (if sharing a channel)
3. Or use their own accounts if they have owner permissions

---

## 🎓 Learning & Support

### Q: I don't understand OAuth/APIs. Can I still do this?

**A:** Absolutely! Just follow the step-by-step guide. You don't need to understand the technical details.

### Q: Where can I learn more about YouTube APIs?

**A:** 
- [YouTube Analytics API docs](https://developers.google.com/youtube/analytics)
- [YouTube Data API docs](https://developers.google.com/youtube/v3)

### Q: What if I get stuck?

**A:** 
1. Check the troubleshooting section in `YOUTUBE_API_SETUP.md`
2. Run `python verify_setup.py` to see what's wrong
3. Review this FAQ
4. Check error messages carefully - they usually tell you what's wrong

### Q: Can I break something?

**A:** No! Worst case, you delete the credentials and start over. Your YouTube channel is completely safe.

---

## 🎯 Quick Decision Helper

### "Should I use existing or new Google Cloud project?"

**New project** if:
- This is your first time using Google Cloud Console
- You want to keep things organized
- You might delete it later

**Existing project** if:
- You already have one and know what you're doing
- You want everything in one place

### "Which email should I use for test users?"

**Use:** The same email you'll sign in with during authorization (the one that owns the channel)

### "Desktop app or Web application?"

**Always choose:** Desktop app (this is not a web app)

### "Internal or External user type?"

**Choose:**
- External (if personal Google account)
- Internal (only if you have Google Workspace)

Most people choose External.

---

## ✅ Pre-Setup Checklist

Before you start, make sure:
- [ ] I have owner access to a YouTube channel
- [ ] I know the email and password for that account
- [ ] I have 10 minutes available
- [ ] I'm on the computer where I'll use the tool
- [ ] Virtual environment is activated

---

## 🎉 Success Indicators

You know you're done when:
- [ ] `credentials.json` exists in project folder
- [ ] `token.pickle` exists in project folder
- [ ] `python cli.py list` runs without errors
- [ ] `python verify_setup.py` says "ALL CHECKS PASSED"
- [ ] No error messages appear

---

## 📚 Related Documentation

- **Detailed Setup:** `YOUTUBE_API_SETUP.md`
- **Quick Reference:** `SETUP_QUICK_REFERENCE.md`
- **Checklist:** `SETUP_CHECKLIST.txt`
- **Flow Diagram:** `SETUP_FLOW_DIAGRAM.txt`
- **Getting Started:** `START_HERE.md`
- **Using the Tool:** `QUICKSTART_V2.md`

---

**Still have questions?** Check the troubleshooting section in `YOUTUBE_API_SETUP.md` or review the error message carefully - it usually tells you exactly what's wrong!

