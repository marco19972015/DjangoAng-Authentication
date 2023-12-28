# JWT is the industry standard method for representing claims securely between two parties
# a compact and self-contained way for securely transmitting information between parties as a JSON object
import jwt, datetime
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header

from .models import User


# Create a middleware called JWTAuthentication and have it extend from BaseAuthentication
class JWTAuthentication(BaseAuthentication):
    # Get the headers and get the user and in the end we return the user

    # We need to override the authenticate function
    def authenticate(self, request):
         # To get the access token we assign get_authorization_header to auth variable
        auth = get_authorization_header(request).split()

        # Add an if condition where if auth is sent and the len is 2 then do the following
        if auth and len(auth) == 2:
            # Then we want to get the decoded token
            token = auth[1].decode('utf-8')
            
            # pass the unicode token to the decode function
            id = decode_access_token(token)

            user = User.objects.get(pk=id)

            return (user, None)
        
        raise exceptions.AuthenticationFailed('unauthenticated') 
      
    

# The access token needs to access our end points, but it will also have to expire.
# Once token expires, we will use the refresh_token in order to generate a new access token.

# Pass in an id of a user
def create_access_token(id):
    return jwt.encode({
        'user_id': id,
        # Access token will leave after 30 sec
        'exp':  datetime.datetime.utcnow() + datetime.timedelta(seconds=30),
        # Creation time
        'iat': datetime.datetime.utcnow()
    }, 'access_secret', algorithm='HS256')


def decode_access_token(token):
    try:
        payload = jwt.decode(token, 'access_secret', algorithms='HS256')
        return payload['user_id']
    
    except Exception as e:
        print(e)
        raise exceptions.AuthenticationFailed('unauthenticated')


def create_refresh_token(id):
    return jwt.encode({
        'user_id': id,
        # Access token will leave after 7 days
        'exp':  datetime.datetime.utcnow() + datetime.timedelta(days=30),
        # Creation time
        'iat': datetime.datetime.utcnow()
    }, 'refresh_secret', algorithm='HS256')


