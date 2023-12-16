# When we hit the api path (located in app folder under urls.py) we get taken to this urls.py unser core folder app
from django.urls import path
from .views import RegisterAPIView

urlpatterns = [
    # In here we need to add the path (register)
    # When we hist the register path we call it as a view
    path('register', RegisterAPIView.as_view()),  # FIRST PROB I didn't correctly add the pathing
]