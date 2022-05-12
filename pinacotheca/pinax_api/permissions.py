from rest_framework import permissions
from rest_framework.permissions import  IsAuthenticated, IsAuthenticatedOrReadOnly, BasePermission


class IsEditorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_editor

