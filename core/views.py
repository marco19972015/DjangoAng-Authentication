from django.shortcuts import render

# To handle exception from the REST framework
from rest_framework import exceptions

# APIView to return the request as a view
from rest_framework.views import APIView

# Response object that takes unrendered content and uses content negotiation to determine the correct content type 
# to return to the client
from rest_framework.response import Response


from core.authentication import JWTAuthentication, create_access_token, create_refresh_token, decode_refresh_token

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
        # if not user.check_password(password):
        #     raise exceptions.AuthenticationFailed(f"password: {password}")
        
        if password != user.password:
            raise exceptions.AuthenticationFailed("Invalid Password")
        
        # Once we get email and password we create an access token and refresh token
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        # Returns will be different (create a variable)
        response = Response()

        # access token will appear in the body | refresh token will appear in cookies
        # httponly=True is important since it allows our frontend to access the cookie, not just the back end
        response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)
        response.data = {
            'token': access_token
        }
    
        # # We serialize the User (create)
        # serializer = UserSerializer(user)

        # # We return the data so we can see it
        # return Response(serializer.data)
        return response


# Create the UserAPIView and have the APIView extend from it
class UserAPIView(APIView):
    # This acts as a middleware by getting the headers and getting the user
    # we will in authentication.py ->
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
       
# Endpoint to refresh Bearer token if it's expired
class RefreshAPIView(APIView):
    def post(self, request):
        # Get the refresh token from the cookies
        refresh_token = request.COOKIES.get('refresh_token')

        # Get the user id from decode_refresh_token
        id = decode_refresh_token(refresh_token)

        # Once we get id, get the access token
        access_token = create_access_token(id)

        # The Response will return token, and the new access token
        return Response({
            'token': access_token
        })

# log out endpoint
class LogoutAPIView(APIView):
    def post(self, request):
        # To remove cookie we get the response
        response = Response()
        # delete the cookie with the key refresh_token
        response.delete_cookie(key='refresh_token')
        # the response lets the user know if it was successful
        response.data = {
            'message': 'success'
        }

        # return the message in response
        return response