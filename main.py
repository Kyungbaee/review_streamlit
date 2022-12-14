import streamlit as st
import re
from konlpy.tag import Okt
from keras_preprocessing.sequence import pad_sequences
from keras.models import load_model
import os
import pandas as pd
import pickle
import plotly.express as px
from io import StringIO
import streamlit_authenticator as stauth
import yaml
from pathlib import Path

# st.set_page_config(layout="wide")
col1,col2=st.columns([1.5,2.5])
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
stopwords = ['도', '는', '다', '의', '가', '이', '은', '한', '에', '하', '고', '을', '를', '인', '듯', '과', '와', '네', '들', '듯', '지', '임', '게']
max_len = 80

def sentiment(n_sentence):
  n_sentence = re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣 ]','', n_sentence)
  n_sentence = okt.morphs(n_sentence)
  n_sentence = [word for word in n_sentence if not word in stopwords]
  encoded = tokenizer.texts_to_sequences([n_sentence])
  pad_new = pad_sequences(encoded, maxlen = max_len)

  score = float(loaded_model.predict(pad_new))

  return score

def main():
    review = st.text_input('리뷰 문장 분석 (최대 80글자)', '문장을 입력해주세요.')
    if (review != '문장을 입력해주세요.') & (review != ""):
        r_score =  sentiment(review)
        if(r_score > 0.5): 
            st.info("{:.2f}% 확률로 긍정 리뷰입니다.".format(r_score * 100))
        else:
            st.info("{:.2f}% 확률로 부정 리뷰입니다.".format((1 - r_score) * 100))

def main2():
    uploaded_file = st.file_uploader("리뷰 파일 분석", accept_multiple_files=False)
    review_list = []
    if uploaded_file is not None:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        string_data = stringio.read()
        for review in string_data.split('\n'):
            r_score = sentiment(review)
            if(r_score > 0.5): 
                review_list.append(('긍정',1))
            else:
                review_list.append(('부정',1))
            
        df = pd.DataFrame(review_list, columns=["감정","카운트"])
            
        fig1 = px.pie(df.groupby("감정", as_index=False).sum(), values='카운트', names='감정', title='리뷰 감정 분석')      #plotly pie차트
        st.plotly_chart(fig1)

# --- login ---
with open('config.yaml') as file:
    config = yaml.load(file, Loader=stauth.SafeLoader)

## yaml 파일 데이터로 객체 생성
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

## 로그인 위젯 렌더링
## log(in/out)(로그인 위젯 문구, 버튼 위치)
## 버튼 위치 = "main" or "sidebar"
name, authentication_status, username = authenticator.login("Login","main")

# authentication_status : 인증 상태 (실패, 값없음, 성공)
if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status:
    authenticator.logout("Logout","sidebar")
    st.sidebar.title(f"Welcome {name}")

    loaded_model = load_model('best_model.h5')
    with open('tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)
    okt = Okt()

    with col1:
        main()
    with col2:
        main2()
