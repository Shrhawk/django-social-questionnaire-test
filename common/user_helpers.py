from django.contrib.auth.models import User


def create_user(user_name):
    """
    create django auth user
    :param user_name:
    :return:
    """
    user = User.objects.filter(username=user_name).first()
    if not user:
        user = User.objects.create_user(username=user_name)
    return user
