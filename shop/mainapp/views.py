from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from rest_framework import generics
from .serializers import *
from .renders import *


class CouriersCreateView(generics.CreateAPIView):
    serializer_class = CouriersCreateSerializer
    # renderer_classes = (UserRenderer,)


class CouriersListView(generics.ListAPIView):
    serializer_class = CouriersListSerializer
    queryset = Courier.objects.all()
