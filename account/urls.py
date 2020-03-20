from django.urls import path
from .views      import SignUpView , SignInView, Activate, BalanceView

urlpatterns = [
    path('/signup', SignUpView.as_view()),
    path('/signin', SignInView.as_view()),
    path('/balance', BalanceView.as_view()),
    path('/activate/<str:uidb64>/<str:token>', Activate.as_view())
]

