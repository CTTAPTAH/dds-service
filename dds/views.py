from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Status, TransactionType, Category, Subcategory, CashFlowRecord
from .serializers import (
    StatusSerializer,
    TransactionTypeSerializer,
    CategorySerializer,
    SubcategorySerializer,
    CashFlowRecordSerializer
)

class StatusViewSet(viewsets.ModelViewSet):
    queryset = Status.objects.all().order_by("name")
    serializer_class = StatusSerializer

class TransactionTypeViewSet(viewsets.ModelViewSet):
    queryset = TransactionType.objects.all().order_by("name")
    serializer_class = TransactionTypeSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.select_related("transaction_type").order_by("name")
    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Фильтрация категорий по типу операции.
        # Используется на фронте: выбрал тип - подгрузились категории этого типа
        transaction_type = self.request.query_params.get("transaction_type")
        if transaction_type:
            queryset = queryset.filter(transaction_type_id=transaction_type)
        return queryset

class SubcategoryViewSet(viewsets.ModelViewSet):
    queryset = Subcategory.objects.select_related("category").order_by("name")
    serializer_class = SubcategorySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Фильтрация подкатегорий по категории
        # Используется на фронте: выбрал категорию - подгрузились её подкатегории
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category_id=category)
        return queryset

class CashFlowRecordViewSet(viewsets.ModelViewSet):
    queryset = CashFlowRecord.objects.select_related(
        "status",
        "category",
        "category__transaction_type",
        "subcategory",
    ).order_by("-date", "-created_at")
    serializer_class = CashFlowRecordSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

        # Фильтр по статусу
        status = params.get("status")
        if status:
            queryset = queryset.filter(status_id=status)

        # Фильтр по категории
        category = params.get("category")
        if category:
            queryset = queryset.filter(category_id=category)

        # Фильтр по подкатегории
        subcategory = params.get("subcategory")
        if subcategory:
            queryset = queryset.filter(subcategory_id=subcategory)

        # Фильтр по периоду дат
        date_from = params.get("date_from")
        if date_from:
            queryset = queryset.filter(date__gte=date_from)

        date_to = params.get("date_to")
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        return queryset