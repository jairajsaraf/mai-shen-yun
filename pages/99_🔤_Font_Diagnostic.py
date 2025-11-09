"""
Font Loading Diagnostic Tool
Checks if custom fonts are properly configured and accessible
"""

import streamlit as st
import os
from pathlib import Path

st.set_page_config(page_title="Font Diagnostic", page_icon="🔤", layout="wide")

st.title("🔤 Font Loading Diagnostic", anchor=False)
st.markdown("---")

# Check Streamlit version
st.header("1️⃣ Streamlit Version Check", anchor=False)
try:
    import streamlit
    version = streamlit.__version__
    st.success(f"✅ Streamlit version: {version}")

    # Parse version
    major, minor, patch = version.split('.')[:3]
    version_number = float(f"{major}.{minor}")

    if version_number >= 1.35:
        st.success("✅ Version supports custom fonts via config.toml (requires 1.35.0+)")
    else:
        st.error(f"❌ Version {version} does NOT support custom fonts via config.toml. Requires 1.35.0+")
        st.warning("**Solution**: Update requirements.txt to `streamlit>=1.35.0` and reinstall")
except Exception as e:
    st.error(f"❌ Error checking version: {e}")

st.markdown("---")

# Check config file
st.header("2️⃣ Config File Check", anchor=False)

config_path = Path(".streamlit/config.toml")
if config_path.exists():
    st.success(f"✅ Config file exists at: {config_path}")

    with open(config_path, 'r') as f:
        config_content = f.read()

    # Check for key configurations
    if "enableStaticServing = true" in config_content:
        st.success("✅ Static serving is enabled")
    else:
        st.error("❌ Static serving is NOT enabled")

    if "[[theme.fontFaces]]" in config_content:
        st.success("✅ Custom font faces are defined")
        font_count = config_content.count("[[theme.fontFaces]]")
        st.info(f"Found {font_count} font face definitions")
    else:
        st.warning("⚠️ No custom font faces defined")

    with st.expander("View config.toml"):
        st.code(config_content, language="toml")
else:
    st.error(f"❌ Config file NOT found at: {config_path}")

st.markdown("---")

# Check font files
st.header("3️⃣ Font Files Check", anchor=False)

font_files = [
    "app/static/SpaceGrotesk-VariableFont_wght.ttf",
    "app/static/SpaceMono-Bold.ttf",
    "app/static/SpaceMono-BoldItalic.ttf",
    "app/static/SpaceMono-Italic.ttf",
    "app/static/SpaceMono-Regular.ttf"
]

all_exist = True
for font_file in font_files:
    font_path = Path(font_file)
    if font_path.exists():
        size_kb = font_path.stat().st_size / 1024
        st.success(f"✅ {font_file} ({size_kb:.1f} KB)")
    else:
        st.error(f"❌ {font_file} - NOT FOUND")
        all_exist = False

if all_exist:
    st.success("✅ All font files are present")
else:
    st.error("❌ Some font files are missing")
    st.warning("**Solution**: Add font files to app/static/ directory (see app/static/README.md)")

st.markdown("---")

# Check static directory serving
st.header("4️⃣ Static Directory Check", anchor=False)

static_dir = Path("app/static")
if static_dir.exists() and static_dir.is_dir():
    st.success(f"✅ Static directory exists: {static_dir}")
    files = list(static_dir.glob("*"))
    st.info(f"Contains {len(files)} files")

    with st.expander("View directory contents"):
        for file in files:
            st.write(f"- {file.name}")
else:
    st.error(f"❌ Static directory NOT found: {static_dir}")

st.markdown("---")

# Test font rendering
st.header("5️⃣ Font Rendering Test", anchor=False)

st.markdown("""
**Expected fonts:**
- Headings: SpaceGrotesk
- Body text: SpaceGrotesk
- Code: SpaceMono
""")

st.subheader("Sample Heading Text (Should use SpaceGrotesk)")
st.write("This is body text that should use SpaceGrotesk font family.")

st.code("""
# This code block should use SpaceMono
def hello_world():
    print("Hello, World!")
""", language="python")

st.markdown("---")

# Diagnosis summary
st.header("🔍 Diagnosis Summary", anchor=False)

st.markdown("""
### Common Issues & Solutions:

**Issue 1: Streamlit Version Too Old**
- **Problem**: Custom fonts require Streamlit 1.35.0+
- **Solution**: Update `requirements.txt` to `streamlit>=1.35.0`
- **Fix**: Run `pip install --upgrade streamlit>=1.35.0`

**Issue 2: Font Files Missing**
- **Problem**: Font files not in app/static/ directory
- **Solution**: Download fonts from Google Fonts
- **Fix**: See `app/static/README.md` for instructions

**Issue 3: Static Serving Not Enabled**
- **Problem**: `enableStaticServing` not set in config.toml
- **Solution**: Add `enableStaticServing = true` under `[server]`

**Issue 4: Browser Cache**
- **Problem**: Old fonts cached in browser
- **Solution**: Hard refresh (Ctrl+Shift+R) or clear browser cache

**Issue 5: Config File Order**
- **Problem**: Config sections in wrong order
- **Solution**: Ensure `[server]` comes before `[[theme.fontFaces]]`

### Recommended Fix:

1. **Update Streamlit**:
   ```bash
   pip install --upgrade "streamlit>=1.35.0"
   ```

2. **Verify config.toml** has this structure:
   ```toml
   [server]
   enableStaticServing = true

   [[theme.fontFaces]]
   family = "SpaceGrotesk"
   url = "app/static/SpaceGrotesk-VariableFont_wght.ttf"
   ```

3. **Restart Streamlit**:
   ```bash
   streamlit run app.py
   ```

4. **Hard refresh browser**: Ctrl+Shift+R (or Cmd+Shift+R on Mac)
""")

# Instructions
st.info("""
💡 **After fixing**:
1. Restart the Streamlit server
2. Hard refresh your browser (Ctrl+Shift+R)
3. Check if fonts are now loading properly
""")
