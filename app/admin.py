from django.contrib import admin
from .models import Product, CaseStudyResult, ContactEnquiry, Category

# Register your models here.
admin.site.register(Product)
admin.site.register(CaseStudyResult)
admin.site.register(ContactEnquiry)
admin.site.register(Category)
