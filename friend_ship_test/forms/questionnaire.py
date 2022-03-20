from django import forms

from friend_ship_test.models import Answer


class QuestionnaireForm(forms.Form):
    question = forms.CharField(max_length=200, required=False)
    question_id = forms.CharField(widget=forms.HiddenInput)
    answer = forms.ModelChoiceField(
        queryset=Answer.objects.none(),
        empty_label='Select to include in your friend ship test',
        required=False
    )


class QuestionnaireAttemptForm(QuestionnaireForm):
    answer = forms.ModelChoiceField(
        queryset=Answer.objects.none(),
        empty_label='Select Answer from below',
        required=True
    )
