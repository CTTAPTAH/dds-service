from django.contrib import admin
from .models import Status, TransactionType, Category, Subcategory, CashFlowRecord

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(TransactionType)
class TransactionTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "transaction_type")
    list_filter = ("transaction_type",)
    search_fields = ("name",)

@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category")
    list_filter = ("category",)
    search_fields = ("name",)

@admin.register(CashFlowRecord)
class CashFlowRecordAdmin(admin.ModelAdmin):
    list_display = ("date", "status", "category", "subcategory", "amount", "comment")
    list_filter = ("status", "category", "subcategory")
    search_fields = ("comment",)
    date_hierarchy = "date"