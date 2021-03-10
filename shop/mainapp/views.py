from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from rest_framework import generics
from .serializers import *


class CouriersCreateView(generics.CreateAPIView):
    serializer_class = CouriersCreateSerializer

    # def perform_create(self, serializer):
    #     data = get_object_or_404(Author, id=self.request.data.get('author_id'))
    #     return serializer.save(author=author)
# class CouriersCreateView(generics.ListCreateAPIView):
#     queryset = Courier.objects.all()
#     serializer_class = CouriersDetailSerializer


class CouriersListView(generics.ListAPIView):
    serializer_class = CouriersListSerializer
    queryset = Courier.objects.all()
