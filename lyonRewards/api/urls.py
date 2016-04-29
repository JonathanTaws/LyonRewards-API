from django.conf.urls import url, include
from api import views
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as view_authtoken

# Create a router and register our viewsets with it.
import api
from api.customs import CustomObtainAuthToken

router = DefaultRouter()
router.register(r'tags', views.TagViewSet)
router.register(r'events', views.EventViewSet)
router.register(r'users', views.ProfileViewSet)
router.register(r'partners', views.PartnerViewSet)
router.register(r'offers', views.PartnerOfferViewSet)
router.register(r'acts', views.CitizenActViewSet)

# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^users/(?P<userId>[0-9]+)/offers/(?P<offerId>[0-9]+)/debit', api.views.debit),
    url(r'^users/(?P<userId>[0-9]+)/acts/(?P<actId>[0-9]+)/credit', api.views.credit),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^login/', CustomObtainAuthToken.as_view()),
    url(r'^docs/', include('rest_framework_swagger.urls')),
]

