from rest_framework import serializers
from .models import Student, AcademicResult, FeesTracker

class StudentSerializer(serializers.ModelSerializer):
    # 🕵️ We include the child data so the app has 'everything' on login
    marks = serializers.SerializerMethodField()
    fees = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = '__all__'

    def get_marks(self, obj):
        # Returns all academic results for this student
        return list(obj.marks.values())

    def get_fees(self, obj):
        # Returns the current financial standing
        tracker = FeesTracker.objects.filter(student=obj).first()
        return {
            "total_due": tracker.total_fees_due if tracker else 0,
            "total_paid": tracker.total_fees_paid if tracker else 0,
            "balance": tracker.fees_balance if tracker else 0
        }