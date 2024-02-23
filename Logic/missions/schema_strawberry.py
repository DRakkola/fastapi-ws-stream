import strawberry
from strawberry_django.optimizer import DjangoOptimizerExtension
from .types import *

@strawberry.type
class Query:

    missions: list[Mission] = strawberry.django.field()


schema = strawberry.Schema(
    query=Query,
    extensions=[
        DjangoOptimizerExtension,  # not required, but highly recommended
    ],
)