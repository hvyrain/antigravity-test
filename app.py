import streamlit as st
from PIL import Image
import colorgram
import io

# 앱 설정
st.set_page_config(
    page_title="🎨 컬러 팔레트 추출기",
    page_icon="🎨",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
    .color-box {
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 10px;
        transition: transform 0.2s;
    }
    .color-box:hover {
        transform: translateY(-5px);
    }
    .hex-text {
        font-size: 1.2rem;
        letter-spacing: 1px;
    }
    .rgb-text {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .mockup-container {
        border-radius: 15px;
        padding: 30px;
        margin-top: 20px;
        text-align: center;
        box-shadow: 0 10px 15px rgba(0,0,0,0.1);
    }
    .mockup-btn {
        border-radius: 25px;
        padding: 12px 24px;
        font-size: 1.1rem;
        font-weight: 600;
        cursor: pointer;
        margin: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .mockup-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 10px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)


def rgb_to_hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b).upper()

def get_luminance(r, g, b):
    # Calculate luminance to decide text color (black vs white)
    return (0.299 * r + 0.587 * g + 0.114 * b)

st.title("🎨 찰떡 컬러 팔레트 추출기")
st.markdown("**시각디자인과 학생들을 위한 영감 도구!** 이미지를 업로드하고 숨겨진 메인 색상들을 찾아보세요.")

# 사이드바 설정
with st.sidebar:
    st.header("⚙️ 설정")
    num_colors = st.slider("추출할 색상 개수", min_value=3, max_value=12, value=5)
    st.markdown("---")
    st.info("💡 **Tip:** 복잡한 이미지일수록 더 많은 색상을 추출해보면 재미있는 결과를 얻을 수 있습니다.")

uploaded_file = st.file_uploader("이미지를 여기에 드롭하거나 클릭해서 업로드하세요 (JPG, PNG)", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    # 이미지 로드
    image = Image.open(uploaded_file)
    
    st.subheader("🖼️ 원본 이미지")
    # 넓이를 화면에 맞게 조정
    st.image(image, width="content")
    
    st.subheader(f"✨ 추출된 {num_colors}가지 주요 색상")
    
    # colorgram은 파일 경로나 PIL Image 객체를 받음
    # 빠른 처리를 위해 이미지가 너무 크면 리사이즈
    image_copy = image.copy()
    image_copy.thumbnail((400, 400))
    
    # spinner를 사용하여 로딩 상태 표시
    with st.spinner('색상을 분석하고 추출하는 중입니다...'):
        colors = colorgram.extract(image_copy, num_colors)
    
    # 추출된 색상을 화면에 표시
    cols = st.columns(len(colors))
    
    extracted_data = []
    for i, color in enumerate(colors):
        r, g, b = color.rgb.r, color.rgb.g, color.rgb.b
        hex_code = rgb_to_hex(r, g, b)
        proportion = color.proportion
        
        extracted_data.append({
            'rgb': (r,g,b),
            'hex': hex_code,
            'proportion': proportion
        })
        
        # 텍스트 색상 결정 (배경이 밝으면 검정 텍스트, 어두우면 흰 텍스트)
        text_color = "black" if get_luminance(r, g, b) > 150 else "white"
        text_shadow = "none" if text_color == "black" else "1px 1px 2px rgba(0,0,0,0.5)"
        
        with cols[i]:
            st.markdown(f"""
            <div class="color-box" style="background-color: {hex_code}; color: {text_color}; text-shadow: {text_shadow};">
                <div class="hex-text">{hex_code}</div>
                <div class="rgb-text">RGB({r},{g},{b})</div>
                <div style="font-size: 0.8rem; margin-top: 5px;">{proportion*100:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("---")
    st.subheader("📱 UI 적용 미리보기 (Mockup)")
    st.markdown("추출된 색상을 실제 버튼 등 UI 컴포넌트에 적용했을 때 어떤 느낌일지 확인해보세요. **버튼을 클릭하면 테마 색상이 부드럽게 변경됩니다!**")
    
    if len(extracted_data) >= 2:
        primary = extracted_data[0]
        secondary = extracted_data[1]
        
        import streamlit.components.v1 as components
        
        primary_btn_text = 'black' if get_luminance(*primary['rgb']) > 150 else 'white'
        secondary_btn_text = 'black' if get_luminance(*secondary['rgb']) > 150 else 'white'
        
        html_code = f"""
        <style>
            body {{ font-family: sans-serif; margin: 0; padding: 0; }}
            .mockup-container {{
                border-radius: 15px;
                padding: 30px;
                text-align: center;
                box-shadow: 0 10px 15px rgba(0,0,0,0.1);
                background-color: #F8F9FA;
                border: 2px solid {primary['hex']}aa;
                transition: all 0.4s ease;
                min-height: 150px;
            }}
            #mockup-title {{
                color: {primary['hex']}; 
                margin-bottom: 10px;
                transition: color 0.4s ease;
            }}
            #mockup-text {{
                color: #444444; 
                font-size: 1.05rem; 
                margin-bottom: 25px;
            }}
            #mockup-theme-text {{
                font-weight: bold;
                color: {primary['hex']};
                transition: color 0.4s ease;
            }}
            .mockup-btn {{
                border-radius: 25px;
                padding: 12px 24px;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                margin: 10px;
                transition: transform 0.2s, box-shadow 0.2s, background-color 0.4s, color 0.4s, border 0.4s;
            }}
            .mockup-btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 10px rgba(0,0,0,0.15);
            }}
            .btn-primary {{
                background-color: {primary['hex']}; 
                color: {primary_btn_text}; 
                border: 2px solid {primary['hex']};
            }}
            .btn-secondary {{
                background-color: transparent; 
                border: 2px solid {secondary['hex']}; 
                color: {secondary['hex']};
            }}
        </style>

        <div class="mockup-container" id="mockup-box">
            <h3 id="mockup-title">나만의 감각적인 디자인 포트폴리오</h3>
            <p id="mockup-text">
                선택된 테마 색상은 현재 <span id="mockup-theme-text">{primary['hex']}</span>입니다. ✨
            </p>
            <!-- 클릭 시 첫 번째 버튼은 항상 메인 색상으로, 두 번째 버튼은 서브 색상(아웃라인)으로 변합니다. -->
            <button class="mockup-btn btn-primary" id="btn-1" onclick="changeTheme('{primary['hex']}', '{secondary['hex']}', '{primary_btn_text}', '{secondary_btn_text}')">
                주요 테마 보기
            </button>
            <button class="mockup-btn btn-secondary" id="btn-2" onclick="changeTheme('{secondary['hex']}', '{primary['hex']}', '{secondary_btn_text}', '{primary_btn_text}')">
                보조 테마 보기
            </button>
        </div>

        <script>
            function changeTheme(mainCol, subCol, mainTextColor, subTextColor) {{
                // 컨테이너 테두리 변경
                document.getElementById('mockup-box').style.borderColor = mainCol + 'aa';
                
                // 제목 색상 변경
                document.getElementById('mockup-title').style.color = mainCol;
                
                // 텍스트 강조 색상 변경
                var themeText = document.getElementById('mockup-theme-text');
                themeText.innerHTML = mainCol;
                themeText.style.color = mainCol;
                
                // 첫 번째 버튼 (주요 테마 보기) 을 클릭된 테마 색상으로 칠함
                var btn1 = document.getElementById('btn-1');
                btn1.style.backgroundColor = mainCol;
                btn1.style.borderColor = mainCol;
                btn1.style.color = mainTextColor;
                
                // 두 번째 버튼 (보조 테마 보기) 을 다른 색상의 아웃라인으로 변경
                var btn2 = document.getElementById('btn-2');
                btn2.style.borderColor = subCol;
                btn2.style.color = subCol;
                btn2.style.backgroundColor = 'transparent';
            }}
        </script>
        """
        components.html(html_code, height=350)
else:
    st.info("👆 위 영역에 영감을 얻고 싶은 이미지를 업로드해 주세요!")
