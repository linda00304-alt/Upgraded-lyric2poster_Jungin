import io
import os
import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
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

# 2. Style & Background Image upload
st.sidebar.subheader("2. Style & Background")
bg_theme = st.sidebar.selectbox(
    "Poster Mood",
    ["Midnight Neon", "Sunset Glow", "Dreamy Blue", "Minimal Mono"]
)
uploaded_bg = st.sidebar.file_uploader("Upload Your Photo (Optional)", type=["png", "jpg", "jpeg"])

include_metadata_card = st.sidebar.checkbox("🎵 Show Music Metadata Card", value=True)
include_qr_code = st.sidebar.checkbox("📱 Add Scannable QR Code", value=True)

# 3. Generate button
generate_btn = st.sidebar.button("✨ Generate Poster", type="primary")

# Main screen UI
st.title("🎨 Lyric2Poster Studio")
st.markdown("Create your own emotional lyric poster and add music metadata and QR codes for interactive sharing.")

# Poster rendering function
def generate_poster(lyric, title, artist, link, theme, custom_bg, show_card, show_qr):
    width, height = 1080, 1080
    
    poster = Image.new("RGB", (width, height))
    draw_bg = ImageDraw.Draw(poster)
    
    # 1. Background Setup with guaranteed Rich Gradients
    if custom_bg is not None:
        bg_img = Image.open(custom_bg).convert("RGBA")
        poster = ImageOps.fit(bg_img, (width, height), method=Image.Resampling.LANCZOS)
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 120))
        poster = Image.alpha_composite(poster, overlay).convert("RGB")
        draw_bg = ImageDraw.Draw(poster)
        text_color = (255, 255, 255)
        sub_color = (200, 200, 200)
        card_bg = (30, 30, 35, 220)
    else:
        # Define exact gradient colors based on theme
        if theme == "Midnight Neon":
            c1, c2 = (35, 25, 55), (10, 10, 18)
            text_color = (255, 255, 255)
            sub_color = (190, 160, 220)
            card_bg = (45, 35, 65, 230)
        elif theme == "Sunset Glow":
            c1, c2 = (90, 35, 55), (35, 20, 40)
            text_color = (255, 235, 245)
            sub_color = (240, 180, 200)
            card_bg = (95, 45, 65, 230)
        elif theme == "Dreamy Blue":
            c1, c2 = (25, 55, 95), (10, 20, 40)
            text_color = (230, 245, 255)
            sub_color = (150, 200, 240)
            card_bg = (35, 65, 105, 230)
        else:  # Minimal Mono
            c1, c2 = (245, 245, 247), (215, 215, 220)
            text_color = (20, 20, 20)
            sub_color = (110, 110, 115)
            card_bg = (255, 255, 255, 240)

        # Draw smooth vertical gradient line by line
        for y in range(height):
            r = int(c1[0] + (c2[0] - c1[0]) * (y / height))
            g = int(c1[1] + (c2[1] - c1[1]) * (y / height))
            b = int(c1[2] + (c2[2] - c1[2]) * (y / height))
            draw_bg.line([(0, y), (width, y)], fill=(r, g, b))

        # Artistic double frame lines
        draw_bg.rectangle([60, 60, width-60, height-60], outline=sub_color, width=2)
        draw_bg.rectangle([72, 72, width-72, height-72], outline=sub_color, width=1)

    draw = ImageDraw.Draw(poster)

    # Font loader
    def load_font(size):
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "DejaVuSans-Bold.ttf",
            "DejaVuSans.ttf"
        ]
        for path in font_paths:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except:
                    continue
        return ImageFont.load_default()

    font_large = load_font(52)
    font_medium = load_font(34)
    font_small = load_font(24)

    # Lyrics layout
    lines = lyric.split("\n")
    line_height = 75
    total_text_height = len(lines) * line_height
    start_y = (height - total_text_height) // 2 - 40

    for i, line in enumerate(lines):
        draw.text((120, start_y + (i * line_height)), line, fill=text_color, font=font_large)

    # Render bottom music metadata card widget
    if show_card:
        card_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        card_draw = ImageDraw.Draw(card_layer)
        
        card_x1, card_y1 = 100, 780
        card_x2, card_y2 = 980, 960
        
        card_draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=24, fill=card_bg)
        
        card_draw.text((150, 815), f"Now Playing  •  {title}", fill=text_color, font=font_medium)
        card_draw.text((150, 875), artist, fill=sub_color, font=font_small)
        
        # Progress bar
        card_draw.rounded_rectangle([150, 925, 930, 937], radius=6, fill=(150, 150, 150, 150))
        card_draw.rounded_rectangle([150, 925, 480, 937], radius=6, fill=text_color)
        
        poster = Image.alpha_composite(poster.convert("RGBA"), card_layer).convert("RGB")

    # Render QR code
    if show_qr and link:
        qr = qrcode.QRCode(box_size=5, border=1)
        qr.add_data(link)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
        qr_img = qr_img.resize((120, 120))
        poster.paste(qr_img, (830, 100))

    return poster

# Session state handling
if "poster_image" not in st.session_state:
    st.session_state.poster_image = None

if generate_btn:
    st.session_state.poster_image = generate_poster(
        lyric_text, song_title, artist_name, music_link, 
        bg_theme, uploaded_bg, include_metadata_card, include_qr_code
    )

if st.session_state.poster_image is not None:
    st.image(st.session_state.poster_image, caption="Generated Lyric Poster Preview", use_container_width=True)
    
    buf = io.BytesIO()
    st.session_state.poster_image.save(buf, format="PNG")
    byte_im = buf.getvalue()
    
    st.download_button(
        label="💾 Download Poster Image (PNG)",
        data=byte_im,
        file_name="lyric_poster_art.png",
        mime="image/png"
    )
else:
    st.info("👈 Set your options in the sidebar and click **[Generate Poster]** to create your artwork!")
