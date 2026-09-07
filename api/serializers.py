from rest_framework import serializers
from .models import School

class SchoolContextSerializer(serializers.ModelSerializer):
    """Packages school branding for the mobile app"""
    class Meta:
        model = School
        fields = ['id', 'name', 'school_motto', 'logo', 'is_verified', 'school_account_id']

class UserIdentitySerializer(serializers.Serializer):
    """The Universal USDC Identity Packet"""
    token = serializers.CharField()
    role = serializers.CharField()
    display_name = serializers.CharField()
    photo = serializers.SerializerMethodField()
    school_context = SchoolContextSerializer()

    def get_photo(self, obj):
        request = self.context.get('request')
        photo_url = obj.get('photo_url')
        if photo_url and request:
            # Ensures the image link works on the local network (192.168...)
            return request.build_absolute_uri(photo_url)
        return None