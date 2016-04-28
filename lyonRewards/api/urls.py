from django.conf.urls import url, include
from api import views
from rest_framework.routers import DefaultRouter

# Create a router and register our viewsets with it.
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
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]