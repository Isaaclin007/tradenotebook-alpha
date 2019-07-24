from rest_framework import serializers, views
from rest_framework.response import Response

from .pyziabm_run import main

# Create your views here.

# class InputSerializer(serializers.Serializer):
#     model_input = serializers.CharField()
# current implementation does not require input 

class PyView(views.APIView):
    
    def get(self, request):
        # serializer = InputSerializer()
        df = main()
        return Response({'message':'success', 'data': df})
