from django import forms
from .models import CaseStudyResult, ContactEnquiry, Category, Product

class CategoryForm(forms.ModelForm):
    """
    Form to manage product categories in the admin dashboard.
    """
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Herbal Teas', 'required': 'true'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Provide description details...'}),
        }


class ProductForm(forms.ModelForm):
    """
    Form to register or update wellness items in the catalog.
    """
    class Meta:
        model = Product
        fields = ['category', 'title', 'slug', 'description', 'regular_price', 'sale_price', 'image', 'image_2', 'image_3', 'is_in_stock', 'is_featured']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Active Brightening Facial Serum'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. active-brightening-facial-serum'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 8, 'placeholder': 'Usage and benefit details...'}),
            'regular_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'is_in_stock': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CaseStudyResultForm(forms.ModelForm):
    """
    Form to publish case studies, including demographics,
    before/after images, and dual video input fields.
    """
    class Meta:
        model = CaseStudyResult
        fields = [
            'patient_name',
            'age',
            'condition_treated',
            'improvement_percentage',
            'duration_weeks',
            'before_image',
            'after_image',
            'video_file',
            'video_url',
            'testimonial',
            'associated_product'
        ]
        widgets = {
            'patient_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sarah L. / Subject 14'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 29'}),
            'condition_treated': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Eczema / Digestive Bloating'}),
            'improvement_percentage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 94'}),
            'duration_weeks': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 4'}),
            'associated_product': forms.Select(attrs={'class': 'form-control'}),
            'testimonial': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter direct quote...'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'e.g. https://www.youtube.com/embed/...'}),
        }

    def clean_patient_name(self):
        from django.utils.html import escape
        return escape(self.cleaned_data.get('patient_name', '').strip())

    def clean_condition_treated(self):
        from django.utils.html import escape
        return escape(self.cleaned_data.get('condition_treated', '').strip())

    def clean_testimonial(self):
        from django.utils.html import escape
        return escape(self.cleaned_data.get('testimonial', '').strip())

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class ContactEnquiryForm(forms.ModelForm):
    """
    Form to handle customer questions from the Contact Us page.
    """
    class Meta:
        model = ContactEnquiry
        fields = ['full_name', 'email', 'subject', 'message']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'John Doe'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'john@example.com'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Order inquiry / Consultation request'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Describe your query...'}),
        }

    def clean_full_name(self):
        from django.utils.html import escape
        return escape(self.cleaned_data.get('full_name', '').strip())

    def clean_subject(self):
        from django.utils.html import escape
        return escape(self.cleaned_data.get('subject', '').strip())

    def clean_message(self):
        from django.utils.html import escape
        return escape(self.cleaned_data.get('message', '').strip())
