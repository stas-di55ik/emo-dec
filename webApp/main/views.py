from django.shortcuts import render, redirect
from django.urls import reverse


from .forms import SentimentAnalysisSourceForm
from .models import TextSentimentAnalyser, PhotoEmotionDetector, InstagramAPIHelper

import os
import requests
from threading import Timer

import datetime
import math

from .secrets import IG_APP_ID, IG_APP_SECRET


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
        input_file_name = f'{timestamp}_{input_file.name}'
        input_file_path = f'main/static/main/tmp/photoAnalysis/req/{input_file_name}'
        PhotoEmotionDetector.download_image(input_file, input_file_path)
        result = PhotoEmotionDetector.analyze(input_file_path, input_file_name)
        print(result)

        return render(request, 'main/faceEmotionDetectionResult.html', result)

    return render(request, 'main/faceEmotionDetectionInput.html')


def textSentimentAnalysis(request):
    error = ''
    if request.method == 'POST':
        form = SentimentAnalysisSourceForm(request.POST)
        if form.is_valid():
            input_text = form.cleaned_data['text']
            timestamp = math.floor(datetime.datetime.now().timestamp() * 1000000)
            result = TextSentimentAnalyser.analyze(input_text, timestamp)
            print(result)

            return render(request, 'main/textSentimentAnalysisResult.html', result)
        else:
            error = 'The form is invalid!'

    form = SentimentAnalysisSourceForm()
    data = {
        'form': form,
        'error': error
    }

    return render(request, 'main/textSentimentAnalysisInput.html', data)


def igPublicationAudit(request):
    ig_helper = InstagramAPIHelper(IG_APP_ID, IG_APP_SECRET)
    ig_helper.initialize_api()
    login_url = ig_helper.get_login_url()

    if request.method == 'POST':
        ig_helper.init_token()
        profile_data = ig_helper.get_profile_data()
        request.session['profile_data'] = profile_data
        return redirect('igPublicationAuditProfile')

    data = {'login_url': login_url}

    return render(request, 'main/igPublicationAuditBegin.html', data)


def igPublicationAuditProfile(request):
    profile_data = request.session.get('profile_data')
    if request.method == 'POST':
        timestamp = math.floor(datetime.datetime.now().timestamp() * 1000000)
        input_publication_id = request.POST.get('publication_id')

        tsa_succeed = False
        tsa_web_dict = {}
        fer_succeed = False
        fer_web_dicts = []

        existing = {}
        for publication in profile_data['user_media']['data']:
            if input_publication_id == publication['id']:
                existing = publication

        tsa_result = None
        if 'caption' in existing:
            tsa_succeed = True
            tsa_result = TextSentimentAnalyser.analyze(existing['caption'], timestamp)

        input_images = []
        if existing['media_type'] == 'CAROUSEL_ALBUM':
            for item in existing['children']['data']:
                if item['media_type'] == 'IMAGE':
                    file_name = f'{timestamp}_{item['id']}.jpg'
                    file_path = f'main/static/main/tmp/photoAnalysis/req/{file_name}'
                    download_status = InstagramAPIHelper.download_image_by_url(item['media_url'], file_path)
                    if download_status:
                        input_images.append({'file_name': file_name, 'file_path': file_path})

        if existing['media_type'] == 'IMAGE':
            file_name = f'{timestamp}_{existing['id']}.jpg'
            file_path = f'main/static/main/tmp/photoAnalysis/req/{file_name}'
            download_status = InstagramAPIHelper.download_image_by_url(existing['media_url'], file_path)
            if download_status:
                input_images.append({'file_name': file_name, 'file_path': file_path})

        if len(input_images) > 0:
            fer_succeed = True
            for img in input_images:
                result = PhotoEmotionDetector.analyze(img['file_path'], img['file_name'])
                fer_web_dicts.append(result)

        return render(request, 'main/igPublicationAuditProfileResult.html', {
            'tsa_succeed': tsa_succeed,
            'tsa_web_dict': tsa_result,
            'fer_succeed': fer_succeed,
            'fer_web_dicts': fer_web_dicts
        })

    return render(request, 'main/igPublicationAuditProfileOutput.html', profile_data)
