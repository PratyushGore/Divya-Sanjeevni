from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    """
    Represents classification layers for organic wellness catalog items.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Represents organic botanical catalog items in the SoulHealing inventory.
    """
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    regular_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    image_2 = models.ImageField(upload_to='products/', null=True, blank=True)
    image_3 = models.ImageField(upload_to='products/', null=True, blank=True)
    is_in_stock = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class CaseStudyResult(models.Model):
    """
    Represents a patient efficacy trial result/case study,
    supporting both image proof and dual video formats.
    """
    patient_name = models.CharField(max_length=120)
    age = models.IntegerField(null=True, blank=True)
    condition_treated = models.CharField(max_length=200)
    improvement_percentage = models.IntegerField(default=90)
    duration_weeks = models.IntegerField(default=4)
    
    # Proof Media Options
    before_image = models.ImageField(upload_to='results/before/', null=True, blank=True)
    after_image = models.ImageField(upload_to='results/after/', null=True, blank=True)
    video_file = models.FileField(upload_to='results/videos/', null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)
    
    testimonial = models.TextField()
    associated_product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='case_studies')
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient_name} - {self.condition_treated}"


class ContactEnquiry(models.Model):
    """
    Represents a customer inquiry or consultation request.
    """
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Resolved', 'Resolved')], default='Pending')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.subject}"
