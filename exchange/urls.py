from django.urls import path
from .views      import ReportVIew, TradeView, ExchangeView

urlpatterns = [
    path('/report/<int:item_id>/<str:unit>', ReportVIew.as_view()),
    path('/trade/<str:option>', TradeView.as_view()),
    path('/<int:item_id>', ExchangeView.as_view())
]

