from django.shortcuts import render

# To handle exception from the REST framework
from rest_framework import exceptions

# APIView to return the request as a view
from rest_framework.views import APIView

# Response object that takes unrendered content and uses content negotiation to determine the correct content type 
# to return to the client
from rest_framework.response import Response


from rest_framework.authentication import get_authorization_header

from core.authentication import create_access_token, decode_access_token

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
        refresh_token = create_access_token(user.id)

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
    # Create the get request method
    def get(self, request):
        # Below we want to send the access token view the headers
        # pass
        # To get the access token we assign get_authorization_header to auth variable
        auth = get_authorization_header(request).split()

        # Add an if condition where if auth is sent and the len is 2 then do the following
        if auth and len(auth) == 2:
            # Then we want to get the decoded token
            token = auth[1].decode('utf-8')
            
            # pass the unicode token to the decode function
            id = decode_access_token(token)

            user = User.objects.get(pk=id)
        
            if user:
                serializer = UserSerializer(user)
                return Response(serializer.data)
            
        raise exceptions.AuthenticationFailed('unauthenticated') 
      
    