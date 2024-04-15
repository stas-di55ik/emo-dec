from .models import SentimentAnalysisSource
from django.forms import ModelForm, Textarea


class SentimentAnalysisSourceForm(ModelForm):
    class Meta:
        model = SentimentAnalysisSource
        fields = ['text']
        widgets = {
            "title": Textarea(attrs={
                "class": "form-control",
                "placeholder": "Enter text for sentiment analysis"
            })
        }
