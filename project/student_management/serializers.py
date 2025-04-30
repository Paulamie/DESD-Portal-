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



from .models import Post

class PostSerializer(serializers.ModelSerializer):
    user_full_name = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['post_id', 'content', 'timestamp', 'user_full_name', 'visibility']

    def get_user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    

from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'comment_text', 'created_at']



