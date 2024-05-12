# serializers.py
from rest_framework import serializers
from money_collections.models import ReportImage, ReportVideo, Report

class ReportImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportImage
        fields = ('id', 'file')

class ReportVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportVideo
        fields = ('id', 'file')

class ReportSerializer(serializers.ModelSerializer):
    images = ReportImageSerializer(many=True, required=False)
    videos = ReportVideoSerializer(many=True, required=False)

    class Meta:
        model = Report
        fields = ('name', 'description', 'price', 'images', 'videos')

    def create(self, validated_data):
        images_data = self.context.get('request').FILES.getlist('images', [])
        videos_data = self.context.get('request').FILES.getlist('videos', [])
        
        validated_data.pop('images', None)
        validated_data.pop('videos', None)
        
        report = Report.objects.create(**validated_data)

        for image_data in images_data:
            image = ReportImage.objects.create(file=image_data)
            report.images.add(image)

        for video_data in videos_data:
            video = ReportVideo.objects.create(file=video_data)
            report.videos.add(video)

        return report

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.price = validated_data.get('price', instance.price)
        instance.save()

        images_data = self.context.get('request').FILES.getlist('images', [])
        videos_data = self.context.get('request').FILES.getlist('videos', [])
        
        # Remove images and videos from validated_data as they are not fields in the report model
        validated_data.pop('images', None)
        validated_data.pop('videos', None)

        # Delete existing images and videos
        instance.images.all().delete()
        instance.videos.all().delete()

        for image_data in images_data:
            image = ReportImage.objects.create(file=image_data)
            instance.images.add(image)

        for video_data in videos_data:
            video = ReportVideo.objects.create(file=video_data)
            instance.videos.add(video)

        return instance