from rest_framework import serializers
from .models import Status, TransactionType, Category, Subcategory, CashFlowRecord

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ("id", "name")

class TransactionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionType
        fields = ("id", "name")

class CategorySerializer(serializers.ModelSerializer):
    transaction_type_name = serializers.CharField(source='transaction_type.name', read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'transaction_type', 'transaction_type_name')

class SubcategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Subcategory
        fields = ('id', 'name', 'category', 'category_name')

class CashFlowRecordSerializer(serializers.ModelSerializer):
    # Дополнительные поля только для чтения, чтобы в ответе API
    # видеть не просто id, а читаемые названия
    status_name = serializers.CharField(source="status.name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    subcategory_name = serializers.CharField(source="subcategory.name", read_only=True)
    transaction_type_name = serializers.CharField(source="category.transaction_type.name", read_only=True)

    class Meta:
        model = CashFlowRecord
        fields = (
            "id",
            "date",
            "status",
            "status_name",
            "category",
            "category_name",
            "subcategory",
            "subcategory_name",
            "transaction_type_name",
            "amount",
            "comment",
            "created_at",
        )

    def validate(self, data):
        category = data.get("category")
        subcategory = data.get("subcategory")

        # Подкатегория должна принадлежать выбранной категории
        if category and subcategory:
            if subcategory.category != category:
                raise serializers.ValidationError(
                    "Подкатегория не принадлежит выбранной категории."
                )

        return data