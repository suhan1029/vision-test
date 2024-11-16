import streamlit as st
from openai import OpenAI
from PIL import Image
import os
from dotenv import load_dotenv
import base64
import toml

# TOML 파일에서 환경 변수 로드
def load_config(env="default"):
    config = toml.load("config.toml")
    return config[env]

# 환경 변수 로드
config = load_config()
api_key = config.get("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OpenAI API 키가 설정되지 않았습니다. TOML 파일을 확인하세요.")


# OpenAI 클라이언트 설정
client = OpenAI(api_key=api_key)


# 사용자 정의 CSS 적용
def local_css(file_name):
    with open(file_name, encoding='utf-8') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Flask 앱의 CSS를 로드 (Flask의 style.css 파일 경로를 지정)
local_css("style.css")

def describe_image(base64_image, mime_type):
    try:
        prompt = "Describe the content of this image in Korean."

        # OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-4o",  # 올바른 모델 이름 사용
            messages=[
                {
                    'role': 'user',
                    'content': [
                        {'type': 'text', 'text': prompt},
                        {
                            'type': 'image_url',
                            'image_url': {'url': f'data:{mime_type};base64,{base64_image}'},
                        },
                    ]
                }
            ],
            temperature=1.0,
        )
        # 응답 내용 반환
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

def main():
    st.title("비전 AI")
    st.write("이미지를 올리면 AI가 이미지를 인식하고 설명해줍니다.")
            
    # 이미지 업로드
    uploaded_file = st.file_uploader("이미지를 선택하시오.", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        try:
            # 이미지를 Streamlit에 표시
            image = Image.open(uploaded_file)
            st.image(image, caption="업로드한 이미지", use_column_width=True)

            # MIME 타입 추출
            mime_type = f"image/{uploaded_file.type.split('/')[-1]}"

            # 파일 포인터를 처음으로 이동
            uploaded_file.seek(0)

            # Base64로 변환
            base64_image = base64.b64encode(uploaded_file.read()).decode('utf-8')

            # 이미지 설명 생성
            with st.spinner("Processing image..."):
                description = describe_image(base64_image, mime_type)

            # 결과 출력
            st.subheader("Generated Description")
            st.write(description)
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
