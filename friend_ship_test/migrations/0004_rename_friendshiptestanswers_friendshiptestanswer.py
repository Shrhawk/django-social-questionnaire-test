# Generated by Django 4.0.3 on 2022-03-20 09:34

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('friend_ship_test', '0003_alter_answer_options_friendshiptest_uuid_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='FriendShipTestAnswers',
            new_name='FriendShipTestAnswer',
        ),
    ]
