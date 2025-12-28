from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Attachment, Comment, Project, Task

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "content", "author", "created_at", "updated_at"]
        read_only_fields = ["task", "author", "created_at", "updated_at"]


class AttachmentSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    file_size = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = ["id", "file", "file_name", "uploaded_by", "uploaded_at", "file_size"]
        read_only_fields = ["task", "uploaded_by", "uploaded_at", "file_name"]

    def get_file_size(self, obj):
        try:
            return obj.file.size
        except (AttributeError, OSError):
            return None


class TaskSerializer(serializers.ModelSerializer):
    assignee = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    is_completed = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "project",
            "assignee",
            "created_by",
            "priority",
            "status",
            "due_date",
            "completed_at",
            "created_at",
            "updated_at",
            "is_completed",
            "comments",
            "attachments",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at"]


class ProjectSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)
    member_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="members",
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "description",
            "creator",
            "members",
            "status",
            "start_date",
            "deadline",
            "created_at",
            "updated_at",
            "tasks",
            "member_ids",
        ]
        read_only_fields = ["creator", "created_at", "updated_at"]

    def create(self, validated_data):
        creator = validated_data.get("creator")  # noqa
        members = validated_data.pop("members", [])
        project = Project.objects.create(**validated_data)
        project.members.set(members)
        return project
