from rest_framework import serializers

from .models import Result

class InputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ['id', 'created', 'model_input', 'delivered']

# class InputSerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only=True)
#     model_input = serializers.CharField(max_length = 100)
#     delivered = serializers.BooleanField(required=False, default=True)

#     def create(self, validated_data):
#         return Results.objects.create(**validated_data)