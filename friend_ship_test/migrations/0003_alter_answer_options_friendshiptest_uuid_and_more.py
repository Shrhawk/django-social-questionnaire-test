# Generated by Django 4.0.3 on 2022-03-20 08:14

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('friend_ship_test', '0002_friendshiptest_friendshiptestanswers_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='answer',
            options={'ordering': ('id',)},
        ),
        migrations.AddField(
            model_name='friendshiptest',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.DeleteModel(
            name='FriendShipTestInvites',
        ),
    ]
