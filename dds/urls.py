from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StatusViewSet,
    TransactionTypeViewSet,
    CategoryViewSet,
    SubcategoryViewSet,
    CashFlowRecordViewSet,
)

router = DefaultRouter()
router.register("statuses", StatusViewSet, basename="status")
router.register("transaction-types", TransactionTypeViewSet, basename="transaction-type")
router.register("categories", CategoryViewSet, basename="category")
router.register("subcategories", SubcategoryViewSet, basename="subcategory")
router.register("records", CashFlowRecordViewSet, basename="record")

urlpatterns = [
    path("", include(router.urls)),
]