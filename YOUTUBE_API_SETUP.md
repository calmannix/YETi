# YouTube API Setup Guide

This guide will walk you through setting up YouTube Analytics API access for your YouTube Experiment Manager.

## Prerequisites

✅ You have **owner access** to a YouTube channel  
✅ Python 3.x is installed  
✅ Virtual environment is set up (already done)

---

## Step-by-Step Setup

### Step 1: Access Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with the **same Google account** that owns your YouTube channel

### Step 2: Create a New Project (or Select Existing)

1. Click on the **project dropdown** at the top of the page (next to "Google Cloud")
2. Click **"NEW PROJECT"** button
3. Enter project details:
   - **Project name**: `YouTube Experiment Manager` (or any name you prefer)
   - **Organization**: Leave as default (No organization)
4. Click **"CREATE"**
5. Wait a few seconds for the project to be created
6. Make sure your new project is selected in the project dropdown

### Step 3: Enable YouTube Analytics API

1. In the Google Cloud Console, open the **navigation menu** (☰ hamburger icon, top left)
2. Navigate to: **APIs & Services > Library**
3. In the search box, type: `YouTube Analytics API`
4. Click on **"YouTube Analytics API"** in the results
5. Click the **"ENABLE"** button
6. Wait for it to enable (should take a few seconds)

### Step 4: Enable YouTube Data API v3 (Also Required)

1. While still in the API Library, search for: `YouTube Data API v3`
2. Click on **"YouTube Data API v3"**
3. Click the **"ENABLE"** button

### Step 5: Configure OAuth Consent Screen

Before creating credentials, you need to set up the OAuth consent screen:

1. Go to: **APIs & Services > OAuth consent screen** (from left menu)
2. Choose **"External"** user type (unless you have a Google Workspace account)
3. Click **"CREATE"**

4. **Fill in the required fields:**
   - **App name**: `YouTube Experiment Manager`
   - **User support email**: Your email address
   - **Developer contact information**: Your email address
   - Leave other fields as default

5. Click **"SAVE AND CONTINUE"**

6. **Scopes page**: Click **"ADD OR REMOVE SCOPES"**
   - Search for and select:
     - `YouTube Analytics API` - `.../auth/yt-analytics.readonly`
     - `YouTube Data API v3` - `.../auth/youtube.readonly`
   - Click **"UPDATE"**
   - Click **"SAVE AND CONTINUE"**

7. **Test users page**: Click **"ADD USERS"**
   - Add your email address (the one that owns the YouTube channel)
   - Click **"ADD"**
   - Click **"SAVE AND CONTINUE"**

8. **Summary page**: Review and click **"BACK TO DASHBOARD"**

### Step 6: Create OAuth 2.0 Credentials

1. Go to: **APIs & Services > Credentials** (from left menu)
2. Click **"+ CREATE CREDENTIALS"** at the top
3. Select **"OAuth client ID"**

4. **Configure the OAuth client:**
   - **Application type**: Select **"Desktop app"**
   - **Name**: `YouTube Experiment Manager Desktop Client` (or any name)

5. Click **"CREATE"**

6. A dialog will appear with your Client ID and Client Secret
   - Click **"DOWNLOAD JSON"**

### Step 7: Save Credentials File

1. The downloaded file will have a name like: `client_secret_XXXXX.json`
2. **Rename it to**: `credentials.json`
3. **Move it to**: `path/to/YETi/`
   - This is your project root directory
   - It should be in the same folder as `youtube_analytics.py`

### Step 8: Test the Setup

1. Open Terminal
2. Navigate to your project:
   ```bash
   cd "path/to/YETi"
   ```

3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

4. Run a test command:
   ```bash
   python cli.py list
   ```

### Step 9: Complete OAuth Authorization

When you run the command for the first time:

1. **A browser window will automatically open**
2. You'll see a Google sign-in page
3. **Sign in with the account that owns your YouTube channel**
4. You'll see a warning: "Google hasn't verified this app"
   - Click **"Advanced"**
   - Click **"Go to YouTube Experiment Manager (unsafe)"**
   - This is safe - it's your own app!

5. Review the permissions:
   - View your YouTube Analytics reports
   - View your YouTube account
   
6. Click **"Allow"**

7. You'll see: "The authentication flow has completed"
8. Close the browser tab

9. Return to your Terminal - the command should now work!

10. A file called `token.pickle` will be created in your project directory
    - This stores your authentication
    - You won't need to authorize again unless you delete this file

### Step 10: Verify Everything Works

Run this command to check your channel info:

```bash
python check_channel_info.py
```

You should see information about your YouTube channel!

---

## 📁 What Files You Should Have

After setup, your project directory should contain:

- ✅ `credentials.json` - Your OAuth credentials (downloaded from Google Cloud)
- ✅ `token.pickle` - Auto-generated after first authorization
- ✅ All other project files

---

## 🔒 Security Notes

**Important:**

- ⚠️ **NEVER share `credentials.json`** with anyone
- ⚠️ **NEVER share `token.pickle`** with anyone
- ⚠️ **NEVER commit these files to Git** (they should be in .gitignore)
- ✅ These files contain access to your YouTube channel data
- ✅ If compromised, revoke access in [Google Cloud Console](https://console.cloud.google.com/apis/credentials)

---

## 🎯 Quick Verification Checklist

Before proceeding with experiments, verify:

- [ ] Google Cloud project created
- [ ] YouTube Analytics API enabled
- [ ] YouTube Data API v3 enabled
- [ ] OAuth consent screen configured
- [ ] OAuth credentials created and downloaded
- [ ] `credentials.json` file in project root
- [ ] Authorization completed in browser
- [ ] `token.pickle` file generated
- [ ] `python cli.py list` runs without errors
- [ ] Channel info displays correctly

---

## 🐛 Troubleshooting

### Error: "credentials.json not found"
- Make sure the file is named exactly `credentials.json` (not `credentials (1).json` or `client_secret_xxx.json`)
- Make sure it's in the project root directory: `path/to/YETi/`

### Error: "Access blocked: YouTube Experiment Manager has not completed Google verification"
- You need to add your email as a test user in OAuth consent screen (Step 5, point 7)
- Go back to OAuth consent screen > Test users > Add your email

### Error: "The OAuth client was not found"
- Make sure you selected "Desktop app" as application type
- Try downloading the credentials again

### Error: "API has not been used in project before"
- Make sure both YouTube Analytics API and YouTube Data API v3 are enabled
- Wait 5-10 minutes after enabling and try again

### Error: "insufficient authentication scopes"
- Delete `token.pickle`
- Run the authorization flow again
- Make sure you added both scopes in Step 5

### Authorization browser doesn't open
- Copy the URL from the terminal
- Paste it into your browser manually
- Complete the authorization
- Copy the authorization code back to terminal if prompted

### "Brand account" issues
- See `BRAND_ACCOUNT_TROUBLESHOOTING.md` in your project

---

## 🎉 Next Steps

Once setup is complete:

1. **Read the quickstart**: `QUICKSTART_V2.md`
2. **Start the web dashboard**: `python start_server.py`
3. **Create your first experiment** using the dashboard or CLI
4. **Run experiments** and analyze results!

---

## 📞 Need Help?

- Check `README_v2.md` for full documentation
- Check `QUICKSTART_V2.md` for usage guide
- Review `BRAND_ACCOUNT_TROUBLESHOOTING.md` if using a brand account
- Visit [Google Cloud Console Help](https://cloud.google.com/support)

---

**You're all set! 🚀**

The YouTube API is now connected and ready to fetch analytics data for your experiments.

