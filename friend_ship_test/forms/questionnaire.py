from django import forms


class QuestionnaireForm(forms.Form):
    question = forms.CharField(max_length=200, required=False)
    question_id = forms.CharField(widget=forms.HiddenInput)
    answer = forms.CharField(max_length=200, required=True, widget=forms.Textarea)
