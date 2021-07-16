from django import forms
from.models import Review

# Make your forms here

class RatingForm(forms.Form):
    rating = forms.IntegerField(min_value=0,max_value=5, widget=forms.IntegerField(attrs={'placeholder':'Rating'}))
    review = forms.CharField(widget=forms.Textarea(attrs={'placeholder':'Review'}))
    
    class Meta:
        model = Review
        fields = {'rating','review'}    