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

        return {'negative': f'{math.floor(score['neg'] * 100)}%',
                'positive': f'{math.floor(score['pos'] * 100)}%',
                'neutrality': f'{math.floor(score['neu'] * 100)}%'}

    @staticmethod
    def plot(emotion_list, timestamp):
        fig, ax1 = plt.subplots()
        ax1.bar(emotion_list.keys(), emotion_list.values())
        fig.autofmt_xdate()
        filename = f"main/static/main/tmp/textAnalysis/{timestamp}graph.png"
        plt.savefig(filename)

        return filename

# test = TextSentimentAnalyser.analyze('lol kek insecure', math.floor(datetime.datetime.now().timestamp() * 1000000))


# class FaceEmotionRecognitionSource(models.Model):
#     img = models.ImageField
#
#     def __str__(self):
#         return self.img

