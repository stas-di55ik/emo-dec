from django.shortcuts import render


def index(request):
    return render(request, 'main/index.html')


def about(request):
    return render(request, 'main/about.html')


def contacts(request):
    return render(request, 'main/contacts.html')


def faceEmotionDetection(request):
    return render(request, 'main/faceEmotionDetection.html')


def textSentimentAnalysis(request):
    return render(request, 'main/textSentimentAnalysis.html')


def igPublicationAudit(request):
    return render(request, 'main/igPublicationAudit.html')
