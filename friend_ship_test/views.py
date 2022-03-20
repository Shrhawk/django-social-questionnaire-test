from django.forms import formset_factory
from django.shortcuts import render, get_object_or_404
from django.views import View

from common.constants import TEST_COMPARISON_MESSAGE
from common.user_helpers import create_user
from friend_ship_test.forms.friend_ship_attempt_test import FriendShipAttemptTestForm
from friend_ship_test.forms.friend_ship_create_test import FriendShipCreateTestForm
from friend_ship_test.forms.questionnaire import QuestionnaireForm
from friend_ship_test.models import (
    Question, FriendShipTestQuestionnaire, FriendShipTestAnswer,
    FriendShipTestResult, FriendShipTest
)


class FriendShipTestView(View):
    questionnaire_form = QuestionnaireForm
    questionnaire_form_set = formset_factory(questionnaire_form, extra=0)
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
                'question_id': question.id
            })
        return initial_questions_data

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

    def get(self, request, *args, **kwargs):
        initial_questions_data = FriendShipTestView.create_initial_data_for_questions(Question.get_random_questions())
        return render(
            request,
            self.template_name,
            {
                'friend_ship_test_form': self.friend_ship_test_form(),
                'questionnaire_form_set': self.questionnaire_form_set(initial=initial_questions_data)
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
        questionnaire_form_set_submitted = self.questionnaire_form_set(request.POST)
        if friend_ship_test_form.is_valid() and questionnaire_form_set_submitted.is_valid():
            friend_ship_test_instance = friend_ship_test_form.save()
            friend_ship_test_user = friend_ship_test_instance.create_user()
            friend_ship_test_result_instance = FriendShipTestResult(
                friend_ship_test=friend_ship_test_instance,
                created_by=friend_ship_test_user
            )
            friend_ship_test_result_instance.save()
            for form in questionnaire_form_set_submitted:
                form_data = form.cleaned_data
                question, test_result = FriendShipTestView.load_question_and_verify_answer(
                    question_id=form_data['question_id'],
                    answer=form_data['answer']
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
                'questionnaire_form_set': self.questionnaire_form_set(initial=initial_questions_data)
            }
        )

    def compare_test_results(self, owner_test_results, user_test_results, owner_profile):
        """
        Compare owner test results with friend test results
        """
        total_questions, total_matched_answers = 0, 0
        for (owner_test_result, user_test_result) in zip(owner_test_results, user_test_results):
            total_questions += 1
            if (
                    owner_test_result.question_id == user_test_result.question_id and
                    owner_test_result.result == user_test_result.result and
                    str(owner_test_result.answer).lower() == str(user_test_result.answer).lower()
            ):
                total_matched_answers += 1
        percentage = (total_matched_answers / total_questions) * 100
        self.comparison_result = TEST_COMPARISON_MESSAGE.format(
            friend_name=owner_profile.username,
            percentage=percentage
        )

    def post(self, request, *args, **kwargs):
        friend_ship_attempt_test_form = self.friend_ship_attempt_test_form(request.POST)
        friend_ship_test_submitted = True
        friend_ship_test_instance = None
        test_result_info = {
            "questions_attempted": 0,
            "correct_answers": 0,
            "wrong_answers": 0
        }
        questionnaire_form_set_submitted = self.questionnaire_form_set(request.POST)
        if friend_ship_attempt_test_form.is_valid() and questionnaire_form_set_submitted.is_valid():
            friend_ship_attempt_test_form_data = friend_ship_attempt_test_form.cleaned_data
            friend_ship_test_user = create_user(friend_ship_attempt_test_form_data['user_name'])
            friend_ship_test_instance = get_object_or_404(
                FriendShipTest,
                uuid=friend_ship_attempt_test_form_data['friend_ship_test_id']
            )
            friend_ship_test_result_instance = FriendShipTestResult(
                friend_ship_test=friend_ship_test_instance,
                created_by=friend_ship_test_user
            )
            friend_ship_test_result_instance.save()
            for form in questionnaire_form_set_submitted:
                form_data = form.cleaned_data
                question, test_result = FriendShipTestView.load_question_and_verify_answer(
                    question_id=form_data['question_id'],
                    answer=form_data['answer']
                )
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

            friend_ship_owner_test_result_answers = FriendShipTestResult.objects.filter(
                friend_ship_test=friend_ship_test_instance,
                created_by=friend_ship_test_instance.created_by
            ).first()
            self.compare_test_results(
                friend_ship_owner_test_result_answers.answers.all(),
                friend_ship_test_result_instance.answers.all(),
                friend_ship_test_instance.created_by
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
