from rest_framework import serializers
from eye_generator import EyeGenerator
from restapi.arm import Arm

class MoveCommandSerializer(serializers.Serializer):
    left_orientation = serializers.ChoiceField(choices=['F', 'B'])
    left_speed = serializers.FloatField(min_value=0.0, max_value=100.0, default=0.0)
    right_orientation = serializers.ChoiceField(choices=['F', 'B'])
    right_speed = serializers.FloatField(min_value=0.0, max_value=100.0, default=0.0)
    duration = serializers.FloatField(min_value=0.0, default=1.0)
    distance = serializers.FloatField(min_value=0.0, default=None)


class MoveToTargetCommandSerializer(serializers.Serializer):
    x = serializers.FloatField()
    y = serializers.FloatField()
    speed = serializers.FloatField(min_value=0.0, max_value=100.0, default=0.0)
    timeout = serializers.FloatField(min_value=0.0, default=10.0)


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


class SetMoodSerializer(serializers.Serializer):
    mood = serializers.ChoiceField(choices=EyeGenerator.get_moods(), default='relaxed')


class SetLcdPictureSerializer(serializers.Serializer):
    name = serializers.CharField()


class MoveArmCommandSerializer(serializers.Serializer):
    id = serializers.ChoiceField(choices=Arm.get_ids())
    angle = serializers.IntegerField()


class MoveArmToPositionCommandSerializer(serializers.Serializer):
    position_id = serializers.ChoiceField(choices=Arm.get_position_ids())
