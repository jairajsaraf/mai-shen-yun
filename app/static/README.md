# Font Files Directory

This directory should contain the custom font files referenced in `.streamlit/config.toml`.

## Required Fonts

### Space Grotesk (Main Font)
- **File:** `SpaceGrotesk-VariableFont_wght.ttf`
- **Download:** https://fonts.google.com/specimen/Space+Grotesk
- **License:** Open Font License

### Space Mono (Code Font)
- **Files:**
  - `SpaceMono-Regular.ttf`
  - `SpaceMono-Bold.ttf`
  - `SpaceMono-Italic.ttf`
  - `SpaceMono-BoldItalic.ttf`
- **Download:** https://fonts.google.com/specimen/Space+Mono
- **License:** Open Font License

## Installation Instructions

1. Visit Google Fonts links above
2. Click "Download family" button
3. Extract the ZIP files
4. Copy the `.ttf` files to this directory
5. Restart the Streamlit app

## Alternative: Use System Fonts

If you prefer not to add custom fonts, the app will fall back to system fonts. To use system fonts:

1. Edit `.streamlit/config.toml`
2. Change `font = "SpaceGrotesk"` to `font = "sans serif"`
3. Change `codeFont = "SpaceMono"` to `codeFont = "monospace"`
4. Remove or comment out the `[[theme.fontFaces]]` sections

The dashboard will work perfectly fine with system fonts!
