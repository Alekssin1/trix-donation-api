# serializers.py
from rest_framework import serializers
from organizations.models import Post, PostImage, PostVideo

class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ('id', 'file')

class PostVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostVideo
        fields = ('id', 'file')

class PostSerializer(serializers.ModelSerializer):
    images = PostImageSerializer(many=True, required=False)
    videos = PostVideoSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = ('name', 'description', 'images', 'videos')

    def create(self, validated_data):
        images_data = self.context.get('request').FILES.getlist('images', [])
        videos_data = self.context.get('request').FILES.getlist('videos', [])
        
        validated_data.pop('images', None)
        validated_data.pop('videos', None)
        
        post = Post.objects.create(**validated_data)

        for image_data in images_data:
            image = PostImage.objects.create(file=image_data)
            post.images.add(image)

        for video_data in videos_data:
            video = PostVideo.objects.create(file=video_data)
            post.videos.add(video)

        return post

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        images_data = self.context.get('request').FILES.getlist('images', [])
        videos_data = self.context.get('request').FILES.getlist('videos', [])
        
        # Remove images and videos from validated_data as they are not fields in the Post model
        validated_data.pop('images', None)
        validated_data.pop('videos', None)

        # Delete existing images and videos
        instance.images.all().delete()
        instance.videos.all().delete()

        for image_data in images_data:
            image = PostImage.objects.create(file=image_data)
            instance.images.add(image)

        for video_data in videos_data:
            PostVideo.objects.create(file=video_data)

        return instance