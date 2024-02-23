"""
URL configuration for geoApi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from graphene_django.views import GraphQLView
from missions.schema import schema
from missions.schema_strawberry import schema as strawberry_schema
from django.views.decorators.csrf import csrf_exempt
from missions.views import *
from rest_framework import routers
from strawberry.django.views import GraphQLView as AsyncGraphQLView
from fileUpload import urls
router = routers.DefaultRouter()
router.register('delegations', DelegationsViewSet, basename='delegations')
router.register(r'new-mission', MissionViewSet)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql/',csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema))),
    path('model-fields/', ModelFieldsView.as_view(), name='model-fields'),
    path('mission-heatmap/', MissionDetailAPIView.as_view(), name='mission-heatmap'),
    path('api/', include(router.urls)),
    path('mission-data/', MissionData.as_view(), name='mission-data'),
    path('strawberry', AsyncGraphQLView.as_view(schema=strawberry_schema)),
    path('monthly-distance/', TotalDistanceView.as_view(), name='monthly-distance'),
    path('monthly-count/', PicturesByMonthView.as_view(), name='monthly-count'),
    path('dashboard/', DashboardAPIView.as_view(), name='dashboard'),
    path('locations/', LocationList.as_view(), name='location-list'),
    path('pictures/', PicturesList.as_view(), name='picture-list'),
    path('get-image/<str:pk>',ImageView.as_view(),name='get-image'),
    path('',include(urls))
    

]
