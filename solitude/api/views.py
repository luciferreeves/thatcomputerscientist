from django.contrib.auth.models import User
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import authentication_classes, permission_classes

from solitude.api.serializers import UserSerializer


# Create your views here.

class CurrentUser(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, format=None):
        current_user = request.user
        serializer = UserSerializer(current_user)
        return Response(serializer.data)
    

# @APIView(['GET'])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
# def current_user(request, format=None):
#     current_user = request.user
#     serializer = UserSerializer(current_user)
#     return Response(serializer.data)