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
        download_image_from_web(input_file, input_file_path)
        result = PhotoEmotionDetector.analyze(input_file_path, input_file_name)
        print(result)

        return render(request, 'main/faceEmotionDetectionResult.html', prepare_fer_web_dict(result, input_file_path))

    return render(request, 'main/faceEmotionDetection.html')


def textSentimentAnalysis(request):
    error = ''
    if request.method == 'POST':
        form = SentimentAnalysisSourceForm(request.POST)
        if form.is_valid():
            input_text = form.cleaned_data['text']
            timestamp = math.floor(datetime.datetime.now().timestamp() * 1000000)
            result = TextSentimentAnalyser.analyze(input_text, timestamp)

            return render(request, 'main/textSentimentAnalysisResult.html', prepare_tsa_web_dict(result))
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

        tsa_succeed = False
        tsa_web_dict = {}
        fer_succeed = False
        fer_web_dicts = []

        existing = {}
        for publication in profile_data['user_media']['data']:
            if input_publication_id == publication['id']:
                existing = publication

        if 'caption' in existing:
            tsa_succeed = True
            tsa_result = TextSentimentAnalyser.analyze(existing['caption'], timestamp)
            tsa_web_dict = prepare_tsa_web_dict(tsa_result)

        input_images = []
        if existing['media_type'] == 'CAROUSEL_ALBUM':
            for item in existing['children']['data']:
                if item['media_type'] == 'IMAGE':
                    file_name = f'{timestamp}_{item['id']}.jpg'
                    file_path = f'main/static/main/tmp/photoAnalysis/req/{file_name}'
                    download_status = download_image_by_url(item['media_url'], file_path)
                    if download_status:
                        input_images.append({'file_name': file_name, 'file_path': file_path})

        if existing['media_type'] == 'IMAGE':
            file_name = f'{timestamp}_{existing['id']}.jpg'
            file_path = f'main/static/main/tmp/photoAnalysis/req/{file_name}'
            download_status = download_image_by_url(existing['media_url'], file_path)
            if download_status:
                input_images.append({'file_name': file_name, 'file_path': file_path})

        if len(input_images) > 0:
            fer_succeed = True
            for img in input_images:
                result = PhotoEmotionDetector.analyze(img['file_path'], img['file_name'])
                fer_web_dicts.append(prepare_fer_web_dict(result, img['file_path']))

        return render(request, 'main/igPublicationAuditProfileResult.html', {
            'tsa_succeed': tsa_succeed,
            'tsa_web_dict': tsa_web_dict,
            'fer_succeed': fer_succeed,
            'fer_web_dicts': fer_web_dicts
        })

    return render(request, 'main/igPublicationAuditProfile.html', profile_data)


def download_image_from_web(input_file, input_file_path):
    with open(input_file_path, 'wb') as destination:
        for chunk in input_file.chunks():
            destination.write(chunk)
    print(f'Uploaded image saved at:', input_file_path)


def download_image_by_url(url, save_path):
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


def prepare_fer_web_dict(result, input_file_path):
    if result['status']:
        result_for_web = []
        for element in result['result']:
            Timer(120.0, lambda el=element: os.remove(el['file_path'])).start()
            result_for_web.append({
                'emotion': element['emotion'],
                'file_path': element['file_path'].lstrip()[5:]
            })
        Timer(120.0, lambda: os.remove(input_file_path)).start()

        web_dict = {
            'status': result['status'],
            'result': result_for_web,
            'input_file_path': input_file_path.lstrip()[5:]
        }

    else:
        Timer(120.0, lambda: os.remove(input_file_path)).start()
        web_dict = {
            'status': result['status'],
            'input_file_path': input_file_path.lstrip()[5:]
        }

    return web_dict


def prepare_tsa_web_dict(result):
    Timer(120.0, lambda: os.remove(result['plot_path'])).start()

    return {
        'result': result['result'],
        'plot_path': result['plot_path'].lstrip()[5:],
        'plot_succeed': bool(result['emotion_list']),
        'input_text': result['input_text']
    }
