from django.db import models

class Status(models.Model):
    """
    Справочник статусов записи: Бизнес / Личное / Налог.
    Расширяемый список. Новые значения добавляются через интерфейс, без изменения кода.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")

    class Meta:
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"
        ordering = ["name"]

    def __str__(self):
        return self.name

class TransactionType(models.Model):
    """
    Справочник типов операции: Пополнение / Списание.
    Расширяемый список.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")

    class Meta:
        verbose_name = "Тип операции"
        verbose_name_plural = "Типы операций"
        ordering = ["name"]

    def __str__(self):
        return self.name

class Category(models.Model):
    """
    Категория: Маркетинг / Инфраструктура.
    Привязана к конкретному типу операции (по заданию).
    """
    name = models.CharField(max_length=150, verbose_name="Название")
    transaction_type = models.ForeignKey(
        TransactionType,
        on_delete=models.PROTECT,
        related_name="categories",
        verbose_name="Тип операции"
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]
        # Нельзя создать две записи, у которых одновременно совпадают и name, и transaction_type
        unique_together = ("name", "transaction_type")

    def __str__(self):
        return f"{self.name} ({self.transaction_type.name})"

class Subcategory(models.Model):
    """
    Подкатегория: VPS / Avito.
    Привязана к конкретной категории.
    """
    name = models.CharField(max_length=150, verbose_name="Название")
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="subcategories",
        verbose_name="Категория"
    )

    class Meta:
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"
        ordering = ["name"]
        # Нельзя создать две записи, у которых одновременно совпадают и name, и category
        unique_together = ("name", "category")

    def __str__(self):
        return f"{self.name} ({self.category.name})"

class CashFlowRecord(models.Model):
    """
    Сама запись о движении денежных средств.
    Тип операции получаем через category.transaction_type. Без дублирования
    """
    date = models.DateField(
        verbose_name="Дата",
        help_text="Заполняется автоматически, можно изменить вручную"
    )
    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        related_name="records",
        verbose_name="Статус"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="records",
        verbose_name="Категория"
    )
    subcategory = models.ForeignKey(
        Subcategory,
        on_delete=models.PROTECT,
        related_name="records",
        verbose_name="Подкатегория"
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Сумма"
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name="Комментарий"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Создано в системе"
    )

    class Meta:
        verbose_name = "Запись ДДС"
        verbose_name_plural = "Записи ДДС"
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.date} | {self.category} | {self.amount} р."