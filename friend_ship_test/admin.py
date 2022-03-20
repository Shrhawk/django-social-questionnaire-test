from django import forms
from django.contrib import admin

from .models import (
    Question, Answer, FriendShipTest, FriendShipTestQuestionnaire, FriendShipTestAnswer, FriendShipTestResult
)


class QuestionForm(forms.Form):
    question = forms.CharField(max_length=200)
    answer = forms.CharField(max_length=200)


class FriendShipTestQuestionnaireInline(admin.StackedInline):
    model = FriendShipTestQuestionnaire


@admin.register(FriendShipTest)
class FriendShipTestAdmin(admin.ModelAdmin):
    inlines = [FriendShipTestQuestionnaireInline]


admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(FriendShipTestAnswer)
admin.site.register(FriendShipTestResult)
