from django.http import StreamingHttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from restapi import serializers
from restapi.camera import Camera
from restapi.controller import Controller
from django.contrib.staticfiles.views import serve
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    return serve(request, 'index.html')


class RestApiViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['get'])
    def status(self, request):
        return Response({
            'status': 'OK',
            'robot': Controller.serialize()
        })

    @action(detail=False, methods=['post'])
    def move(self, request):
        serializer = serializers.MoveCommandSerializer(data=request.data)
        if serializer.is_valid():
            Controller.move(serializer.data['left_orientation'],
                            serializer.data['left_speed'],
                            serializer.data['right_orientation'],
                            serializer.data['right_speed'],
                            serializer.data['duration'],
                            serializer.data['distance'])
            return Response({
                'status': 'OK',
                'robot': Controller.serialize()
                })
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def move_to_target(self, request):
        serializer = serializers.MoveToTargetCommandSerializer(data=request.data)
        if serializer.is_valid():
            Controller.move_to_target(serializer.data['x'],
                                      serializer.data['y'],
                                      serializer.data['speed'],
                                      serializer.data['timeout'])
            return Response({
                'status': 'OK',
                'robot': Controller.serialize()
                })
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def stop(self, request):
        Controller.stop()
        return Response({
            'status': 'OK',
            'robot': Controller.serialize()
            })

    @action(detail=False, methods=['post'])
    def set_light(self, request):
        serializer = serializers.LightCommandSerializer(data=request.data)
        if serializer.is_valid():
            Controller.set_light(serializer.data['left_on'],
                                 serializer.data['right_on'],
                                 serializer.data['arm_on'])
            return Response({
                'status': 'OK',
                'robot': Controller.serialize()
                })
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def blink_light(self, request):
        serializer = serializers.LightCommandSerializer(data=request.data)
        if serializer.is_valid():
            Controller.blink_light(serializer.data['left_on'],
                                   serializer.data['right_on'])
            return Response({
                'status': 'OK',
                'robot': Controller.serialize()
                })
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def select_target(self, request):
        serializer = serializers.SelectTargetSerializer(data=request.data)
        if serializer.is_valid():
            Controller.select_target(serializer.data['x'],
                                     serializer.data['y'])
            return Response({
                'status': 'OK',
                'robot': Controller.serialize()
                })
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def capture_image(self, request):
        serializer = serializers.CapturePictureSerializer(data=request.data)
        if serializer.is_valid():
            Controller.capture_image(serializer.data['destination'])
            return Response({
                'status': 'OK',
                'robot': Controller.serialize()
                })
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def set_lcd_brightness(self, request):
        serializer = serializers.SetLcdBrightnessSerializer(data=request.data)
        if serializer.is_valid():
            Controller.set_lcd_brightness(serializer.data['brightness'])
            return Response({
                'status': 'OK',
                'robot': Controller.serialize()
                })
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def reset_lcd(self, request):
        Controller.reset_lcd()
        return Response({
            'status': 'OK',
            'robot': Controller.serialize()
            })

    @action(detail=False, methods=['post'])
    def say(self, request):
        serializer = serializers.TextToSpeachSerializer(data=request.data)
        if serializer.is_valid():
            Controller.say(serializer.data['destination'], serializer.data['text'])
            return Response({
                'status': 'OK',
                'robot': Controller.serialize()
                })
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def mood(self, request):
        serializer = serializers.SetMoodSerializer(data=request.data)
        if serializer.is_valid():
            Controller.set_mood(serializer.data['mood'])
            return Response({
                'status': 'OK',
                'robot': Controller.serialize()
                })
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def moods(self, request):
        return Response({
            'status': 'OK',
            'moods': Controller.get_moods()
            })

    @action(detail=False, methods=['post'])
    def lcd_picture(self, request):
        serializer = serializers.SetLcdPictureSerializer(data=request.data)
        if serializer.is_valid():
            Controller.set_lcd_picture(serializer.data['name'])
            return Response({
                'status': 'OK',
                'robot': Controller.serialize()
                })
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def stream(self, request):
        return StreamingHttpResponse(Camera.stream(),
                                     content_type="multipart/x-mixed-replace;boundary=FRAME")

    @action(detail=False, methods=['post'])
    def stream_setup(self, request):
        serializer = serializers.VideoStreamSetupSerializer(data=request.data)
        if serializer.is_valid():
            Camera.stream_setup(serializer.data['selected_camera'],
                                                   serializer.data['overlay'])
            return Response({
                'status': 'OK',
                'robot': Controller.serialize()
                })
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    # Arm
    @action(detail=False, methods=['post'])
    def move_arm(self, request):
        serializer = serializers.MoveArmCommandSerializer(data=request.data)
        if serializer.is_valid():
            success, message = Controller.move_arm(serializer.data['id'],
                                                   serializer.data['angle'],
                                                   serializer.data['lock_wrist'])
            if success:
                return Response({
                    'status': 'OK',
                    'robot': Controller.serialize()
                    })
            else:
                return Response({
                    'status': 'KO',
                    'message': message
                })
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def move_arm_to_position(self, request):
        serializer = serializers.MoveArmToPositionCommandSerializer(data=request.data)
        if serializer.is_valid():
            success, message = Controller.move_arm_to_position(serializer.data['position_id'],
                                                               serializer.data['lock_wrist'])
            if success:
                return Response({
                    'status': 'OK',
                    'robot': Controller.serialize()
                    })
            else:
                return Response({
                    'status': 'KO',
                    'message': message
                })
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

