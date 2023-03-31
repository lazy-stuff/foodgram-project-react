from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):
    """
    Permission for authors to create/update/delete, read for everyone.
    """

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or obj.author == request.user)


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
