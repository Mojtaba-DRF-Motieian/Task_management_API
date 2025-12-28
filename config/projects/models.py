from django.conf import settings
from django.db import models


class Project(models.Model):
    # Basic project info
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Relationships
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_projects",
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="projects", blank=True
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_date = models.DateField(null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)

    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        ON_HOLD = "on_hold", "On Hold"

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PLANNED
    )

    def __str__(self):
        return f"{self.id} - {self.title}"


class Task(models.Model):
    # Basic task info
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Relationships
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    # we assume that one task is for one person
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_tasks"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        Medium = "medium", "Medium"
        High = "high", "High"
        ON_HOLD = "critical", "Critical"

    priority = models.CharField(
        max_length=20, choices=Priority.choices, default=Priority.LOW
    )

    class Status(models.TextChoices):
        TO_DO = "todo", "To Do"
        IN_PROGRESS = "in_progress", "In Progress"
        IN_REVIEW = "review", "In Review"
        DONE = "done", "Done"

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PLANNED
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.project.title}"

    @property
    def is_completed(self):
        return self.status == "done"


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="task_comments"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.author} on {self.task.title}"


class Attachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="attachments/%Y/%m/%d/")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_name = models.CharField(max_length=255)

    def __str__(self):
        return self.file_name
