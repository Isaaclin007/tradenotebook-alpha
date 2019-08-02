from rest_framework import views, viewsets
from rest_framework.response import Response

from .pyziabm_run import main

from .serializers import InputSerializer
from .models import Result

# Create your views here.

class PyView(viewsets.ModelViewSet):
    serializer_class = InputSerializer
    queryset = Result.objects.all()
    http_method_names = ['get', 'post']

    def create(self, request):
        serializer = InputSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            df = main()
            return Response({'message':'success', 'params':serializer.validated_data, 'data': df})
        return Response({'message': 'error!'})

    def list(self, request):
        return Response({'message':'please POST arbitrary data'})

    def retrieve(self, request, pk):
        return Response({'message':'please POST arbitrary data'})

class RandomView(views.APIView):
    def get(self, request):
        return Response({'message': 'hi!'})
