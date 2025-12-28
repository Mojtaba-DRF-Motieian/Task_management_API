from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import (
    AttachmentViewSet,
    CommentViewSet,
    ProjectViewSet,
    TaskListViewSet,
    TaskViewSet,
)

router = DefaultRouter()
router.register(r"projects", ProjectViewSet, basename="project")
router.register(r"tasks", TaskListViewSet, basename="task")

# Create a nested router for tasks under projects
projects_router = routers.NestedSimpleRouter(router, r"projects", lookup="project")
projects_router.register(r"tasks", TaskViewSet, basename="project-tasks")

# Create nested routers for comments and attachments under tasks
tasks_router = routers.NestedSimpleRouter(projects_router, r"tasks", lookup="task")
tasks_router.register(r"comments", CommentViewSet, basename="task-comments")
tasks_router.register(r"attachments", AttachmentViewSet, basename="task-attachments")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(projects_router.urls)),
    path("", include(tasks_router.urls)),
]
