from .models import Category, Product, CaseStudyResult, ContactEnquiry

def global_context(request):
    """
    Injects global catalog data and admin indicators across templates.
    """
    return {
        'all_categories': Category.objects.all().order_by('name'),
        'total_products_count': Product.objects.count(),
        'total_results_count': CaseStudyResult.objects.count(),
        'pending_enquiries_count': ContactEnquiry.objects.filter(status='Pending').count(),
    }
