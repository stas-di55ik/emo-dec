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

        input_file_path = f'main/static/main/tmp/photoAnalysis/req/{timestamp}_{input_file.name}'
        with open(input_file_path, 'wb') as destination:
            for chunk in input_file.chunks():
                destination.write(chunk)
        print(f'Uploaded image saved at ({timestamp}):', input_file_path)

        result = PhotoEmotionDetector.analyze(input_file_path, timestamp)
        print(result)

        if result['status']:
            result_for_web = []
            for element in result['result']:
                Timer(7.0, lambda el=element: os.remove(el['file_path'])).start()
                result_for_web.append({
                    'emotion': element['emotion'],
                    'file_path': element['file_path'].lstrip()[5:]
                })
            Timer(7.0, lambda: os.remove(input_file_path)).start()

            web_dict = {
                'status': result['status'],
                'result': result_for_web,
                'input_file_path': input_file_path.lstrip()[5:]
            }

            return render(request, 'main/faceEmotionDetectionResult.html', web_dict)
        else:
            Timer(7.0, lambda: os.remove(input_file_path)).start()
            web_dict = {
                'status': result['status'],
                'input_file_path': input_file_path.lstrip()[5:]
            }

            return render(request, 'main/faceEmotionDetectionResult.html', web_dict)

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
    ig_helper = InstagramAPIHelper(IG_APP_ID, IG_APP_SECRET)
    ig_helper.initialize_api()
    login_url = ig_helper.get_login_url()

    if request.method == 'POST':
        ig_helper.init_token(request)
        profile_data = ig_helper.get_profile_data()
        request.session['profile_data'] = profile_data
        return redirect('igPublicationAuditProfile')

    data = {'login_url': login_url}

    return render(request, 'main/igPublicationAudit.html', data)


def igPublicationAuditProfile(request):
    profile_data = request.session.get('profile_data')
    if request.method == 'POST':
        timestamp = math.floor(datetime.datetime.now().timestamp() * 1000000)
        input_publication_id = request.POST.get('publication_id')

        existing = {}
        for publication in profile_data['user_media']['data']:
            if input_publication_id == publication['id']:
                existing = publication

        if existing['caption']:
            tsa_result = TextSentimentAnalyser.analyze(existing['caption'], timestamp)
            # Timer(15.0, lambda: os.remove(tsa_result['plot_path'])).start()

            tsa_web_dict = {'result': tsa_result['result'],
                            'plot_path': tsa_result['plot_path'].lstrip()[5:],
                            'plot_succeed': bool(tsa_result['emotion_list']),
                            'input_text': tsa_result['input_text']}
        else:
            tsa_result = False

        image_paths = []
        if existing['media_type'] == 'CAROUSEL_ALBUM':
            for item in existing['children']['data']:
                if item['media_type'] == 'IMAGE':
                    file_path = f'main/static/main/tmp/photoAnalysis/req/{timestamp}_{item['id']}.jpg'
                    download_status = download_image(item['media_url'], file_path)
                    if download_status:
                        image_paths.append(file_path)

        if existing['media_type'] == 'IMAGE':
            file_path = f'main/static/main/tmp/photoAnalysis/req/{timestamp}_{existing['id']}.jpg'
            download_status = download_image(existing['media_url'], file_path)
            if download_status:
                image_paths.append(file_path)

        print(f'image_paths: {image_paths}')

    return render(request, 'main/igPublicationAuditProfile.html', profile_data)


def download_image(url, save_path):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"Image downloaded successfully to {save_path}")

        return True
    except Exception as e:
        print(f"Error downloading image: {e}")

        return False
