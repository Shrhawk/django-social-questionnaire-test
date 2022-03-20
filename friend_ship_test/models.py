import random
import uuid

from django.contrib.auth.models import User
from django.db import models

from common.base_model import BaseModel
from common.user_helpers import create_user


class Answer(BaseModel):
    answer_text = models.CharField(max_length=200)

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return str(self.id) + '.' + self.answer_text


class Question(BaseModel):
    question_text = models.CharField(max_length=200)
    answers = models.ManyToManyField(Answer)

    def __str__(self):
        return self.question_text

    @classmethod
    def get_random_questions(cls):
        all_questions = list(cls.objects.all())
        try:
            random_questions = random.sample(all_questions, 10)
        except ValueError:
            return all_questions
        return random_questions

    def verify_answer(self, given_answer):
        given_answer = str(given_answer).lower()
        for answer in self.answers.all():
            if given_answer in str(answer.answer_text).lower():
                return True
        return False


class FriendShipTest(BaseModel):
    name = models.CharField(max_length=200)
    user_name = models.CharField(max_length=200)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    questions = models.ManyToManyField(Question, through='FriendShipTestQuestionnaire')
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=['uuid']),
        ]

    def __str__(self):
        return self.name

    def create_user(self):
        user = create_user(self.user_name)
        self.created_by = user
        self.save()
        return self.created_by


class FriendShipTestQuestionnaire(BaseModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    friend_ship_test = models.ForeignKey(FriendShipTest, on_delete=models.CASCADE)

    def __str__(self):
        return self.question.question_text


class FriendShipTestAnswer(BaseModel):
    question = models.ForeignKey(FriendShipTestQuestionnaire, on_delete=models.CASCADE)
    answer = models.CharField(max_length=200)
    result = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return " ==> ".join([
            self.question.friend_ship_test.name,
            self.created_by.username,
            self.question.question.question_text,
            self.answer,
            str(self.result)
        ])


class FriendShipTestResult(BaseModel):
    friend_ship_test = models.ForeignKey(FriendShipTest, on_delete=models.CASCADE)
    questions_attempted = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    wrong_answers = models.IntegerField(default=0)
    answers = models.ManyToManyField(FriendShipTestAnswer)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return " ==> ".join([self.friend_ship_test.name, self.created_by.username])
