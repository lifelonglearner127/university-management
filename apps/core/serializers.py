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


class TMSChoiceField(serializers.Field):

    def __init__(self, choices, **kwargs):
        self.choices = dict((x, y) for x, y in choices)
        super().__init__(**kwargs)

    def to_representation(self, value):
        try:
            text = self.choices[value]
        except KeyError:
            text = 'Unknown'
        ret = {
            'value': value,
            'text': text
        }
        return ret

    def to_internal_value(self, data):
        return data['value']
