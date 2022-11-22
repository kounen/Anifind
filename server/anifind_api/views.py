from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer
from .models import User
from .serializers import UserSerializer

class UserListApiView(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]

    # 1. List all info from username
    def get(self, request, *args, **kwargs):
        '''
        List all the info for given requested user
        '''
        users = User.objects.filter(username = request.data.get('username'))
        serializer = UserSerializer(users, many=True)
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)

    # 2. Create user
    def post(self, request, *args, **kwargs):
        '''
        Create the user with given data
        '''
        data = {
            'username': request.data.get('username'), 
            'password': request.data.get('password')
        }
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)