import datetime
import random
import string
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
from .models import Reset, User, UserToken

from django.core.mail import send_mail

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


# ISSUE HERE WHERE I'M COMPARING HASED VS UNHASHED PASSWORD
class LoginAPIView(APIView):
    def post(self, request):
        # .data reminds of the object we pass from our template to our component when trying to access different objects in the DOM
        email = request.data['email']
        password = request.data['password']

        # Filter where email is equal to email, and get the first value since our code doesn't know that the email is unique
        user = User.objects.filter(email=email).first()

        # If we did not find the user 
        if user is None:
            # raise AuthFailed exception and let the user know (email)
            raise exceptions.AuthenticationFailed('Invalid Email')
        
        # The password coming in is the encoded password
        # since it was not being checked againts the has properly I was getting an error
        if not user.check_password(password):
            raise exceptions.AuthenticationFailed('Invalid password')
        
        # Once we get email and password we create an access token and refresh token
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        # Assign attributesto UserToken model (When we log in, we create a user token value)
        # (We need to add it here because when we refresh the token in RefreshAPIView class we will add another validation)
        UserToken.objects.create(
            user_id = user.id,
            token = refresh_token,
            # (We don't create a create_at since it is auto added)
            expired_at = datetime.datetime.utcnow() + datetime.timedelta(days=30),
        )


        # Returns will be different (create a variable)
        response = Response()

        # access token will appear in the body | refresh token will appear in cookies
        # httponly=True is important since it allows our frontend to access the cookie, not just the back end
        response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)
        response.data = {
            'token': access_token
        }
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

        # validation, if this value does not exist in the database
        if not UserToken.objects.filter(
            user_id = id,
            token = refresh_token,
            expired_at__gt=datetime.datetime.now(tz=datetime.timezone.utc)
        ).exists():
            # return an exception
            raise exceptions.AuthenticationFailed('unauthenticated')
            

        # Once we get id, get the access token
        access_token = create_access_token(id)

        # The Response will return token, and the new access token
        return Response({
            'token': access_token
        })

# log out endpoint
class LogoutAPIView(APIView):

    def post(self, request):
        # We get the authenticated user in request.user.id, when it's found delete it
        refresh_token = request.COOKIES.get('refresh_token')
        UserToken.objects.filter(token=refresh_token).delete()

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
    
class ForgotAPIView(APIView):
    def post(self, request):
        email = request.data['email']
        # generate a random string
        token = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))

        # Access the Reset model and create a new object with the email and token
        Reset.objects.create(
            email = email,
            token = token
        )

        # For the message we need to provide the URL to send to the frontend (angular port)
        url = 'http://localhost:4200/reset/' + token

        # Function to send emails is called send_mail and needs to be imported from django.core.mail
        send_mail(
            subject = 'Reset your password!',
            # %s will be substituted with url (I can also just use f-string)
            message = 'Click <a href="%s">here</a>to reset your password' % url,
            from_email='from@example.com',
            recipient_list=[email]
        )

        return Response({
            'message': 'success'
        })
    
class ResetAPIView(APIView):
    def post(self, request):
        # Send the password confirm and token
        data = request.data

        # Validation on data for password
        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('Passwords do not match!')
        
        # if password do match, access the Reset objects and filter by token, retrieve the first value
        reset_password = Reset.objects.filter(token=data['token']).first()

        # If password variable is not found then raise an exception
        if not reset_password:
            raise exceptions.APIException('Invalid link!')
        
        # If everything checks out then find the user, 
        # where the email is equal to reset_password (contains email and token), return the first instance 
        user = User.objects.filter(email=reset_password.email).first()

        # if the user is not set, raise another exception 
        if not user: 
            raise exceptions.APIException('User not found!')
        
        # If all checks out
        user.set_password(data['password'])
        user.save()

        return Response({
            'message': 'success'
        })