from rest_framework import serializers
from .models import Student, Staff

class StudentSerializer(serializers.ModelSerializer):
    """
    This converts Student database records into JSON for the Flutter app.
    It includes fields like full_name, balance, and access_code.
    """
    class Meta:
        model = Student
        fields = '__all__'

class StaffSerializer(serializers.ModelSerializer):
    """
    This handles data for the Staff section.
    """
    class Meta:
        model = Staff
        fields = '__all__'