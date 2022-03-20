from django.forms import ModelForm

from friend_ship_test.models import FriendShipTest


class FriendShipCreateTestForm(ModelForm):

    class Meta:
        model = FriendShipTest
        fields = ['name', 'user_name']
