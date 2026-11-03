import io
import os
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import qrcode

# 페이지 기본 설정
st.set_page_config(
    page_title="Upgraded Lyric2Poster Studio",
    page_icon="🎵",
    layout="wide"
)

# 사이드바 디자인 설정
st.sidebar.title("🎵 Upgraded Lyric2Poster Studio")
st.sidebar.markdown("감성적인 가사 포스터 제작 및 음악 메타데이터/QR 위젯 생성기")

st.sidebar.divider()

# 1. 텍스트 입력 섹션
st.sidebar.subheader("1. 가사 및 메타데이터 입력")
lyric_text = st.sidebar.text_area(
    "가사 내용",
    value="내맘에 들어와\n너로 가득 채워진 이 순간",
    height=120
)
song_title = st.sidebar.text_input("곡 제목", value="Ditto")
artist_name = st.sidebar.text_input("아티스트 명", value="NewJeans")
music_link = st.sidebar.text_input("음악 링크 (YouTube / Spotify)", value="https://www.youtube.com/")

# 2. 디자인 및 위젯 옵션
st.sidebar.subheader("2. 스타일 & 위젯 설정")
bg_color_option = st.sidebar.selectbox(
    "배경 테마",
    ["다크 시네마틱 (Dark)", "클린 화이트 (Light)", "선셋 그라데이션", "딥 오션"]
)
include_metadata_card = st.sidebar.checkbox("🎵 음악 메타데이터 카드 표시", value=True)
include_qr_code = st.sidebar.checkbox("📱 실시간 스캔 QR 코드 추가", value=True)

# 3. 이미지 생성 버튼
generate_btn = st.sidebar.button("✨ 포스터 생성하기", type="primary")

# 메인 화면 UI
st.title("🎨 Lyric2Poster Studio")
st.markdown("나만의 감성적인 가사 포스터를 만들고, 음악 메타데이터와 QR코드로 인터랙션을 더해보세요.")

# 포스터 렌더링 함수
def generate_poster(lyric, title, artist, link, bg_theme, show_card, show_qr):
    # 기본 캔버스 설정 (정사각형 인스타그램 포스터 규격: 1080x1080)
    width, height = 1080, 1080
    
    # 테마별 배경색 설정
    if bg_theme == "다크 시네마틱 (Dark)":
        bg_color = (18, 18, 18)
        text_color = (255, 255, 255)
        sub_color = (170, 170, 170)
        card_bg = (30, 30, 30, 200)
    elif bg_theme == "클린 화이트 (Light)":
        bg_color = (245, 245, 247)
        text_color = (30, 30, 30)
        sub_color = (110, 110, 110)
        card_bg = (255, 255, 255, 230)
    elif bg_theme == "선셋 그라데이션":
        bg_color = (45, 27, 45)
        text_color = (255, 230, 240)
        sub_color = (210, 160, 180)
        card_bg = (60, 35, 60, 200)
    else:  # 딥 오션
        bg_color = (15, 25, 45)
        text_color = (230, 240, 255)
        sub_color = (150, 180, 210)
        card_bg = (25, 40, 70, 200)

    # 기본 이미지 생성
    poster = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(poster)

    # 폰트 로드 (시스템 기본 폰트 대체 혹은 기본 제공 폰트 사용)
    try:
        font_large = ImageFont.truetype("DejaVuSans-Bold.ttf", 54)
        font_medium = ImageFont.truetype("DejaVuSans.ttf", 36)
        font_small = ImageFont.truetype("DejaVuSans.ttf", 26)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # 가사 텍스트 중앙 배치
    lines = lyric.split("\n")
    total_text_height = len(lines) * 70
    start_y = (height - total_text_height) // 2 - 100

    for i, line in enumerate(lines):
        # 텍스트 중앙 정렬을 위한 대략적인 위치 계산
        draw.text((80, start_y + (i * 70)), line, fill=text_color, font=font_large)

    # 하단 음악 메타데이터 카드 위젯 렌더링
    if show_card:
        card_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        card_draw = ImageDraw.Draw(card_layer)
        
        card_x1, card_y1 = 80, 820
        card_x2, card_y2 = 1000, 1000
        
        # 카드 배경 그리기
        card_draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=24, fill=card_bg)
        
        # 곡 정보 텍스트
        card_draw.text((130, 850), f"Now Playing  •  {title}", fill=text_color, font=font_medium)
        card_draw.text((130, 900), artist, fill=sub_color, font=font_small)
        
        # 음악 재생 바 (Progress Bar)
        card_draw.rounded_rectangle([130, 955, 930, 967], radius=6, fill=(100, 100, 100, 150))
        card_draw.rounded_rectangle([130, 955, 450, 967], radius=6, fill=text_color)
        
        poster = Image.alpha_composite(poster.convert("RGBA"), card_layer).convert("RGB")

    # QR 코드 추가 렌더링
    if show_qr and link:
        qr = qrcode.QRCode(box_size=4, border=1)
        qr.add_data(link)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        qr_img = qr_img.resize((120, 120))
        
        # 포스터 우측 상단 또는 카드 옆에 배치
        poster.paste(qr_img, (880, 80))

    return poster

# 미리보기 및 다운로드 처리
if generate_btn:
    with st.spinner("포스터와 음악 위젯을 생성하고 있습니다..."):
        result_poster = generate_poster(
            lyric_text, song_title, artist_name, music_link, 
            bg_color_option, include_metadata_card, include_qr_code
        )
        
        # 화면에 표시
        st.image(result_poster, caption="생성된 리릭스 포스터 미리보기", use_container_width=True)
        
        # 다운로드 버튼 제공
        buf = io.BytesIO()
        result_poster.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        st.download_button(
            label="💾 포스터 이미지 다운로드 (PNG)",
            data=byte_im,
            file_name="lyric_poster_with_widget.png",
            mime="image/png"
        )
else:
    # 초기 화면 예시 이미지 공간 안내
    st.info("👈 왼쪽 사이드바에서 가사를 입력하고 **[포스터 생성하기]** 버튼을 눌러주세요!")
