from django.shortcuts import render

from .forms import SentimentAnalysisSourceForm
from .models import TextSentimentAnalyser

import os
from threading import Timer

import datetime
import math


def index(request):
    return render(request, 'main/index.html')


def about(request):
    return render(request, 'main/about.html')


def contacts(request):
    return render(request, 'main/contacts.html')


def faceEmotionDetection(request):
    return render(request, 'main/faceEmotionDetection.html')


def textSentimentAnalysis(request):
    error = ''
    if request.method == 'POST':
        form = SentimentAnalysisSourceForm(request.POST)
        if form.is_valid():
            input_text = form.cleaned_data['text']
            timestamp = math.floor(datetime.datetime.now().timestamp() * 1000000)
            result = TextSentimentAnalyser.analyze(input_text, timestamp)
            Timer(5.0, lambda: os.remove(result['plot_path'])).start()

            web_dict = {'result': result['result'],
                        'plot_path': result['plot_path'].lstrip()[5:],
                        'plot_succeed': bool(result['emotion_list']),
                        'input_text': result['input_text']}

            return render(request, 'main/textSentimentAnalysisResult.html', web_dict)
        else:
            error = 'The form is invalid!'
    form = SentimentAnalysisSourceForm()
    data = {
        'form': form,
        'error': error
    }

    return render(request, 'main/textSentimentAnalysis.html', data)


def igPublicationAudit(request):
    return render(request, 'main/igPublicationAudit.html')
