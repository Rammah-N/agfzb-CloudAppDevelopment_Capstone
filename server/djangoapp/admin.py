from django.contrib import admin
from .models import CarMake, CarModel

# Register your models here.
admin.site.register(CarMake)
admin.site.register(CarModel)

# CarModelInline class
class CarModelInline(admin.StackedInline):
    model = CarModel
    extra = 1 

# CarModelAdmin class
class CarModelAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "dealer_id",
        "make",
        "carType",
    ]

# CarMakeAdmin class with CarModelInline
class CarMakeAdmin(admin.ModelAdmin):
    inlines = [CarModelInline]
    list_display = ["name", "description"]