# GitHub Setup Guide for YETi

This guide will help you set up your YETi project on GitHub.

## 📋 Pre-Upload Checklist

All sensitive data has been removed:
- ✅ OpenAI API key removed from `config_template.env`
- ✅ `.gitignore` created to exclude sensitive files
- ✅ Personal paths removed from documentation
- ✅ `credentials.json` will be ignored (not uploaded)
- ✅ `token.pickle` will be ignored (not uploaded)
- ✅ `.env` file will be ignored (not uploaded)

## 🚀 Upload to GitHub

### Step 1: Initialize Git Repository

```bash
cd "/Users/calmannix/Applications/YouTube experiment"
git init
```

### Step 2: Add All Files

```bash
git add .
```

### Step 3: Create Initial Commit

```bash
git commit -m "Initial commit: YETi v2.0 - YouTube Experiment Testing Intelligence"
```

### Step 4: Create Repository on GitHub

1. Go to https://github.com/new
2. Repository name: `YETi` (or your preferred name)
3. Description: "YouTube A/B testing tool with statistical analysis and AI insights"
4. Choose: **Public** (recommended) or Private
5. **Do NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

### Step 5: Connect and Push

```bash
# Add GitHub as remote (replace with your repository URL)
git remote add origin https://github.com/calmannix/YETi.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## 🔒 Verify Security

After pushing, verify these files are **NOT** on GitHub:
- ❌ `credentials.json`
- ❌ `token.pickle`
- ❌ `.env`
- ❌ Any files with API keys

These should be present:
- ✅ `README.md`
- ✅ `.gitignore`
- ✅ `LICENSE`
- ✅ `config_template.env` (with placeholder, not real API key)
- ✅ All source code files
- ✅ Documentation

## 📝 Recommended GitHub Settings

### Repository Settings

1. **About Section**: Add description and topics
   - Description: "YouTube A/B testing tool with statistical analysis and AI insights"
   - Topics: `youtube`, `ab-testing`, `analytics`, `python`, `data-science`, `statistics`, `ai`, `openai`

2. **Social Preview**: Add an image (optional)

3. **Enable Issues**: For bug reports and feature requests

4. **Enable Discussions**: For Q&A and community discussions

### Branch Protection (Optional but Recommended)

If you want to protect your main branch:
1. Go to Settings → Branches
2. Add rule for `main` branch
3. Enable:
   - Require pull request reviews before merging
   - Require status checks to pass before merging

### GitHub Pages (Optional)

You can enable GitHub Pages to host documentation:
1. Go to Settings → Pages
2. Source: Deploy from a branch
3. Branch: `main` / `docs` folder

## 📋 After Upload

1. **Update URLs in README**: If your repo name is different, update links in README.md
   ```bash
   # Clone the repository
   git clone https://github.com/calmannix/YETi.git  # Update with actual name
   ```

2. **Add Badges**: Consider adding status badges to README.md
   - Build status
   - Code coverage
   - License badge
   - Python version badge

3. **Create First Release**: 
   - Go to Releases → Create a new release
   - Tag: `v2.0.0`
   - Title: `YETi v2.0.0 - Initial Public Release`
   - Description: Summarize features

## 🎉 Sharing Your Project

Once uploaded, share your project:
- Tweet about it with #YouTube #DataScience
- Post on Reddit (r/datascience, r/youtube, r/Python)
- Share on LinkedIn
- Submit to awesome lists (awesome-python, awesome-youtube)

## 🔄 Future Updates

To update your GitHub repository after making local changes:

```bash
# Stage changes
git add .

# Commit changes
git commit -m "Description of changes"

# Push to GitHub
git push origin main
```

## ⚠️ Important Reminders

- **Never commit sensitive data**: Double-check before pushing
- **Review .gitignore**: Ensure it covers all sensitive files
- **Keep credentials safe**: Never share `credentials.json` or `token.pickle`
- **Use environment variables**: Keep API keys in `.env` (which is gitignored)

## 🆘 Need Help?

If you encounter issues:
1. Check GitHub's [Git Handbook](https://guides.github.com/introduction/git-handbook/)
2. Review [GitHub's documentation](https://docs.github.com/)
3. Ask in [GitHub Community](https://github.community/)

---

**Ready to share your awesome YouTube A/B testing tool with the world! 🚀**

