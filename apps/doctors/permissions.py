from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsCreatorOrReadOnly(BasePermission):
    """Any authenticated user may read; only the creator may modify or delete."""

    message = "Only the user who created this doctor can modify or delete it."

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.created_by_id == request.user.id
