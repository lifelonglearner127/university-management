from rest_framework import serializers


class CreatedTimeModel(serializers.Serializer):

    created = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )


class TimeStampedSerializer(serializers.Serializer):

    created = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )
    updated = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )