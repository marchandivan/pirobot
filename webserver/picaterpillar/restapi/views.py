from rest_framework import viewsets, status
from rest_framework.decorators import action

from restapi.controller import Controller
from restapi.serializers import MoveCommandSerializer
from rest_framework.response import Response


class RestApiViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['get'])
    def status(self, request):
        return Response({
            'status': 'OK',
            'robot': Controller.serialize()
        })

    @action(detail=False, methods=['post'])
    def move(self, request):
        serializer = MoveCommandSerializer(data=request.data)
        if serializer.is_valid():
            Controller.move(serializer.data['left_orientation'],
                            serializer.data['left_speed'],
                            serializer.data['right_orientation'],
                            serializer.data['right_speed'],
                            serializer.data['duration'])
            return Response({
                'status': 'OK',
                'robot': Controller.serialize()
                })
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
