import io
import os
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import qrcode

# Page configuration
st.set_page_config(
    page_title="Lyric2Poster Studio",
    page_icon="🎵",
    layout="wide"
)

# Sidebar styling and inputs
st.sidebar.title("🎵 Lyric2Poster Studio")
st.sidebar.markdown("Create emotional lyric posters with metadata and QR widgets.")

st.sidebar.divider()

# 1. Text input section
st.sidebar.subheader("1. Lyrics & Metadata")
lyric_text = st.sidebar.text_area(
    "Lyrics",
    value="Into my heart\nThe moment filled with you",
    height=120
)
song_title = st.sidebar.text_input("Song Title", value="Ditto")
artist_name = st.sidebar.text_input("Artist Name", value="NewJeans")
music_link = st.sidebar.text_input("Music Link (YouTube / Spotify)", value="https://www.youtube.com/")

# 2. Style & Widget options
st.sidebar.subheader("2. Style & Widget Settings")
bg_color_option = st.sidebar.selectbox(
    "Background Theme",
    ["Dark Cinematic", "Clean White", "Sunset Gradient", "Deep Ocean"]
)
include_metadata_card = st.sidebar.checkbox("🎵 Show Music Metadata Card", value=True)
include_qr_code = st.sidebar.checkbox("📱 Add Scannable QR Code", value=True)

# 3. Generate button
generate_btn = st.sidebar.button("✨ Generate Poster", type="primary")

# Main screen UI
st.title("🎨 Lyric2Poster Studio")
st.markdown("Create your own emotional lyric poster and add music metadata and QR codes for interactive sharing.")

# Poster rendering function
def generate_poster(lyric, title, artist, link, bg_theme, show_card, show_qr):
    width, height = 1080, 1080
    
    # Theme background settings
    if bg_theme == "Dark Cinematic":
        bg_color = (18, 18, 18)
        text_color = (255, 255, 255)
        sub_color = (170, 170, 170)
        card_bg = (30, 30, 30, 200)
    elif bg_theme == "Clean White":
        bg_color = (245, 245, 247)
        text_color = (30, 30, 30)
        sub_color = (110, 110, 110)
        card_bg = (255, 255, 255, 230)
    elif bg_theme == "Sunset Gradient":
        bg_color = (45, 27, 45)
        text_color = (255, 230, 240)
        sub_color = (210, 160, 180)
        card_bg = (60, 35, 60, 200)
    else:  # Deep Ocean
        bg_color = (15, 25, 45)
        text_color = (230, 240, 255)
        sub_color = (150, 180, 210)
        card_bg = (25, 40, 70, 200)

    poster = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(poster)

    # Load default fonts (fully compatible with English characters)
    try:
        font_large = ImageFont.truetype("DejaVuSans-Bold.ttf", 54)
        font_medium = ImageFont.truetype("DejaVuSans.ttf", 36)
        font_small = ImageFont.truetype("DejaVuSans.ttf", 26)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Center lyrics text layout
    lines = lyric.split("\n")
    total_text_height = len(lines) * 70
    start_y = (height - total_text_height) // 2 - 100

    for i, line in enumerate(lines):
        draw.text((80, start_y + (i * 70)), line, fill=text_color, font=font_large)

    # Render bottom music metadata card widget
    if show_card:
        card_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        card_draw = ImageDraw.Draw(card_layer)
        
        card_x1, card_y1 = 80, 820
        card_x2, card_y2 = 1000, 1000
        
        card_draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=24, fill=card_bg)
        
        card_draw.text((130, 850), f"Now Playing  •  {title}", fill=text_color, font=font_medium)
        card_draw.text((130, 900), artist, fill=sub_color, font=font_small)
        
        card_draw.rounded_rectangle([130, 955, 930, 967], radius=6, fill=(100, 100, 100, 150))
        card_draw.rounded_rectangle([130, 955, 450, 967], radius=6, fill=text_color)
        
        poster = Image.alpha_composite(poster.convert("RGBA"), card_layer).convert("RGB")

    # Render QR code
    if show_qr and link:
        qr = qrcode.QRCode(box_size=4, border=1)
        qr.add_data(link)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        qr_img = qr_img.resize((120, 120))
        poster.paste(qr_img, (880, 80))

    return poster

# Preview and download handler
if generate_btn:
    with st.spinner("Generating poster and music widget..."):
        result_poster = generate_poster(
            lyric_text, song_title, artist_name, music_link, 
            bg_color_option, include_metadata_card, include_qr_code
        )
        
        st.image(result_poster, caption="Generated Lyric Poster Preview", use_container_width=True)
        
        buf = io.BytesIO()
        result_poster.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        st.download_button(
            label="💾 Download Poster Image (PNG)",
            data=byte_im,
            file_name="lyric_poster_with_widget.png",
            mime="image/png"
        )
else:
    st.info("👈 Please enter your lyrics in the sidebar and click **[Generate Poster]**!")
