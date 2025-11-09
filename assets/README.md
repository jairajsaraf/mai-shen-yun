# Assets Directory

This directory contains static assets for the Mai Shen Yun dashboard.

## Banner Image

To use a custom banner image on the homepage:

1. **Add your PNG file** to this directory as `banner.png`
   ```bash
   cp your-image.png assets/banner.png
   ```

2. **Image Specifications:**
   - Format: PNG (or JPG/JPEG also supported)
   - Recommended dimensions: 1920x400 pixels (or similar 4.8:1 ratio)
   - The image will automatically scale to fit the banner container
   - Text overlay with dark shadow is applied for readability

3. **Fallback Behavior:**
   - If `banner.png` is not found, the dashboard will use a gradient background
   - No errors will occur if the image is missing

## Changing the Image

To change the banner image:
- Simply replace `assets/banner.png` with your new image
- Restart the Streamlit app to see the changes
- Keep the same filename (`banner.png`) for automatic loading

## Supported Image Formats

The base64 encoding function supports:
- PNG (.png)
- JPEG (.jpg, .jpeg)
- GIF (.gif)
- WebP (.webp)

Just name your file `banner.png` (or update the path in `app.py` line 35).
