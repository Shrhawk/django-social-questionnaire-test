from django import forms


class FriendShipAttemptTestForm(forms.Form):
    name = forms.CharField(max_length=200, required=False)
    friend_ship_test_id = forms.CharField(widget=forms.HiddenInput)
    created_by = forms.CharField(max_length=200, required=False)
    user_name = forms.CharField(max_length=200, required=True)
