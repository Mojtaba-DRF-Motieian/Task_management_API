import permissions
from django.contrib.auth import get_user_model
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from .models import Attachment, Comment, Project, Task
from .serializers import (
    AttachmentSerializer,
    CommentSerializer,
    ProjectSerializer,
    TaskSerializer,
)


def validate_user_id(user_id):
    if user_id in (None, ""):
        raise ValidationError({"error": "user_id is required"})

    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        raise ValidationError({"error": "user_id must be a valid integer"})

    if user_id_int <= 0:
        raise ValidationError({"error": "user_id must be positive"})

    return user_id_int


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.ProjectPermission]

    def get_queryset(self):
        # Users can see projects they created or are members of
        return Project.objects.filter(
            models.Q(creator=self.request.user) | models.Q(members=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=["post"])
    def add_member(self, request, pk=None):
        project = self.get_object()
        user_id = request.data.get("user_id")

        # Check permissions
        if project.creator != request.user:
            return Response(
                {"error": "Only project creator can add members"},
                status=status.HTTP_403_FORBIDDEN,
            )

        user_id = validate_user_id(user_id)

        if project.members.filter(id=user_id).exists():
            return Response({"error": "User is already a member"}, status=400)

        User = get_user_model()
        user = get_object_or_404(User, id=user_id)
        project.members.add(user)
        return Response({"status": "member added"})


class TaskListViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.TaskPermission]

    def get_queryset(self):
        project_id = self.kwargs.get("project_pk")
        project = get_object_or_404(Project, pk=project_id)

        # Only allow creator or members to see tasks
        user = self.request.user
        if project.creator == user or project.members.filter(id=user.id).exists():
            return Task.objects.filter(project_id=project_id)
        return Task.objects.none()

    def perform_create(self, serializer):
        project_pk = self.kwargs.get("project_pk")
        project = get_object_or_404(Project, pk=project_pk)

        # Permission check: only project creator can create tasks
        if project.creator != self.request.user:
            raise PermissionDenied(
                "You don't have permission to create tasks in this project"
            )

        serializer.save(created_by=self.request.user, project=project)

    def get_task(self):
        task = self.get_object()
        if task.project.creator != self.request.user:
            raise PermissionDenied("You arent the creator of the project")
        return task

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        task = self.get_task()
        user_id = request.data.get("user_id")
        user_id = validate_user_id(user_id)
        User = get_user_model()
        user = get_object_or_404(User, id=user_id)
        task.assignee = user
        task.save()
        return Response({"status": "task assigned"})

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        task = self.get_task()
        task.status = "done"
        task.completed_at = timezone.now()
        task.is_completed = True
        task.save()
        return Response({"status": "task completed"})


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.CommentPermission]

    def get_task(self):
        """Helper method to get task with permission check"""
        task = get_object_or_404(Task, id=self.kwargs.get("task_pk"))
        if self.request.user not in task.project.members.all():
            raise PermissionDenied("You don't have access to this task's project")
        return task

    def get_queryset(self):
        task = self.get_task()
        return Comment.objects.filter(task=task)

    def perform_create(self, serializer):
        task = self.get_task()
        serializer.save(author=self.request.user, task=task)


class AttachmentViewSet(viewsets.ModelViewSet):
    serializer_class = AttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_task(self):
        """Helper method to get task with permission check"""
        task = get_object_or_404(Task, id=self.kwargs.get("task_pk"))
        if self.request.user not in task.project.members.all():
            raise PermissionDenied("You don't have access to this task's project")
        return task

    def get_queryset(self):
        task = self.get_task()
        return Attachment.objects.filter(task=task)

    def perform_create(self, serializer):
        task = self.get_task()  # Reuse the same permission check
        file_name = serializer.validated_data["file"].name
        serializer.save(uploaded_by=self.request.user, task=task, file_name=file_name)
