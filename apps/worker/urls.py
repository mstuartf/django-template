from django.urls import path

from . import views

urlpatterns = [
    path('', views.worker_task_handler, name='worker_task_handler'),
    # path('example-job/', views.example_cron_task, name='example_cron_task'),
]
