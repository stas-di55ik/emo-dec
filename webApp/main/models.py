from django.db import models

import datetime
import math

import string
from collections import Counter
import matplotlib.pyplot as plt

from deep_translator import GoogleTranslator

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer

import cv2
from deepface import DeepFace

from instagram_basic_display.InstagramBasicDisplay import InstagramBasicDisplay
import requests
from .secrets import IG_ACCESS_TOKEN


class SentimentAnalysisSource(models.Model):
    text = models.TextField('Text')

    def __str__(self):
        return self.text


class TextSentimentAnalyser:
    @staticmethod
    def analyze(input_text, timestamp):
        print(f"input_text: {input_text}")
        clean_text = TextSentimentAnalyser.get_clean_text(input_text)
        print(f"clean_text: {clean_text}")
        valuable_words = TextSentimentAnalyser.get_valuable_words(clean_text)
        print(f"valuable_words: {valuable_words}")
        emotion_list = TextSentimentAnalyser.get_emotion_list(valuable_words)
        print(f"emotion_list: {emotion_list}")
        result = TextSentimentAnalyser.sentiment_analyse(clean_text)
        print(f"result: {result}")
        plot_path = TextSentimentAnalyser.plot(emotion_list, timestamp)
        print(f"plot_path: {plot_path}")

        return {'input_text': input_text, 'result': result, 'emotion_list': emotion_list, 'plot_path': plot_path}

    @staticmethod
    def get_clean_text(input_text):
        translated_text = GoogleTranslator(source='auto', target='en').translate(input_text)
        lower_case = translated_text.lower()
        clean_text = lower_case.translate(str.maketrans('', '', string.punctuation))

        return clean_text

    @staticmethod
    def get_valuable_words(input_text):
        tokenized_words = word_tokenize(input_text, "english")
        valuable_words = TextSentimentAnalyser.remove_stopwords(tokenized_words)

        return valuable_words

    @staticmethod
    def remove_stopwords(tokenized_words):
        final_words = []
        for word in tokenized_words:
            if word not in stopwords.words('english'):
                final_words.append(word)

        return final_words

    @staticmethod
    def get_emotion_list(valuable_words):
        emotion_list = []
        with open('main/static/main/cache/emotions.txt', 'r') as file:
            for line in file:
                clean_line = line.replace("\n", '').replace(",", '').replace("'", '').strip()
                word, emotion = clean_line.split(': ')

                if word in valuable_words:
                    emotion_list.append(emotion)
        counted_emotion_list = Counter(emotion_list)

        return counted_emotion_list

    @staticmethod
    def sentiment_analyse(input_text):
        score = SentimentIntensityAnalyzer().polarity_scores(input_text)

        return {
            'negative': f'{round(score['neg'] * 100, 2)}%',
            'positive': f'{round(score['pos'] * 100, 2)}%',
            'neutrality': f'{round(score['neu'] * 100, 2)}%'
        }

    @staticmethod
    def plot(emotion_list, timestamp):
        fig, ax1 = plt.subplots()
        ax1.bar(emotion_list.keys(), emotion_list.values())
        fig.autofmt_xdate()
        filename = f"main/static/main/tmp/textAnalysis/{timestamp}_graph.png"
        plt.savefig(filename)

        return filename


class PhotoEmotionDetector:
    @staticmethod
    def analyze(input_file_path, timestamp):
        img = cv2.imread(input_file_path)
        try:
            predictions = DeepFace.analyze(img)

            return {'status': True, 'result': PhotoEmotionDetector.handle_predictions(predictions, img, timestamp)}
        except:
            return {'status': False}

    @staticmethod
    def crop_face(img, region, index, timestamp):
        cropped_image = img[region['y']:region['y'] + region['h'], region['x']:region['x'] + region['w']]
        file_path = f"main/static/main/tmp/photoAnalysis/res/{index}_{timestamp}_face.png"
        cv2.imwrite(file_path, cropped_image)

        return file_path

    @staticmethod
    def handle_predictions(predictions, img, timestamp):
        result = []
        for index, value in enumerate(predictions):
            # print(f'index: {index}, emotion: {value['emotion']}, region: {value['region']}')
            result.append({
                'emotion': PhotoEmotionDetector.formalize_answer(value['emotion']),
                'file_path': PhotoEmotionDetector.crop_face(img, value['region'], index, timestamp)
            })

        return result

    @staticmethod
    def formalize_answer(emotion):
        return {
            'angry': f'{round(emotion['angry'], 2)}%',
            'disgust': f'{round(emotion['disgust'], 2)}%',
            'fear': f'{round(emotion['fear'], 2)}%',
            'happy': f'{round(emotion['happy'], 2)}%',
            'sad': f'{round(emotion['sad'], 2)}%',
            'surprise': f'{round(emotion['surprise'], 2)}%',
            'neutral': f'{round(emotion['neutral'], 2)}%',
        }


class InstagramAPIHelper:
    def __init__(self, ig_app_id, ig_app_secret):
        self.ig_app_id = ig_app_id
        self.ig_app_secret = ig_app_secret
        self.api = None

    def initialize_api(self):
        self.api = InstagramBasicDisplay(
            app_id=self.ig_app_id,
            app_secret=self.ig_app_secret,
            redirect_url='https://www.google.com.ua/?hl=uk',
        )

    def get_login_url(self):
        if self.api is None:
            self.initialize_api()

        return self.api.get_login_url()

    def init_token(self, request):
        # code = request.args.get('code')
        # short_lived_token = self.api.get_o_auth_token(code)
        # long_lived_token = self.api.get_long_lived_token(short_lived_token.get('access_token'))
        # access_token = long_lived_token.access_token
        access_token = IG_ACCESS_TOKEN
        self.api.set_access_token(access_token)

    def get_profile_data(self):
        return {'profile': self.api.get_user_profile(), 'user_media': self.api.get_user_media()}
