import graphene
from graphene_django.types import DjangoObjectType
import graphql_geojson
from .models import WorldBorder,Location,Picture,Mission

class WorldBorderType(graphql_geojson.GeoJSONType, DjangoObjectType):
    class Meta:
        model = WorldBorder
        geojson_field = 'mpoly'

class MissionType(graphql_geojson.GeoJSONType, DjangoObjectType):
    class Meta:
        model = Mission
        geojson_field = 'area'
        
        

class LocationType(graphql_geojson.GeoJSONType, DjangoObjectType):
    class Meta:
        model = Location
        geojson_field = 'geometry'

class PictureType(graphql_geojson.GeoJSONType, DjangoObjectType):
    class Meta:
        model = Picture
        geojson_field = 'geometry'
        

class Query(graphene.ObjectType):
    world_borders = graphene.List(
        WorldBorderType,
        region=graphene.Int(),
        subregion=graphene.Int(),
        name=graphene.String(),
    )
    
    locations = graphene.List(
        LocationType, 
        timestamp=graphene.DateTime(),
        lon=graphene.Float(),
        lat=graphene.Float(),
        mission=graphene.String(),
    )
    
    pictures = graphene.List(
        PictureType, 
        timestamp=graphene.DateTime(),
        lon=graphene.Float(),
        lat=graphene.Float(),
        mission=graphene.String(),
    )
    all_missions = graphene.List(MissionType)
    def resolve_all_missions(self, info, **kwargs):
        return Mission.objects.all()
    
    def resolve_locations(self, info, mission=None, lat=None, lon=None,timestamp=None, **kwargs):
        # Create a filter dictionary based on the provided arguments
        filters = {}
        if mission is not None:
            filters['mission__name__icontains'] = mission
        if lat is not None:
            filters['lat'] = lat
        if lon is not None:
            filters['lon'] = lon
        if timestamp is not None:
            filters['timestamp'] = timestamp

        # Apply filters to the queryset
        return Location.objects.filter(**filters)
    
    def resolve_pictures(self, info, mission=None, lat=None, lon=None,timestamp=None, **kwargs):
        # Create a filter dictionary based on the provided arguments
        filters = {}
        if mission is not None:
            filters['mission__name__icontains'] = mission
        if lat is not None:
            filters['lat'] = lat
        if lon is not None:
            filters['lon'] = lon
        if timestamp is not None:
            filters['timestamp'] = timestamp

        # Apply filters to the queryset
        return Picture.objects.filter(**filters)
    
    
    def resolve_world_borders(self, info, region=None, subregion=None, name=None, **kwargs):
        # Create a filter dictionary based on the provided arguments
        filters = {}
        if region is not None:
            filters['region'] = region
        if subregion is not None:
            filters['subregion'] = subregion
        if name is not None:
            filters['name__icontains'] = name

        # Apply filters to the queryset
        return WorldBorder.objects.filter(**filters)

schema = graphene.Schema(query=Query)
