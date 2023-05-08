from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import *
from .use_cases import *
from django.contrib.auth.models import *
from rest_framework.decorators import api_view,permission_classes
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend


class MultiSerializerViewSet(viewsets.ModelViewSet):
    serializers = { 
        'default': None,
    }

    def get_serializer_class(self):
            return self.serializers.get(self.action,
                        self.serializers.get('default'))


@api_view(["POST"])
@csrf_exempt
@permission_classes([AllowAny])
def SignIn(request):
    return generate_token(request.data["username"],request.data["password"])

@api_view(["POST"])
@csrf_exempt
@permission_classes([AllowAny])
def SignUp(request):
    return create_user(request.data["username"],request.data["email"],request.data["password"])

@api_view(["POST"])
@csrf_exempt
@permission_classes([IsAuthenticated])
def ChangePassword(request):
    return change_password(request.user,request.data["password"])


class AmbitoViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Ambito.objects.all()
    serializers = {
        'default': AmbitoSerializer,
        'create':CreateAmbitoSerializer
    }