# To have access to ModelSerializer
from rest_framework.serializers import ModelSerializer

from rest_framework.views import Response
# To have access to our User class
from .models import User

# What are Serializers and why do we need them?
# When we create the user, we return the User data in our views.py
# But we can not return the User as an object as it is (it will throw an error (meaning we have to serialize the object))
# That object is converted to JSON (this is done through the serializers)
class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        # We can also use '__all__' however, this will return all the fields in core_users
        fields = ['id', 'first_name', 'last_name', 'email', 'password']

