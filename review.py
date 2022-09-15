import re
from eunjeon import Mecab
from keras_preprocessing.sequence import pad_sequences
from keras.models import load_model
import os
import pickle

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

loaded_model = load_model('best_model.h5')

with open('tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

mecab = Mecab()

stopwords = ['도', '는', '다', '의', '가', '이', '은', '한', '에', '하', '고', '을', '를', '인', '듯', '과', '와', '네', '들', '듯', '지', '임', '게']


max_len = 80

def sentiment(n_sentence):
  n_sentence = re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣 ]','', n_sentence)
  n_sentence = mecab.morphs(n_sentence)
  n_sentence = [word for word in n_sentence if not word in stopwords]
  encoded = tokenizer.texts_to_sequences([n_sentence])
  pad_new = pad_sequences(encoded, maxlen = max_len)

  score = float(loaded_model.predict(pad_new))

  if(score > 0.5):
    # return 1
    print("{:.2f}% 확률로 긍정 리뷰입니다.".format(score * 100))
  else:
    # return 0
    print("{:.2f}% 확률로 부정 리뷰입니다.".format((1 - score) * 100))


if __name__ == '__main__':
    print("--리뷰 분석 시작--")
    print("문장 입력을 해주세요.")
    review = str(input())
    sentiment(review)
