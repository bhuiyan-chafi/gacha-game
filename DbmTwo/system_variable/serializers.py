from rest_framework import serializers
from .models import SystemVariable


class SystemVariableSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemVariable
        fields = ['id', 'name', 'value']  # Include id, name, and value fields
