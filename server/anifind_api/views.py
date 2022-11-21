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

    # 1. List all
    def get_user(self, request, *args, **kwargs):
        '''
        List all the info for given requested user
        '''
        users = User.objects.filter(user_id = request.data.get('user_id'))
        serializer = UserSerializer(users, many=True)
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
    # 2. Create
    # def post(self, request, *args, **kwargs):
    #     '''
    #     Create the user with given data
    #     '''
    #     data = {
    #         'UserID': request.data.get('UserID'), 
    #         'Name': request.data.get('Name'), 
    #     }
    #     serializer = UserSerializer(data=data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)

    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)