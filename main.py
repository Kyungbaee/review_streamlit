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
import sqlite3 
import hashlib

def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False

def create_user():
	c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')

def add_user(username,password):
	c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username,password))
	conn.commit()

def login_user(username,password):
	c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
	data = c.fetchall()
	return data

st.set_page_config(layout="wide")
col1,col2,col3=st.columns([1.5,2.5,1.5])

conn = sqlite3.connect('database.db')
c = conn.cursor()

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

loaded_model = load_model('best_model.h5')

with open('tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

okt = Okt()

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

def main3():

	st.title("ログイン機能テスト")

	menu = ["ホーム","ログイン","サインアップ"]
	choice = st.sidebar.selectbox("メニュー",menu)

	if choice == "ホーム":
		st.subheader("ホーム画面です")

	elif choice == "ログイン":
		st.subheader("ログイン画面です")

		username = st.sidebar.text_input("ユーザー名を入力してください")
		password = st.sidebar.text_input("パスワードを入力してください",type='password')
		if st.sidebar.checkbox("ログイン"):
			create_user()
			hashed_pswd = make_hashes(password)

			result = login_user(username,check_hashes(password,hashed_pswd))
			if result:

				st.success("{}さんでログインしました".format(username))

			else:
				st.warning("ユーザー名かパスワードが間違っています")

	elif choice == "サインアップ":
		st.subheader("新しいアカウントを作成します")
		new_user = st.text_input("ユーザー名を入力してください")
		new_password = st.text_input("パスワードを入力してください",type='password')

		if st.button("サインアップ"):
			create_user()
			add_user(new_user,make_hashes(new_password))
			st.success("アカウントの作成に成功しました")
			st.info("ログイン画面からログインしてください")

if __name__ == '__main__':
	main()
with col1:
    main()
with col2:
    main2()
with col3:
    main3()

