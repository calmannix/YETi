# 👹 YETi Branding Update

## Official Name
**YETi** - YouTube Experiment Testing intelligence

## Emoji Icon
👹 (Monster/Oni emoji)

## Changes Applied

### 1. Web Dashboard (`api/templates/index.html`)
- ✅ Updated page title to "YETi - YouTube Experiment Testing intelligence"
- ✅ Added monster emoji favicon (👹) using inline SVG data URI
- ✅ Updated header to show "👹 YETi"
- ✅ Updated subtitle to include full name
- ✅ Updated footer branding

### 2. Documentation Files
- ✅ `README_v2.md` - Updated main title and branding
- ✅ `START_HERE.md` - Updated to reference YETi
- ✅ `QUICKSTART_V2.md` - Updated title with YETi branding

### 3. Server Files
- ✅ `api/server.py` - Updated docstring
- ✅ `start_server.py` - Updated startup message with emoji

## Favicon Implementation
The favicon uses an inline SVG data URI to display the 👹 emoji:
```html
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>👹</text></svg>">
```

This approach:
- ✅ No external file needed
- ✅ Works in all modern browsers
- ✅ Shows emoji in browser tab
- ✅ Perfect for cross-platform emoji support

## Testing
To see the changes:
1. Start the server: `python start_server.py`
2. Look at the browser tab - you'll see 👹
3. The dashboard header now shows "👹 YETi"
4. Footer displays full branding

## Visual Appearance
```
Browser Tab: 👹 YETi - YouTube Experiment Testing intelligence

Dashboard Header:
┌─────────────────────────────────────────────────────┐
│ 👹 YETi                                              │
│ YouTube Experiment Testing intelligence -           │
│ A/B Testing & Analytics Dashboard                   │
└─────────────────────────────────────────────────────┘
```

---
**Version:** 2.0  
**Updated:** November 4, 2025







