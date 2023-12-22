# JWT is the industry standard method for representing claims securely between two parties
# a compact and self-contained way for securely transmitting information between parties as a JSON object
import jwt, datetime


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

def create_refresh_token(id):
    return jwt.encode({
        'user_id': id,
        # Access token will leave after 7 days
        'exp':  datetime.datetime.utcnow() + datetime.timedelta(days=30),
        # Creation time
        'iat': datetime.datetime.utcnow()
    }, 'refresh_secret', algorithm='HS256')


