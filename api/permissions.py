from rest_framework import permissions

class IsSchoolDataOwner(permissions.BasePermission):
    """
    CRITICAL: Ensures a user can only access data belonging 
    to their specific school.
    """
    def has_object_permission(self, request, view, obj):
        # If the object is a school, check its ID
        if isinstance(obj, School):
            return obj == request.user.profile.school
        
        # For students/staff, check if their school matches the user's school
        return obj.school == request.user.profile.school
    
from rest_framework import permissions

class IsSchoolDataOwner(permissions.BasePermission):
    """Enforces that a user only sees data from their authorized school."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # 🛡️ Server-Side Isolation: Compare the user's school to the object's school
        user_school = getattr(request.user, 'school', None)
        obj_school = getattr(obj, 'school', None)
        return user_school == obj_school