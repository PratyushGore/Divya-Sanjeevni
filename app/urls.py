from django.urls import path
from . import views

urlpatterns = [
    # Public Pages
    path('', views.home_view, name='home'),
    path('index.html', views.home_view, name='home_html'),
    path('products/', views.products_view, name='products'),
    path('products.html', views.products_view, name='products_html'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('product-detail.html', views.product_detail_demo, name='product_detail_demo'),
    path('results/', views.results_view, name='results'),
    path('results.html', views.results_view, name='results_html'),
    path('results/<int:pk>/', views.result_detail, name='result_detail'),
    path('result-detail.html', views.result_detail_demo, name='result_detail_demo'),
    path('business/', views.business_view, name='business'),
    path('business.html', views.business_view, name='business_html'),
    path('contact/', views.contact_view, name='contact'),
    path('contact.html', views.contact_view, name='contact_html'),
    path('search/', views.search_view, name='search'),
    path('support-norms/', views.support_norms_view, name='support_norms'),
    path('support-norms.html', views.support_norms_view, name='support_norms_html'),

    # Admin Portal Views
    path('admin-portal/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-dashboard.html', views.admin_dashboard_view, name='admin_dashboard_html'),
    path('admin-portal/login/', views.admin_login_view, name='admin_login'),
    path('admin-login.html', views.admin_login_view, name='admin_login_html'),
    path('admin-portal/logout/', views.admin_logout_view, name='admin_logout'),
    path('admin-portal/categories/', views.admin_categories_view, name='admin_categories'),
    path('admin-categories.html', views.admin_categories_view, name='admin_categories_html'),
    path('admin-portal/categories/<int:category_id>/delete/', views.delete_category_view, name='delete_category'),
    path('admin-contact-enquiries.html', views.admin_contact_enquiries_view, name='admin_contact_enquiries_html'),
    path('admin-add-product.html', views.admin_add_product_view, name='admin_add_product_html'),
    path('admin-add-result.html', views.admin_add_result_view, name='admin_add_result_html'),
    path('admin-manage-products.html', views.admin_manage_products_view, name='admin_manage_products'),
    path('admin-manage-results.html', views.admin_manage_results_view, name='admin_manage_results'),

    # Public AJAX APIs
    path('api/contact/', views.contact_enquiry_create_api, name='api_contact_create'),
    path('api/auth/token/', views.get_jwt_token_api, name='api_jwt_token'),

    # Admin AJAX APIs
    path('api/results/add/', views.case_study_create_api, name='api_case_study_create'),
    path('api/products/add/', views.product_add_api, name='api_product_add'),
    path('api/admin/products/', views.product_admin_api, name='api_admin_products_list'),
    path('api/admin/products/<int:product_id>/', views.product_admin_api, name='api_admin_product_detail'),
    path('api/admin/results/', views.result_admin_api, name='api_admin_results_list'),
    path('api/admin/results/<int:result_id>/', views.result_admin_api, name='api_admin_result_detail'),
    path('api/admin/enquiries/', views.contact_enquiry_admin_api, name='api_admin_enquiries_list'),
    path('api/admin/enquiries/<int:enquiry_id>/', views.contact_enquiry_admin_api, name='api_admin_enquiry_detail'),
    path('api/admin/categories/', views.category_admin_api, name='api_admin_categories'),
    path('api/admin/categories/<int:category_id>/', views.category_admin_api, name='api_admin_category_detail'),
]
