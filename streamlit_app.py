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
    "Color Theme",
    ["Dark Cinematic", "Sunset Mood", "Deep Ocean", "Warm Beige"]
)
uploaded_bg = st.sidebar.file_uploader("Upload Custom Background Image (Optional)", type=["png", "jpg", "jpeg"])

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
    
    # 1. Background Setup
    if custom_bg is not None:
        # User uploaded a custom background image
        bg_img = Image.open(custom_bg).convert("RGBA")
        poster = ImageOps.fit(bg_img, (width, height), method=Image.Resampling.LANCZOS)
        # Add a dark overlay to make text readable
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 100))
        poster = Image.alpha_composite(poster, overlay).convert("RGB")
    else:
        # Preset themes with gradient/mood styling
        if theme == "Dark Cinematic":
            bg_color = (20, 20, 24)
            text_color = (255, 255, 255)
            sub_color = (170, 170, 170)
            card_bg = (35, 35, 42, 210)
        elif theme == "Sunset Mood":
            bg_color = (55, 30, 45)
            text_color = (255, 235, 245)
            sub_color = (220, 170, 190)
            card_bg = (70, 40, 60, 210)
        elif theme == "Deep Ocean":
            bg_color = (15, 30, 55)
            text_color = (235, 245, 255)
            sub_color = (160, 190, 220)
            card_bg = (25, 45, 75, 210)
        else:  # Warm Beige
            bg_color = (245, 240, 235)
            text_color = (40, 40, 40)
            sub_color = (120, 115, 110)
            card_bg = (255, 255, 255, 230)

        poster = Image.new("RGB", (width, height), color=bg_color)
        
        # Add a subtle decorative graphic line or frame to avoid "plain" look
        draw_dec = ImageDraw.Draw(poster)
        draw_dec.rectangle([50, 50, width-50, height-50], outline=sub_color, width=2)

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
    start_y = (height - total_text_height) // 2 - 60

    for i, line in enumerate(lines):
        draw.text((120, start_y + (i * line_height)), line, fill=text_color, font=font_large)

    # Render bottom music metadata card widget
    if show_card:
        card_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        card_draw = ImageDraw.Draw(card_layer)
        
        card_x1, card_y1 = 100, 800
        card_x2, card_y2 = 980, 980
        
        card_draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=24, fill=card_bg)
        
        card_draw.text((150, 835), f"Now Playing  •  {title}", fill=text_color, font=font_medium)
        card_draw.text((150, 895), artist, fill=sub_color, font=font_small)
        
        # Progress bar
        card_draw.rounded_rectangle([150, 945, 930, 957], radius=6, fill=(120, 120, 120, 150))
        card_draw.rounded_rectangle([150, 945, 480, 957], radius=6, fill=text_color)
        
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
