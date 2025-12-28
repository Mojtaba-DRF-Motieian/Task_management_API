from django.shortcuts import get_object_or_404
from rest_framework import permissions

from .models import Project


class ProjectPermission(permissions.BasePermission):
    """
    Permissions for ProjectViewSet:
    - Any authenticated user can create a project (for now).
    - Only the project creator can add members.
    """

    def has_permission(self, request, view):
        # Allow all authenticated users to create projects
        if view.action == "create":
            return request.user and request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        # Only the creator can add members
        if not request.user or not request.user.is_authenticated:
            return False

        if view.action == "add_member":
            return obj.creator == request.user
        return True


def return_project(view):
    """
    Given a DRF view, extract project_pk from its kwargs
    and return the corresponding Project instance.
    Returns False if no project_pk is provided.
    """
    project_pk = view.kwargs.get("project_pk")
    if not project_pk:
        return False
    project = get_object_or_404(Project, pk=project_pk)
    return project


class TaskPermission(permissions.BasePermission):
    """
    Permissions for TaskViewSet:
    - Only authenticated users can access.
    - Only the project creator can create tasks.
    - Only the project creator can assign/complete tasks.
    """

    def has_permission(self, request, view):
        # Require authentication for all actions
        if not request.user or not request.user.is_authenticated:
            return False

        project = return_project(view)
        if project is False:
            return False

        if view.action == "create":
            return project.creator == request.user

        if view.action == "list":
            return (
                project.creator == request.user
                or project.members.filter(id=request.user.id).exists()
            )

        return False

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        if view.action in ["assign", "complete", "update", "partial_update", "destroy"]:
            return obj.project.creator == request.user

        if view.action == "retrieve":
            return (
                obj.project.creator == request.user
                or obj.project.members.filter(id=request.user.id).exists()
            )
        return False


class CommentPermission(permissions.BasePermission):
    """
    Permissions for CommentViewSet:
    - Only project members (including creator) can view or create comments.
    - Only the project creator can update or delete comments.
    """

    def has_permission(self, request, view):
        # Must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # For list and create, check project membership via URL
        if view.action in ["list", "create"]:
            project = return_project(view)
            if project is False:
                return False
            return (
                project.creator == request.user
                or project.members.filter(id=request.user.id).exists()
            )

        # For retrieve/update/destroy, object-level permissions will handle it
        return False

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        # Viewing allowed for members or creator
        if view.action == "retrieve":
            return (
                obj.task.project.creator == request.user
                or obj.task.project.members.filter(id=request.user.id).exists()
            )

        # Updating or deleting allowed only for project creator
        if view.action in ["update", "partial_update", "destroy"]:
            return obj.task.project.creator == request.user

        return False


class AttachmentPermission(permissions.BasePermission):
    """
    Permissions for CommentViewSet:
    - Only project members (including creator) can view or create comments.
    - Only the project creator can update or delete comments.
    """

    def has_permission(self, request, view):
        # Must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # For list and create, check project membership via URL
        if view.action in ["list", "create"]:
            project = return_project(view)
            if project is False:
                return False
            return (
                project.creator == request.user
                or project.members.filter(id=request.user.id).exists()
            )

        # For retrieve/update/destroy, object-level permissions will handle it
        return False

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        # Viewing allowed for members or creator
        if view.action == "retrieve":
            return (
                obj.task.project.creator == request.user
                or obj.task.project.members.filter(id=request.user.id).exists()
            )

        # Updating or deleting allowed only for project creator
        if view.action in ["update", "partial_update", "destroy"]:
            return obj.task.project.creator == request.user

        return False
