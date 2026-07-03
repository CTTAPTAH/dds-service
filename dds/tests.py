from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Status, TransactionType, Category, Subcategory, CashFlowRecord
from decimal import Decimal
import datetime

class StatusAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.status = Status.objects.create(name="Бизнес")

    # Получение списка статусов
    def test_get_statuses(self):
        response = self.client.get("/api/statuses/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # Создание нового статуса
    def test_create_status(self):
        response = self.client.post("/api/statuses/", {"name": "Личное"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Status.objects.count(), 2)

    # Нельзя создать статус с дублирующимся именем
    def test_create_duplicate_status(self):
        response = self.client.post("/api/statuses/", {"name": "Бизнес"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class TransactionTypeAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.transaction_type = TransactionType.objects.create(name="Списание")

    # Получение списка типов операций
    def test_get_transaction_types(self):
        response = self.client.get("/api/transaction-types/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # Создание нового типа операции
    def test_create_transaction_type(self):
        response = self.client.post("/api/transaction-types/", {"name": "Пополнение"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TransactionType.objects.count(), 2)

class CategoryAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.transaction_type = TransactionType.objects.create(name="Списание")
        self.category = Category.objects.create(
            name="Маркетинг",
            transaction_type=self.transaction_type
        )

    # Получение списка категорий
    def test_get_categories(self):
        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Фильтрация категорий по типу операции
    def test_filter_categories_by_type(self):
        response = self.client.get(f"/api/categories/?transaction_type={self.transaction_type.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # Фильтрация не возвращает чужие категории
    def test_filter_categories_wrong_type(self):
        other_type = TransactionType.objects.create(name="Пополнение")
        response = self.client.get(f"/api/categories/?transaction_type={other_type.id}")
        self.assertEqual(len(response.data), 0)

class SubcategoryAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.transaction_type = TransactionType.objects.create(name="Списание")
        self.category = Category.objects.create(
            name="Маркетинг",
            transaction_type=self.transaction_type
        )
        self.subcategory = Subcategory.objects.create(
            name="Avito",
            category=self.category
        )

    # Фильтрация подкатегорий по категории
    def test_filter_subcategories_by_category(self):
        response = self.client.get(f"/api/subcategories/?category={self.category.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Avito")

class CashFlowRecordAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.status_obj = Status.objects.create(name="Бизнес")
        self.transaction_type = TransactionType.objects.create(name="Списание")
        self.category = Category.objects.create(
            name="Маркетинг",
            transaction_type=self.transaction_type
        )
        self.subcategory = Subcategory.objects.create(
            name="Avito",
            category=self.category
        )
        self.record = CashFlowRecord.objects.create(
            date=datetime.date(2025, 6, 1),
            status=self.status_obj,
            category=self.category,
            subcategory=self.subcategory,
            amount=Decimal("5000.00"),
            comment="Тест"
        )

    # Получение списка записей ДДС
    def test_get_records(self):
        response = self.client.get("/api/records/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # Создание новой записи ДДС
    def test_create_record(self):
        data = {
            "date": "2025-06-15",
            "status": self.status_obj.id,
            "category": self.category.id,
            "subcategory": self.subcategory.id,
            "amount": "3000.00",
        }
        response = self.client.post("/api/records/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CashFlowRecord.objects.count(), 2)

    # Нельзя создать запись с подкатегорией из другой категории
    def test_create_record_wrong_subcategory(self):
        other_category = Category.objects.create(
            name="Инфраструктура",
            transaction_type=self.transaction_type
        )
        other_subcategory = Subcategory.objects.create(
            name="VPS",
            category=other_category
        )
        data = {
            "date": "2025-06-15",
            "status": self.status_obj.id,
            "category": self.category.id,
            "subcategory": other_subcategory.id,
            "amount": "3000.00",
        }
        response = self.client.post("/api/records/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Редактирование записи ДДС
    def test_update_record(self):
        data = {
            "date": "2025-06-01",
            "status": self.status_obj.id,
            "category": self.category.id,
            "subcategory": self.subcategory.id,
            "amount": "9999.00",
        }
        response = self.client.put(f"/api/records/{self.record.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.record.refresh_from_db()
        self.assertEqual(self.record.amount, Decimal("9999.00"))

    # Удаление записи ДДС
    def test_delete_record(self):
        response = self.client.delete(f"/api/records/{self.record.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CashFlowRecord.objects.count(), 0)

    # Фильтрация записей по статусу
    def test_filter_records_by_status(self):
        response = self.client.get(f"/api/records/?status={self.status_obj.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # Фильтрация по периоду дат
    def test_filter_records_by_date(self):
        response = self.client.get("/api/records/?date_from=2025-01-01&date_to=2025-12-31")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)