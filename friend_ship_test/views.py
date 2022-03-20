from django.forms import formset_factory
from django.shortcuts import render, get_object_or_404
from django.views import View

from common.constants import TEST_COMPARISON_MESSAGE, MAX_QUESTIONS_ALLOWED
from common.user_helpers import create_user
from friend_ship_test.forms.friend_ship_attempt_test import FriendShipAttemptTestForm
from friend_ship_test.forms.friend_ship_create_test import FriendShipCreateTestForm
from friend_ship_test.forms.questionnaire import QuestionnaireForm, QuestionnaireAttemptForm
from friend_ship_test.models import (
    Question, FriendShipTestQuestionnaire, FriendShipTestAnswer,
    FriendShipTestResult, FriendShipTest
)


class FriendShipTestView(View):
    template_name = 'create_test.html'
    comparison_result = ''

    def update_test_results(self, friend_ship_test_result_instance, test_result_info):
        friend_ship_test_result_instance.questions_attempted = test_result_info["questions_attempted"]
        friend_ship_test_result_instance.correct_answers = test_result_info["correct_answers"]
        friend_ship_test_result_instance.wrong_answers = test_result_info["wrong_answers"]
        friend_ship_test_result_instance.save()

    @staticmethod
    def create_initial_data_for_questions(questions):
        initial_questions_data = []
        for question in questions:
            initial_questions_data.append({
                'question': question.question_text,
                'question_id': question.id,
                'question_instance': question
            })
        return initial_questions_data

    def prepare_questionnaire_form_set(self, post_data={}, initial_questions_data=[]):
        if not post_data:
            questionnaire_form_set_instance = self.questionnaire_form_set(initial=initial_questions_data)
        else:
            questionnaire_form_set_instance = self.questionnaire_form_set(post_data, initial=initial_questions_data)
        for form_index, form in enumerate(questionnaire_form_set_instance):
            try:
                form.fields['answer'].queryset = initial_questions_data[form_index]['question_instance'].answers.all()
            except IndexError:
                pass
        return questionnaire_form_set_instance

    @staticmethod
    def save_friend_ship_test_answer(
            friend_ship_test_result_instance,
            friend_ship_questionnaire_instance,
            answer,
            test_result,
            friend_ship_test_user
    ):
        friend_ship_answer_instance = FriendShipTestAnswer(
            question=friend_ship_questionnaire_instance,
            answer=answer,
            result=test_result,
            created_by=friend_ship_test_user
        )
        friend_ship_answer_instance.save()
        friend_ship_test_result_instance.answers.add(friend_ship_answer_instance)
        return friend_ship_answer_instance

    @staticmethod
    def load_question_and_verify_answer(question_id, answer):
        question = Question.objects.get(id=question_id)
        test_result = question.verify_answer(answer)
        return question, test_result


class FriendShipCreateTestView(FriendShipTestView):
    friend_ship_test_form = FriendShipCreateTestForm
    questionnaire_form_set = formset_factory(QuestionnaireForm, extra=0)

    def get(self, request, *args, **kwargs):
        initial_questions_data = FriendShipTestView.create_initial_data_for_questions(Question.get_random_questions())
        return render(
            request,
            self.template_name,
            {
                'friend_ship_test_form': self.friend_ship_test_form(),
                'questionnaire_form_set': self.prepare_questionnaire_form_set(
                    initial_questions_data=initial_questions_data
                )
            }
        )

    def post(self, request, *args, **kwargs):
        friend_ship_test_form, friend_ship_test_created = self.friend_ship_test_form(request.POST), True
        friend_ship_test_instance = None
        test_result_info = {
            "questions_attempted": 0,
            "correct_answers": 0,
            "wrong_answers": 0
        }
        initial_questions_data = FriendShipTestView.create_initial_data_for_questions(Question.get_random_questions())
        questionnaire_form_set_submitted = self.prepare_questionnaire_form_set(
            post_data=request.POST,
            initial_questions_data=initial_questions_data
        )
        if friend_ship_test_form.is_valid() and questionnaire_form_set_submitted.is_valid():
            friend_ship_test_instance = friend_ship_test_form.save()
            friend_ship_test_user = friend_ship_test_instance.create_user()
            friend_ship_test_result_instance = FriendShipTestResult(
                friend_ship_test=friend_ship_test_instance,
                created_by=friend_ship_test_user
            )
            friend_ship_test_result_instance.save()
            selected_question_count = 0
            for form in questionnaire_form_set_submitted:
                form_data = form.cleaned_data
                selected_answer = form_data['answer']
                if selected_answer and selected_question_count <= MAX_QUESTIONS_ALLOWED:
                    selected_question_count += 1
                    question, test_result = FriendShipTestView.load_question_and_verify_answer(
                        question_id=form_data['question_id'],
                        answer=selected_answer.answer_text
                    )
                    friend_ship_test_instance.questions.add(question)
                    friend_ship_questionnaire_instance = FriendShipTestQuestionnaire.objects.filter(
                        question=question,
                        friend_ship_test=friend_ship_test_instance
                    ).first()
                    FriendShipTestView.save_friend_ship_test_answer(
                        friend_ship_test_result_instance,
                        friend_ship_questionnaire_instance,
                        answer=form_data['answer'],
                        test_result=test_result,
                        friend_ship_test_user=friend_ship_test_user
                    )
                    test_result_info["questions_attempted"] += 1
                    if test_result:
                        test_result_info["correct_answers"] += 1
                    else:
                        test_result_info["wrong_answers"] += 1
            self.update_test_results(friend_ship_test_result_instance, test_result_info)
        else:
            friend_ship_test_created = False
        return render(
            request,
            self.template_name,
            {
                'friend_ship_test_form': friend_ship_test_form,
                'friend_ship_test_created': friend_ship_test_created,
                'friend_ship_test_instance': friend_ship_test_instance,
                'questionnaire_form_set': questionnaire_form_set_submitted
            }
        )


