from django.shortcuts import render
from rest_framework.views import APIView

# Find out what the code below is doing
from rest_framework.response import Response

# Create your views here.
# Create view using the API view (extends from API view)
# This is the base class when we create an end point
# To add to our route we add it to urls.py
class RegisterAPIView(APIView):
    def post(self, request):
        # After this we can test in Postman (this is all posible after the pathing is completed
        # (urls.py in app -> urls.py in core -> views.py ))
        return Response(request.data)