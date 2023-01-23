from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import (SigninView,UserView,CardApiView,CardDetailAPIView)

urlpatterns = [
    path('<int:m_id>/me/', UserView.as_view(), name='user-list-view'),
    path('<int:m_id>/me/<int:id>/', UserView.as_view(), name='user-detail-view'),
    path('<int:m_id>/card/', CardApiView.as_view(), name='card-list-view'),
    path('<int:m_id>/card/<int:id>/', CardDetailAPIView.as_view(), name='card-detail-view'),
    path('signin/', SigninView.as_view(), name='signin'),
]