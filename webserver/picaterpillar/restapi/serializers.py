from rest_framework import serializers


class MoveCommandSerializer(serializers.Serializer):
    left_orientation = serializers.ChoiceField(choices=['F', 'B'])
    left_speed = serializers.FloatField(min_value=0.0, max_value=100.0, default=0.0)
    right_orientation = serializers.ChoiceField(choices=['F', 'B'])
    right_speed = serializers.FloatField(min_value=0.0, max_value=100.0, default=0.0)
    duration = serializers.FloatField(min_value=0.0, default=1.0)


class LightCommandSerializer(serializers.Serializer):
    left_on = serializers.BooleanField(default=False)
    right_on = serializers.BooleanField(default=False)


class SelectTargetSerializer(serializers.Serializer):
    x = serializers.FloatField(min_value=0.0, max_value=100.0, default=0.0)
    y = serializers.FloatField(min_value=0.0, max_value=100.0, default=0.0)


class CapturePictureSerializer(serializers.Serializer):
    destination = serializers.ChoiceField(choices=['lcd'], default='lcd')


class SetLcdBrightnessSerializer(serializers.Serializer):
    brightness = serializers.FloatField(min_value=0.0, max_value=100.0, default=0.0)


class TextToSpeachSerializer(serializers.Serializer):
    destination = serializers.ChoiceField(choices=['lcd'], default='lcd')
    text = serializers.CharField()
