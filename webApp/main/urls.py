from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('about', views.about, name='about'),
    path('contacts', views.contacts, name='contacts'),
    path('faceEmotionDetection', views.faceEmotionDetection, name='faceEmotionDetection'),
    path('textSentimentAnalysis', views.textSentimentAnalysis, name='textSentimentAnalysis'),
    path('igPublicationAudit', views.igPublicationAudit, name='igPublicationAudit'),
    path('igPublicationAuditProfile', views.igPublicationAuditProfile, name='igPublicationAuditProfile'),
]
