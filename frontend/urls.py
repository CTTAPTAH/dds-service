from django.urls import path
from . import views

urlpatterns = [
    path("", views.records, name="records"),
    path("records/create/", views.record_form, name="record_create"),
    path("records/<int:pk>/edit/", views.record_form, name="record_edit"),
    path("references/", views.references, name="references"),
]