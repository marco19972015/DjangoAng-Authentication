from django.shortcuts import render

# To handle exception from the REST framework
from rest_framework import exceptions

# APIView to return the request as a view
from rest_framework.views import APIView

# Find out what the code below is doing
from rest_framework.response import Response

from .serializers import UserSerializer

# Import to access the contents in models
from .models import User

# Create your views here.
# Create view using the API view (extends from API view)
# This is the base class when we create an end point
# To add to our route we add it to urls.py
class RegisterAPIView(APIView):
    def post(self, request):

        # Returning the content of the request body for validation (specifically the password)
        data = request.data

        # Validation on data for password
        if data['password'] != data['password_confirm']:
            # The other validations should be handles by the User Serializer
            raise exceptions.APIException('Passwords do not match!')
        
        # data = data is required because None may be a valid input or output value
        serializer = UserSerializer(data=data)
        # If one of our fields is not appearing, then we raise an exception
        serializer.is_valid(raise_exception=True)
        # We save it (essentially creating our user from this)
        serializer.save()
        # Here we return it in a JSON format
        return Response(serializer.data)

        # After this we can test in Postman (this is all posible after the pathing is completed
        # (urls.py in app -> urls.py in core -> views.py ))
        # return Response(request.data)

class LoginAPIView(APIView):
    def post(self, request):
        # .data reminds of the object we pass from our template to our component when trying to access different objects in the DOM
        email = request.data['email']
        password = request.data['password']

        # Filter where email is equal to email, and get the first value since our code doesn't know that the email is unique
        user = User.objects.filter(email=email).first()

        # IMPORTANT to raise both exceptions because the user doesn't know if he put the wrong email or the wrong password

        # If we did not find the user 
        if user is None:
            # raise AuthFailed exception and let the user know (email)
            raise exceptions.AuthenticationFailed('Invalid Email')

        # ISSUE BELOW, (WHEN I CHECK TO GET THE BOOLEAN IT IS NOT CORRECT)
        # If the email is correct, now we check the password (We use a built in function check_password)
        if not user.check_password(password):
            raise exceptions.AuthenticationFailed(f"password: {password}")
        
        if password != user.password:
            raise exceptions.AuthenticationFailed("Invalid Password")
        
        # We serialize the User (create)
        serializer = UserSerializer(user)

        # We return the data so we can see it
        return Response(serializer.data)
 

    