from datetime import datetime, timedelta
from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import WorldBorder, Location, Mission,Picture,Delegations
from .serializer import *
from rest_framework import status,viewsets
from rest_framework import generics
from strawberry.django.views import GraphQLView
from .schema_strawberry import Query
from rest_framework.decorators import action
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.serializers.geojson import Serializer as GeoJSONSerializer
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.db.models import Sum
from django.utils import timezone
from django.contrib.gis.db.models.functions import Distance
from django.db.models.functions import TruncMonth
from django.db.models import Count




class MissionViewSet(viewsets.ModelViewSet):
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer
    def create(self, request, *args, **kwargs):
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response({"id": serializer.data['id']}, status=status.HTTP_201_CREATED, headers=headers)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

graphql_view = GraphQLView(schema=Query)


class LocationList(generics.ListAPIView):
    serializer_class = LocationSerializer

    def get_queryset(self):
        queryset = Location.objects.all()

        mission_name = self.request.query_params.get('Mission', None)
        started_timestamp = self.request.query_params.get('From', None)
        end_timestamp = self.request.query_params.get('To', None)
        drone = self.request.query_params.get('Drone', None)
        for time in [started_timestamp, end_timestamp]:
            if time:
                # Correct the format specifier to include a space before %z
                time = time.replace("T", "-")
                time = datetime(int(time.split("-")[0]), int(time.split("-")[1]), int(time.split("-")[2]))
                

        if mission_name:
            queryset = queryset.filter(mission__name=mission_name)

        if started_timestamp:
            # Filter locations with timestamps greater than the specified value
            queryset = queryset.filter(timestamp__gt=started_timestamp)

        if end_timestamp:
            # Filter locations with timestamps lower than the specified value
            queryset = queryset.filter(timestamp__lt=end_timestamp)

        if started_timestamp and end_timestamp:
            # Filter locations with timestamps between the specified values
            queryset = queryset.filter(timestamp__range=[started_timestamp, end_timestamp])

        if drone:
            queryset = queryset.filter(mission__drone=drone)

        return queryset

class PicturesList(generics.ListAPIView):
    serializer_class = PictureSerializer

    def get_queryset(self):
        queryset = Picture.objects.all().order_by('timestamp')

        mission_name = self.request.query_params.get('Mission', None)
        started_timestamp = self.request.query_params.get('From', None)
        end_timestamp = self.request.query_params.get('To', None)
        drone = self.request.query_params.get('Drone', None)
        for time in [started_timestamp, end_timestamp]:
            if time:
                # Correct the format specifier to include a space before %z
                time = time.replace("T", "-")
                time = datetime(int(time.split("-")[0]), int(time.split("-")[1]), int(time.split("-")[2]))
                

        if mission_name:
            queryset = queryset.filter(mission__name=mission_name)

        if started_timestamp:
            # Filter Picturess with timestamps greater than the specified value
            queryset = queryset.filter(timestamp__gt=started_timestamp)

        if end_timestamp:
            # Filter Picturess with timestamps lower than the specified value
            queryset = queryset.filter(timestamp__lt=end_timestamp)

        if started_timestamp and end_timestamp:
            # Filter Picturess with timestamps between the specified values
            queryset = queryset.filter(timestamp__range=[started_timestamp, end_timestamp])

        if drone:
            queryset = queryset.filter(mission__drone=drone)

        return queryset.order_by('timestamp')

class ModelFieldsView(APIView):
    models = {
        'WorldBorder': ['region', 'name'],
        'Location': ['timestamp', 'mission'],
        'Mission': '__all__',  # To include all fields for Mission
    }

    def get(self, request, *args, **kwargs):
        data = {}
        for model_name, fields_list in self.models.items():
            model = globals()[model_name]
            fields = {}
            for field in model._meta.get_fields():
                field_name = field.name
                if fields_list == '__all__' or field_name in fields_list:
                    fields[field_name] = field.get_internal_type()
            data[model_name] = fields

        return Response(data)

class MissionData(APIView):
    def get(self, request, *args, **kwargs):
        missions = Mission.objects.all()
        mission_serializer = MissionSerializer(missions, many=True)

        pictures = Picture.objects.all()
        picture_serializer = PictureSerializer(pictures, many=True)

        locations = Location.objects.all()
        location_serializer = LocationSerializer(locations, many=True)

        data = {
            'missions': mission_serializer.data,
            'pictures': picture_serializer.data,
            'locations': location_serializer.data,
        }

        return Response(data, status=status.HTTP_200_OK)
    
class MissionDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Mission.objects.all()
    serializer_class = MissionDetailSerializer
    
    
