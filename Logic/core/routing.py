from django.urls import path, include
from dash.routing import websocket_urlpatterns as dash_websocket_urlpatterns

urlpatterns = [
    # Your existing urlpatterns here
    path("", include(dash_websocket_urlpatterns)),
]