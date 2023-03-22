from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    """
    Permission for authors to create/update/delete, read for everyone.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        else:
            if obj.author != request.user:
                raise PermissionDenied(
                    'Доступ к редактированию чужого контента закрыт.'
                )
        return True


class IsAdminOrReadOnly(BasePermission):
    """
    Permission for admins to create/update/delete, read for everyone.
    """

    def has_permission(self, request, view):

        return (request.method in SAFE_METHODS
                or request.user.is_authenticated
                and (request.user.is_superuser
                     or request.user.is_stuff))


class IsOwner(BasePermission):
    """
    Permission only for authors to create/update/delete/read.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and request.method
            in SAFE_METHODS
        )

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user
