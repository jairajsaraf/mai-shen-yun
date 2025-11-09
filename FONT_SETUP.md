# Custom Fonts Setup Guide

This guide explains how to enable custom fonts (SpaceGrotesk and SpaceMono) in the Mai Shen Yun dashboard.

## Current Status

The dashboard is configured to use custom fonts, but they require:
1. ✅ Font files in `app/static/` directory
2. ✅ Streamlit 1.35.0 or higher
3. ✅ Proper configuration in `.streamlit/config.toml`
4. ⚠️ **Streamlit version upgrade required**

## Quick Fix (3 Steps)

### Step 1: Upgrade Streamlit

The `requirements.txt` specifies `streamlit>=1.35.0`, but you may have an older version installed.

```bash
pip install --upgrade "streamlit>=1.35.0"
```

### Step 2: Verify Font Files

Font files should already be in `app/static/`. Verify:

```bash
ls -la app/static/*.ttf
```

You should see:
- `SpaceGrotesk-VariableFont_wght.ttf`
- `SpaceMono-Bold.ttf`
- `SpaceMono-BoldItalic.ttf`
- `SpaceMono-Italic.ttf`
- `SpaceMono-Regular.ttf`

### Step 3: Restart & Refresh

```bash
# Stop the Streamlit server (Ctrl+C)
# Start it again
streamlit run app.py

# In your browser: Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
```

## Diagnostic Tool

Run the Font Diagnostic page to identify issues:

1. Start the app: `streamlit run app.py`
2. Navigate to "🔤 Font Diagnostic" in the sidebar
3. Follow the recommendations provided

## Why Fonts May Not Be Working

### Issue 1: Streamlit Version Too Old ⚠️

**Problem**: Custom fonts via `[[theme.fontFaces]]` require Streamlit 1.35.0+

**Check**:
```bash
python -c "import streamlit; print(streamlit.__version__)"
```

**Fix**:
```bash
pip install --upgrade "streamlit>=1.35.0"
```

### Issue 2: Browser Cache

**Problem**: Old cached styles preventing new fonts from loading

**Fix**:
- Chrome/Edge: `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
- Firefox: `Ctrl + F5` (Windows) or `Cmd + Shift + R` (Mac)
- Safari: `Cmd + Option + R`

### Issue 3: Font Files Missing

**Problem**: Font files not downloaded

**Fix**: See `app/static/README.md` for download instructions

## Configuration Details

The `.streamlit/config.toml` file contains:

```toml
[server]
enableStaticServing = true

[[theme.fontFaces]]
family = "SpaceGrotesk"
url = "app/static/SpaceGrotesk-VariableFont_wght.ttf"

# ... additional font configurations

[theme]
font = "SpaceGrotesk"
codeFont = "SpaceMono"
```

## Fallback Fonts

If custom fonts don't work, the dashboard will automatically fall back to system fonts:
- **Headings/Body**: System sans-serif
- **Code**: System monospace

The dashboard will look professional either way!

## Testing Fonts Are Working

1. Open the dashboard
2. Inspect a heading element in browser DevTools
3. Check the computed font-family
4. Should show: `SpaceGrotesk, sans-serif`

OR use the "🔤 Font Diagnostic" page for automated checks.

## Alternative: Use System Fonts

If you prefer not to use custom fonts:

1. Edit `.streamlit/config.toml`
2. Change:
   ```toml
   font = "sans serif"
   codeFont = "monospace"
   ```
3. Comment out or remove all `[[theme.fontFaces]]` sections

## Support

If fonts still don't work after following this guide:

1. Run the diagnostic: Navigate to "🔤 Font Diagnostic" page
2. Check all items show ✅ green checkmarks
3. Verify Streamlit version is 1.35.0+
4. Try a different browser
5. Clear all browser cache and cookies

## Additional Resources

- [Streamlit Theming Documentation](https://docs.streamlit.io/library/advanced-features/theming)
- [Google Fonts - Space Grotesk](https://fonts.google.com/specimen/Space+Grotesk)
- [Google Fonts - Space Mono](https://fonts.google.com/specimen/Space+Mono)
