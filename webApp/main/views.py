from django.shortcuts import render

from .forms import SentimentAnalysisSourceForm
from .models import TextSentimentAnalyser, PhotoEmotionDetector

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
    if request.method == 'POST' and request.FILES.get('input_img'):
        timestamp = math.floor(datetime.datetime.now().timestamp() * 1000000)
        input_file = request.FILES['input_img']

        input_file_path = f'main/static/main/tmp/photoAnalysis/req/{timestamp}_{input_file.name}'
        with open(input_file_path, 'wb') as destination:
            for chunk in input_file.chunks():
                destination.write(chunk)
        print(f'Uploaded image saved at ({timestamp}):', input_file_path)

        result = PhotoEmotionDetector.analyze(input_file_path, timestamp)
        print(result)

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
