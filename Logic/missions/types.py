import strawberry_django
from strawberry import auto

from .models import Picture,Mission

@strawberry_django.type(Picture)
class Picture:
    id: auto
    timestamp: auto

@strawberry_django.type(Mission,fields="__all__")
class Mission:
    pass
    
    
    