class FriendShipTestAttemptView(FriendShipTestView):
    friend_ship_attempt_test_form = FriendShipAttemptTestForm
    questionnaire_form_set = formset_factory(QuestionnaireAttemptForm, extra=0)

    def get(self, request, *args, **kwargs):
        friend_ship_test = get_object_or_404(FriendShipTest, uuid=kwargs['test_uuid'])
        form = self.friend_ship_attempt_test_form(
            initial={
                'name': friend_ship_test.name,
                'friend_ship_test_id': kwargs['test_uuid'],
                'created_by': friend_ship_test.created_by.username
            }
        )
        initial_questions_data = FriendShipTestView.create_initial_data_for_questions(
            friend_ship_test.questions.all()
        )
        return render(
            request,
            self.template_name,
            {
                'friend_ship_test_form': form,
                'questionnaire_form_set': self.prepare_questionnaire_form_set(
                    initial_questions_data=initial_questions_data
                )
            }
        )

    def post(self, request, *args, **kwargs):
        friend_ship_attempt_test_form = self.friend_ship_attempt_test_form(request.POST)
        friend_ship_test_submitted = True
        friend_ship_test_instance = get_object_or_404(FriendShipTest, uuid=kwargs['test_uuid'])
        test_result_info = {
            "questions_attempted": 0,
            "correct_answers": 0,
            "wrong_answers": 0,
            "total_matched_answers": 0
        }
        initial_questions_data = FriendShipTestView.create_initial_data_for_questions(
            friend_ship_test_instance.questions.all()
        )
        questionnaire_form_set_submitted = self.prepare_questionnaire_form_set(
            post_data=request.POST,
            initial_questions_data=initial_questions_data
        )
        if friend_ship_attempt_test_form.is_valid() and questionnaire_form_set_submitted.is_valid():
            friend_ship_attempt_test_form_data = friend_ship_attempt_test_form.cleaned_data
            friend_ship_test_user = create_user(friend_ship_attempt_test_form_data['user_name'])
            friend_ship_test_result_instance = FriendShipTestResult(
                friend_ship_test=friend_ship_test_instance,
                created_by=friend_ship_test_user
            )
            friend_ship_test_result_instance.save()
            for form in questionnaire_form_set_submitted:
                form_data = form.cleaned_data
                question = get_object_or_404(Question, pk=form_data['question_id'])
                friend_ship_questionnaire_instance = FriendShipTestQuestionnaire.objects.filter(
                    question=question,
                    friend_ship_test=friend_ship_test_instance
                ).first()
                friend_ship_owner_test_answer_instance = FriendShipTestAnswer.objects.filter(
                    question=friend_ship_questionnaire_instance,
                    created_by=friend_ship_test_instance.created_by
                ).first()
                test_result = friend_ship_owner_test_answer_instance.verify_answer(form_data['answer'])
                if friend_ship_owner_test_answer_instance.result == test_result:
                    test_result_info["total_matched_answers"] += 1
                FriendShipTestView.save_friend_ship_test_answer(
                    friend_ship_test_result_instance,
                    friend_ship_questionnaire_instance,
                    answer=form_data['answer'],
                    test_result=test_result,
                    friend_ship_test_user=friend_ship_test_user
                )
                test_result_info["questions_attempted"] += 1
                if test_result:
                    test_result_info["correct_answers"] += 1
                else:
                    test_result_info["wrong_answers"] += 1
            self.update_test_results(friend_ship_test_result_instance, test_result_info)
            percentage = (test_result_info["total_matched_answers"] / test_result_info["questions_attempted"]) * 100
            self.comparison_result = TEST_COMPARISON_MESSAGE.format(
                friend_name=friend_ship_test_instance.created_by.username,
                percentage=percentage
            )
        else:
            friend_ship_test_submitted = False
        return render(
            request,
            self.template_name,
            {
                'friend_ship_test_form': friend_ship_attempt_test_form,
                'friend_ship_test_submitted': friend_ship_test_submitted,
                'comparison_result': self.comparison_result,
                'friend_ship_test_created': friend_ship_test_submitted,
                'friend_ship_test_instance': friend_ship_test_instance,
                'questionnaire_form_set': questionnaire_form_set_submitted
            }
        )
