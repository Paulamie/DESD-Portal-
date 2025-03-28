from rest_framework import serializers
from .models import Community, Event, UpdateRequest
from .models import Post

class CommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class UpdateRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UpdateRequest
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'