def calculate_intensity(delegation, mission):
    # Calculate intensity based on the number of associated location and picture points for a specific mission
    location_count = Location.objects.filter(geometry__within=delegation.geometry, mission=mission).count()
    picture_count = Picture.objects.filter(geometry__within=delegation.geometry, mission=mission).count()
    intensity = location_count + picture_count
    return intensity


class DelegationsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Delegations.objects.all()
    serializer_class = DelegationsSerializer

    @action(detail=False, methods=['get'])
    def with_intensity(self, request, *args, **kwargs):
        mission_id = request.query_params.get('mission_id')

        # Remove leading and trailing slashes from mission_id
        if mission_id:
            mission_id = mission_id.strip('/')

            if not mission_id:
                return Response({"error": "Invalid mission_id parameter"}, status=400)
        else:
            return Response({"error": "Missing mission_id parameter"}, status=400)

        try:
            mission = Mission.objects.get(id=mission_id)
        except Mission.DoesNotExist:
            return Response({"error": "Mission not found"}, status=404)

        delegations = Delegations.objects.all()

        geojson_features = []
        for delegation in delegations:
            intensity = calculate_intensity(delegation, mission)

            # Use GeoJSONSerializer to serialize the geometry
            geojson_serializer = GeoJSONSerializer()
            geojson = geojson_serializer.serialize([delegation], use_natural_primary_keys=True)

            # Parse the GeoJSON string into a Python object
            geojson_data = json.loads(geojson)

            # Check if the 'features' key is present
            features = geojson_data.get('features', [])

            if features:
                # Use the first feature's geometry
                geometry = features[0]['geometry']
            else:
                # Use the geometry directly (for cases where 'features' key is not present)
                geometry = geojson_data.get('geometry', {})

            feature = {
                "type": "Feature",
                "geometry": geometry,
                "properties": {
                    "id_del": delegation.id_del,
                    "del_fr": delegation.del_fr,
                    "del_ar": delegation.del_ar,
                    "gouv_id": delegation.gouv_id,
                    "gouv_fr": delegation.gouv_fr,
                    "gouv_ar": delegation.gouv_ar,
                    "intensity": intensity,
                }
            }
            geojson_features.append(feature)

        geojson_data = {
            "type": "FeatureCollection",
            "features": geojson_features
        }

        # Convert GeoJSON to JSON using DjangoJSONEncoder
        response_data = json.loads(json.dumps(geojson_data, cls=DjangoJSONEncoder))

        return Response(response_data)
    
class PicturesByMonthView(APIView):
    def get(self, request, *args, **kwargs):
        # Query to get the total number of pictures for each month
        picture_counts = Picture.objects.annotate(month=TruncMonth('timestamp')).values('month').annotate(total=Count('id'))

        # Serialize the data
        serializer = PictureCountSerializer(picture_counts, many=True)

        return Response(serializer.data)

class TotalDistanceView(APIView):
    def get(self, request, *args, **kwargs):
        
        # Get the current month and year
        current_month = timezone.now().month
        current_year = timezone.now().year

        # Filter locations for the current month
        locations = Location.objects.filter(timestamp__month=current_month, timestamp__year=current_year)
        for location in locations:
            try:
                geometry = GEOSGeometry(location.geometry)
            except ValueError as e:
                print(f"Invalid geometry for location {location.id}: {e}")
        # Calculate total distance using GeoDjango functions
        total_distance = locations.aggregate(total_distance=Sum(Distance('geometry', 'geometry')))['total_distance']

        # You can also calculate distance using other methods based on your requirements

        return Response({'total_distance': total_distance})
    
class ImageView(APIView):
        def get(self, request, pk):
            image_model = Picture.objects.get(pk=pk)
            image_path = image_model.path_img
            return FileResponse(open(image_path, 'rb'))
        
class DashboardAPIView(APIView):
    def get(self, request):
        # Get the newest 10 missions
        newest_missions = Mission.objects.order_by('-started')[:10]

        # Get total number of missions
        total_missions = Mission.objects.count()

        # Get total number of pictures
        total_pictures = Picture.objects.count()

        # You can customize the data structure based on your requirements
        data = {
            'newest_missions': [
                {
                    'id': mission.id,
                    'name': mission.name,
                    'started': mission.started,
                    'live': mission.published,
                    'drone': mission.drone,
                    # Add other fields as needed
                }
                for mission in newest_missions
            ],
            'total_missions': total_missions,
            'total_pictures': total_pictures,
        }

        return Response(data, status=status.HTTP_200_OK)