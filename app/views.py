from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.db.models import Count
from django.utils.text import slugify
import json
from functools import wraps
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import redirect
import logging
from django.utils.html import escape

from .models import Product, CaseStudyResult, ContactEnquiry, Category
from .forms import CaseStudyResultForm, ContactEnquiryForm, CategoryForm, ProductForm
from .security import generate_jwt_token, get_client_ip

logger = logging.getLogger('security')

def admin_required(view_func):
    """
    Decorator that checks if the request user is authenticated and staff.
    Properly handles both AJAX API routes (401/403 response) and HTML portal pages (redirects/render 403).
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            logger.warning(
                f"AUTH_FAILURE: Unauthenticated access attempt to protected route '{request.path}' "
                f"from IP {get_client_ip(request)}."
            )
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'status': 'error', 
                    'message': 'Unauthorized. Token or session authentication required.'
                }, status=401)
            return redirect('admin_login')
            
        if not request.user.is_staff:
            logger.warning(
                f"AUTH_DENIED: Unauthorized access attempt by authenticated user '{request.user.username}' (ID: {request.user.id}) "
                f"to admin route '{request.path}' from IP {get_client_ip(request)}."
            )
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'status': 'error', 
                    'message': 'Forbidden. Administrative privileges required.'
                }, status=403)
            return render(request, 'store/index.html', {
                'error_message': 'Access Denied. Administrative privileges required.'
            }, status=403)
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# Public Views
def home_view(request):
    """
    Renders the public homepage (index.html).
    """
    featured_products = Product.objects.filter(is_featured=True).order_by('-created_at')[:4]
    if not featured_products.exists():
        featured_products = Product.objects.all().order_by('-created_at')[:4]
    return render(request, 'store/index.html', {'featured_products': featured_products})


def products_view(request):
    """
    Renders the public catalog page (products.html).
    """
    products = Product.objects.all().order_by('-created_at')
    categories = Category.objects.all().annotate(product_count=Count('products'))
    return render(request, 'store/products.html', {
        'products': products,
        'categories': categories
    })


def results_view(request):
    """
    Renders the public clinical results & case studies page (results.html).
    """
    case_studies = CaseStudyResult.objects.all().order_by('-published_at')
    return render(request, 'store/results.html', {'case_studies': case_studies})


def business_view(request):
    """
    Renders the B2B Partnerships & Wholesale page (business.html).
    """
    return render(request, 'store/business.html')


def contact_view(request):
    """
    Renders the public Contact Us & Consultation request page (contact.html).
    """
    return render(request, 'store/contact.html')


def search_view(request):
    """
    Handles searches for clinical results & case studies only.
    """
    query = request.GET.get('q', '').strip()
    case_studies = CaseStudyResult.objects.none()
    
    if query:
        # Search results/case studies by patient name, condition treated, or testimonial text
        case_studies = CaseStudyResult.objects.filter(patient_name__icontains=query) | \
                       CaseStudyResult.objects.filter(condition_treated__icontains=query) | \
                       CaseStudyResult.objects.filter(testimonial__icontains=query)
                       
    return render(request, 'store/search.html', {
        'query': query,
        'case_studies': case_studies.distinct()
    })


def support_norms_view(request):
    """
    Renders the public Support & Norms guidelines page (support-norms.html).
    """
    return render(request, 'store/support-norms.html')


# Admin Portal Views
@ensure_csrf_cookie
@admin_required
def admin_dashboard_view(request):
    """
    Renders the admin dashboard overview page.
    """
    total_products = Product.objects.count()
    total_published_results = CaseStudyResult.objects.count()
    total_contact_enquiries = ContactEnquiry.objects.count()
    pending_enquiries = ContactEnquiry.objects.filter(status='Pending').count()
    recent_enquiries = ContactEnquiry.objects.all().order_by('-submitted_at')[:5]
    
    context = {
        'total_products': total_products,
        'total_published_results': total_published_results,
        'total_contact_enquiries': total_contact_enquiries,
        'pending_enquiries': pending_enquiries,
        'recent_enquiries': recent_enquiries,
    }
    return render(request, 'admin_portal/admin-dashboard.html', context)


@ensure_csrf_cookie
@admin_required
def admin_categories_view(request):
    """
    Renders the admin category management page.
    """
    categories = Category.objects.all().annotate(product_count=Count('products')).order_by('name')
    context = {
        'categories': categories,
        'pending_enquiries': ContactEnquiry.objects.filter(status='Pending').count()
    }
    return render(request, 'admin_portal/admin-categories.html', context)


# Admin and Public API Endpoints
@require_http_methods(["POST"])
@admin_required
def case_study_create_api(request):
    """
    API endpoint to handle AJAX submissions for new clinical case studies.
    """
    form = CaseStudyResultForm(request.POST, request.FILES)
    if form.is_valid():
        case_study = form.save()
        return JsonResponse({
            'status': 'success',
            'message': 'Clinical Case Study published successfully.',
            'data': {
                'id': case_study.id,
                'patient_name': case_study.patient_name,
                'condition_treated': case_study.condition_treated
            }
        })
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Validation error. Please verify the highlighted details.',
            'errors': form.errors
        }, status=400)


@require_http_methods(["POST"])
def contact_enquiry_create_api(request):
    """
    Public API endpoint to submit a Contact Enquiry from the 'Contact Us' page.
    """
    form = ContactEnquiryForm(request.POST)
    if form.is_valid():
        enquiry = form.save()
        return JsonResponse({
            'status': 'success',
            'message': 'Your enquiry has been submitted. A wellness specialist will get back to you.'
        })
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Validation error. Please fill out all required fields correctly.',
            'errors': form.errors
        }, status=400)


@require_http_methods(["GET", "POST", "DELETE"])
@admin_required
def contact_enquiry_admin_api(request, enquiry_id=None):
    """
    Admin API endpoint to fetch, resolve, or delete inquiries.
    """
    if request.method == "GET":
        if enquiry_id:
            enquiry = get_object_or_404(ContactEnquiry, id=enquiry_id)
            return JsonResponse({
                'id': enquiry.id,
                'name': enquiry.full_name,
                'email': enquiry.email,
                'subject': enquiry.subject,
                'message': enquiry.message,
                'status': enquiry.status,
                'created_at': enquiry.submitted_at.strftime("%B %d, %Y, %I:%M %p")
            })
        else:
            enquiries = ContactEnquiry.objects.all().order_by('-submitted_at')
            data = [{
                'id': e.id,
                'name': e.full_name,
                'email': e.email,
                'subject': e.subject,
                'status': e.status,
                'created_at': e.submitted_at.strftime("%Y-%m-%d %H:%M:%S")
            } for e in enquiries]
            return JsonResponse({'enquiries': data})

    elif request.method == "POST":
        try:
            if request.content_type == 'application/json':
                payload = json.loads(request.body.decode('utf-8'))
                action = payload.get('action')
            else:
                action = request.POST.get('action')
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Invalid payload format.'}, status=400)
            
        if not action or not isinstance(action, str):
            return JsonResponse({'status': 'error', 'message': 'Action parameter is required.'}, status=400)
            
        action = action.strip()
        if action == "resolve" and enquiry_id:
            enquiry = get_object_or_404(ContactEnquiry, id=enquiry_id)
            enquiry.status = "Resolved"
            enquiry.save()
            return JsonResponse({
                'status': 'success',
                'message': f'Enquiry from {enquiry.full_name} marked as resolved.'
            })
        return JsonResponse({'status': 'error', 'message': 'Invalid action or request state.'}, status=400)

    elif request.method == "DELETE":
        if enquiry_id:
            enquiry = get_object_or_404(ContactEnquiry, id=enquiry_id)
            name = enquiry.full_name
            enquiry.delete()
            return JsonResponse({
                'status': 'success',
                'message': f'Enquiry from {name} has been deleted.'
            })
        return JsonResponse({'status': 'error', 'message': 'Missing enquiry ID'}, status=400)


@require_http_methods(["GET", "POST", "DELETE"])
@admin_required
def category_admin_api(request, category_id=None):
    """
    Admin API endpoint to list, create, or delete product categories via AJAX.
    """
    if request.method == "GET":
        categories = Category.objects.all().annotate(product_count=Count('products')).order_by('name')
        data = [{
            'id': c.id,
            'name': c.name,
            'slug': c.slug,
            'description': c.description or '',
            'product_count': c.product_count
        } for c in categories]
        return JsonResponse({'categories': data})

    elif request.method == "POST":
        try:
            if request.content_type == 'application/json':
                payload = json.loads(request.body.decode('utf-8'))
                name = payload.get('name')
                description = payload.get('description', '')
            else:
                name = request.POST.get('name')
                description = request.POST.get('description', '')
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Invalid request payload format.'}, status=400)

        if not name or not isinstance(name, str) or not name.strip():
            return JsonResponse({'status': 'error', 'message': 'Category name is required.'}, status=400)

        # Enforce length restrictions to prevent database column overflow
        if len(name) > 100:
            return JsonResponse({'status': 'error', 'message': 'Category name cannot exceed 100 characters.'}, status=400)

        # Sanitize HTML tags to prevent stored XSS attacks
        name = escape(name.strip())
        if description and isinstance(description, str):
            description = escape(description.strip())
        elif description:
            description = ""

        slug = slugify(name)
        base_slug = slug
        counter = 1
        while Category.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        category = Category.objects.create(name=name, slug=slug, description=description)
        return JsonResponse({
            'status': 'success',
            'message': f"Category '{category.name}' created successfully.",
            'category': {
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'description': category.description or '',
                'product_count': 0
            }
        })

    elif request.method == "DELETE":
        if category_id:
            category = get_object_or_404(Category, id=category_id)
            name = category.name
            category.delete()
            return JsonResponse({
                'status': 'success',
                'message': f"Category '{name}' deleted successfully."
            })
        return JsonResponse({'status': 'error', 'message': 'Missing category ID.'}, status=400)


def product_detail(request, slug):
    """
    Renders the public detail view for a specific organic wellness product.
    """
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:3]
    return render(request, 'store/product-detail.html', {
        'product': product,
        'related_products': related_products
    })


def result_detail(request, pk):
    """
    Renders the public detail view for a specific clinical case study/result.
    """
    study = get_object_or_404(CaseStudyResult, pk=pk)
    recommended_product = study.associated_product
    return render(request, 'store/result-detail.html', {
        'study': study,
        'recommended_product': recommended_product
    })


@require_http_methods(["POST"])
@admin_required
def delete_category_view(request, category_id):
    """
    Handles form POST deletion for a product category.
    """
    from django.shortcuts import redirect
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    return redirect('admin_categories')


def product_detail_demo(request):
    """
    Renders product-detail.html with a fallback demo product context.
    """
    product = Product.objects.first()
    related_products = Product.objects.all().exclude(id=product.id if product else None)[:3]
    return render(request, 'store/product-detail.html', {
        'product': product,
        'related_products': related_products
    })


def result_detail_demo(request):
    """
    Renders result-detail.html with a fallback demo case study context.
    """
    study = CaseStudyResult.objects.first()
    recommended_product = study.associated_product if study else None
    return render(request, 'store/result-detail.html', {
        'study': study,
        'recommended_product': recommended_product
    })


@ensure_csrf_cookie
@admin_required
def admin_contact_enquiries_view(request):
    """
    Renders the admin contact enquiries panel.
    """
    enquiries = ContactEnquiry.objects.all().order_by('-submitted_at')
    pending_enquiries = ContactEnquiry.objects.filter(status='Pending').count()
    return render(request, 'admin_portal/admin-contact-enquiries.html', {
        'enquiries': enquiries,
        'pending_enquiries': pending_enquiries,
    })


@ensure_csrf_cookie
@admin_required
def admin_add_product_view(request):
    """
    Renders the admin add product form page.
    """
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            from django.shortcuts import redirect
            return redirect('admin_dashboard')
    else:
        form = ProductForm()
    
    categories = Category.objects.all()
    pending_enquiries = ContactEnquiry.objects.filter(status='Pending').count()
    return render(request, 'admin_portal/admin-add-product.html', {
        'form': form,
        'categories': categories,
        'pending_enquiries': pending_enquiries,
    })


@ensure_csrf_cookie
@admin_required
def admin_add_result_view(request):
    """
    Renders the admin add case study result form page.
    """
    if request.method == "POST":
        form = CaseStudyResultForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            from django.shortcuts import redirect
            return redirect('admin_dashboard')
    else:
        form = CaseStudyResultForm()
        
    products = Product.objects.all()
    pending_enquiries = ContactEnquiry.objects.filter(status='Pending').count()
    return render(request, 'admin_portal/admin-add-result.html', {
        'form': form,
        'products': products,
        'pending_enquiries': pending_enquiries,
    })


@ensure_csrf_cookie
@admin_required
def admin_manage_products_view(request):
    """
    Renders the admin manage products page with list, edit, and delete functionality.
    """
    products = Product.objects.select_related('category').order_by('-created_at')
    categories = Category.objects.all()
    pending_enquiries = ContactEnquiry.objects.filter(status='Pending').count()
    return render(request, 'admin_portal/admin-manage-products.html', {
        'products': products,
        'categories': categories,
        'pending_enquiries': pending_enquiries,
    })


@ensure_csrf_cookie
@admin_required
def admin_manage_results_view(request):
    """
    Renders the admin manage results page with list, edit, and delete functionality.
    """
    results = CaseStudyResult.objects.select_related('associated_product').order_by('-published_at')
    products = Product.objects.all()
    pending_enquiries = ContactEnquiry.objects.filter(status='Pending').count()
    return render(request, 'admin_portal/admin-manage-results.html', {
        'results': results,
        'products': products,
        'pending_enquiries': pending_enquiries,
    })


@require_http_methods(["POST"])
@admin_required
def product_add_api(request):
    """
    API endpoint to create a new product from the Add Product form.
    """
    form = ProductForm(request.POST, request.FILES)
    if form.is_valid():
        product = form.save()
        return JsonResponse({
            'status': 'success',
            'message': f"Product '{product.title}' published successfully.",
            'data': {'id': product.id, 'title': product.title, 'slug': product.slug}
        })
    return JsonResponse({'status': 'error', 'message': 'Validation error.', 'errors': form.errors}, status=400)


@require_http_methods(["GET", "POST", "DELETE"])
@admin_required
def product_admin_api(request, product_id=None):
    """
    Admin API to fetch, update, or delete a product.
    """
    if request.method == "GET" and product_id:
        product = get_object_or_404(Product, id=product_id)
        return JsonResponse({
            'id': product.id,
            'title': product.title,
            'slug': product.slug,
            'description': product.description,
            'regular_price': str(product.regular_price),
            'sale_price': str(product.sale_price) if product.sale_price else '',
            'category_id': product.category_id,
            'is_in_stock': product.is_in_stock,
            'is_featured': product.is_featured,
            'image_2_url': product.image_2.url if product.image_2 else '',
            'image_3_url': product.image_3.url if product.image_3 else '',
            'image_url': product.image.url if product.image else ''
        })

    elif request.method == "POST" and product_id:
        product = get_object_or_404(Product, id=product_id)
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            return JsonResponse({'status': 'success', 'message': f"Product '{product.title}' updated successfully."})
        return JsonResponse({'status': 'error', 'message': 'Validation error.', 'errors': form.errors}, status=400)

    elif request.method == "DELETE" and product_id:
        product = get_object_or_404(Product, id=product_id)
        title = product.title
        product.delete()
        return JsonResponse({'status': 'success', 'message': f"Product '{title}' deleted successfully."})

    return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)


@require_http_methods(["GET", "POST", "DELETE"])
@admin_required
def result_admin_api(request, result_id=None):
    """
    Admin API to fetch, update, or delete a case study result.
    """
    if request.method == "GET" and result_id:
        result = get_object_or_404(CaseStudyResult, id=result_id)
        return JsonResponse({
            'id': result.id,
            'patient_name': result.patient_name,
            'age': result.age or '',
            'condition_treated': result.condition_treated,
            'improvement_percentage': result.improvement_percentage,
            'duration_weeks': result.duration_weeks,
            'testimonial': result.testimonial,
            'associated_product_id': result.associated_product_id or '',
            'video_url': result.video_url or ''
        })

    elif request.method == "POST" and result_id:
        result = get_object_or_404(CaseStudyResult, id=result_id)
        form = CaseStudyResultForm(request.POST, request.FILES, instance=result)
        if form.is_valid():
            result = form.save()
            return JsonResponse({'status': 'success', 'message': f"Result for '{result.patient_name}' updated successfully."})
        return JsonResponse({'status': 'error', 'message': 'Validation error.', 'errors': form.errors}, status=400)

    elif request.method == "DELETE" and result_id:
        result = get_object_or_404(CaseStudyResult, id=result_id)
        name = result.patient_name
        result.delete()
        return JsonResponse({'status': 'success', 'message': f"Result for '{name}' deleted successfully."})

    return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)


@csrf_protect
def admin_login_view(request):
    """
    Handles administrator authentication.
    """
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')
        
    error_message = None
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            error_message = "Please provide both username and password."
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_staff:
                    auth_login(request, user)
                    next_url = request.GET.get('next') or request.POST.get('next')
                    if next_url and next_url.startswith('/'):
                        return redirect(next_url)
                    return redirect('admin_dashboard')
                else:
                    error_message = "Access denied. Administrative privileges required."
            else:
                error_message = "Invalid username or password."
                
    return render(request, 'admin_portal/admin-login.html', {
        'error_message': error_message,
        'next': request.GET.get('next', '')
    })


def admin_logout_view(request):
    """
    Logs out the administrator.
    """
    if request.method == "POST" or request.method == "GET":
        auth_logout(request)
    return redirect('admin_login')


@require_http_methods(["POST"])
def get_jwt_token_api(request):
    """
    API endpoint to exchange admin credentials (username/password) for a secure JWT token.
    """
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body.decode('utf-8'))
        else:
            data = request.POST
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Invalid request body format.'}, status=400)

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return JsonResponse({'status': 'error', 'message': 'Both username and password are required.'}, status=400)

    # Authenticate credentials using Django auth backend
    user = authenticate(request, username=username, password=password)

    if user is not None:
        if user.is_active:
            if user.is_staff:
                token = generate_jwt_token(user)
                logger.info(
                    f"AUTH_SUCCESS: User '{username}' (ID: {user.id}) successfully "
                    f"obtained JWT token from IP {get_client_ip(request)}."
                )
                return JsonResponse({
                    'status': 'success',
                    'token': token,
                    'user': {
                        'username': user.username,
                        'is_staff': user.is_staff,
                        'is_superuser': user.is_superuser
                    }
                })
            else:
                logger.warning(
                    f"AUTH_FAILURE: Non-staff user '{username}' attempted "
                    f"JWT generation from IP {get_client_ip(request)}."
                )
                return JsonResponse({'status': 'error', 'message': 'Access Denied. Staff credentials required.'}, status=403)
        else:
            logger.warning(
                f"AUTH_FAILURE: Disabled user '{username}' attempted "
                f"JWT generation from IP {get_client_ip(request)}."
            )
            return JsonResponse({'status': 'error', 'message': 'User account is disabled.'}, status=403)
    else:
        logger.warning(
            f"AUTH_FAILURE: Invalid login credentials for user '{username}' "
            f"from IP {get_client_ip(request)}."
        )
        return JsonResponse({'status': 'error', 'message': 'Invalid username or password.'}, status=401)
