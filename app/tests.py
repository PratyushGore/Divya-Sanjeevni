from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from .models import Category, Product, CaseStudyResult, ContactEnquiry
from .security import generate_jwt_token
import json

class WellnessModelTestCase(TestCase):
    """
    Test cases for database models in the app, verifying slugify save logic and string representation.
    """
    def test_category_slugify_and_str(self):
        category = Category.objects.create(name="Authentic Ayurvedic Herbs", description="Traditional herbs description.")
        self.assertEqual(category.slug, "authentic-ayurvedic-herbs")
        self.assertEqual(str(category), "Authentic Ayurvedic Herbs")

    def test_product_slugify_and_str(self):
        category = Category.objects.create(name="Wellness")
        product = Product.objects.create(
            category=category,
            title="Premium Ashwagandha Powder",
            description="Pure ashwagandha.",
            regular_price=24.99
        )
        self.assertEqual(product.slug, "premium-ashwagandha-powder")
        self.assertEqual(str(product), "Premium Ashwagandha Powder")

    def test_case_study_result_str(self):
        study = CaseStudyResult.objects.create(
            patient_name="Ramesh Kumar",
            condition_treated="Chronic Joint Pain",
            improvement_percentage=95,
            duration_weeks=6,
            testimonial="Highly effective wellness products."
        )
        self.assertEqual(str(study), "Ramesh Kumar - Chronic Joint Pain")

    def test_contact_enquiry_str(self):
        enquiry = ContactEnquiry.objects.create(
            full_name="Amit Patel",
            email="amit@example.com",
            subject="Wholesale Franchise Enquiry",
            message="Looking to distribute organic botanical products."
        )
        self.assertEqual(str(enquiry), "Amit Patel - Wholesale Franchise Enquiry")


class PublicViewTestCase(TestCase):
    """
    Test cases for verifying that all public pages return successfully.
    """
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Ayurveda")
        self.product = Product.objects.create(
            category=self.category,
            title="Divya Sanjeevni Herb",
            description="Test product.",
            regular_price=10.00
        )
        self.study = CaseStudyResult.objects.create(
            patient_name="Test Patient",
            condition_treated="Digestive Disorder",
            testimonial="Great testimonial."
        )

    def test_public_pages_status_codes(self):
        # 1. Homepage
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/index.html')

        # 2. Products Page
        response = self.client.get(reverse('products'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/products.html')

        # 3. Product Detail Page
        response = self.client.get(reverse('product_detail', kwargs={'slug': self.product.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/product-detail.html')

        # 4. Results Page
        response = self.client.get(reverse('results'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/results.html')

        # 5. Result Detail Page
        response = self.client.get(reverse('result_detail', kwargs={'pk': self.study.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/result-detail.html')

        # 6. Business Page
        response = self.client.get(reverse('business'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/business.html')

        # 7. Contact Page
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/contact.html')

        # 8. Search Page
        response = self.client.get(reverse('search') + '?q=Digestive')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/search.html')


class AuthSecurityTestCase(TestCase):
    """
    Test cases to confirm secure pages and login redirect behavior.
    """
    def setUp(self):
        self.client = Client()

    def test_admin_dashboard_redirects_unauthenticated(self):
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        # Verify redirect to login page
        self.assertIn(reverse('admin_login'), response.url)


class APITestCase(TestCase):
    """
    Test cases for AJAX APIs (contact submissions, JWT authentication, and admin CRUD operations).
    """
    def setUp(self):
        self.client = Client()
        # Admin / Staff User
        self.admin_username = "admin"
        self.admin_password = "secure_admin_password"
        self.admin_user = User.objects.create_user(
            username=self.admin_username,
            password=self.admin_password,
            is_staff=True,
            is_active=True
        )
        self.admin_token = generate_jwt_token(self.admin_user)
        self.admin_headers = {
            'HTTP_AUTHORIZATION': f'Bearer {self.admin_token}'
        }

        # Regular User (Non-staff)
        self.regular_username = "regular"
        self.regular_password = "secure_user_password"
        self.regular_user = User.objects.create_user(
            username=self.regular_username,
            password=self.regular_password,
            is_staff=False,
            is_active=True
        )
        self.regular_token = generate_jwt_token(self.regular_user)
        self.regular_headers = {
            'HTTP_AUTHORIZATION': f'Bearer {self.regular_token}'
        }

        # Seed data
        self.category = Category.objects.create(name="Immunity")
        self.product = Product.objects.create(
            category=self.category,
            title="Immunity Booster",
            description="Fights germs.",
            regular_price=15.00
        )
        self.study = CaseStudyResult.objects.create(
            patient_name="Sita Sharma",
            condition_treated="Low Immunity",
            testimonial="Felt better in a week."
        )
        self.enquiry = ContactEnquiry.objects.create(
            full_name="Aman Gupta",
            email="aman@example.com",
            subject="Franchise Opportunity",
            message="How do I get set up?"
        )

    def test_contact_enquiry_create_api(self):
        # 1. Valid POST
        post_data = {
            'full_name': 'Karan Johar',
            'email': 'karan@example.com',
            'subject': 'Franchise Partner Request',
            'message': 'Interested in distribution franchise.'
        }
        response = self.client.post(reverse('api_contact_create'), data=post_data)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertEqual(response_json['status'], 'success')
        self.assertTrue(ContactEnquiry.objects.filter(full_name='Karan Johar').exists())

        # 2. Invalid POST (missing email)
        invalid_data = {
            'full_name': 'Karan Johar',
            'subject': 'Franchise Partner Request',
            'message': 'Interested in distribution franchise.'
        }
        response = self.client.post(reverse('api_contact_create'), data=invalid_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['status'], 'error')

    def test_jwt_auth_token_api(self):
        # 1. Valid credentials
        auth_data = {
            'username': self.admin_username,
            'password': self.admin_password
        }
        response = self.client.post(
            reverse('api_jwt_token'),
            data=json.dumps(auth_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json())

        # 2. Invalid credentials
        bad_auth_data = {
            'username': self.admin_username,
            'password': 'wrong_password'
        }
        response = self.client.post(
            reverse('api_jwt_token'),
            data=json.dumps(bad_auth_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['status'], 'error')

    def test_admin_categories_crud_api(self):
        # 1. Get Categories - Authorized
        response = self.client.get(reverse('api_admin_categories'), **self.admin_headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('categories', response.json())

        # 2. Create Category - Authorized
        cat_data = {
            'name': 'Mental Wellness',
            'description': 'Calming adaptogens.'
        }
        response = self.client.post(
            reverse('api_admin_categories'),
            data=json.dumps(cat_data),
            content_type='application/json',
            **self.admin_headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertTrue(Category.objects.filter(name='Mental Wellness').exists())

        # 3. Create Category - Unauthorized (Regular user)
        response = self.client.post(
            reverse('api_admin_categories'),
            data=json.dumps(cat_data),
            content_type='application/json',
            **self.regular_headers
        )
        self.assertEqual(response.status_code, 403)

        # 4. Delete Category - Authorized
        new_cat = Category.objects.create(name="Delete Me")
        response = self.client.delete(
            reverse('api_admin_category_detail', kwargs={'category_id': new_cat.id}),
            **self.admin_headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Category.objects.filter(id=new_cat.id).exists())

    def test_admin_products_crud_api(self):
        # 1. Add Product API - Authorized
        # We can test products/add endpoint
        prod_post_data = {
            'category': self.category.id,
            'title': 'New Ayurvedic Pills',
            'regular_price': '29.99',
            'description': 'Product description.'
        }
        response = self.client.post(
            reverse('api_product_add'),
            data=prod_post_data,
            **self.admin_headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertTrue(Product.objects.filter(title='New Ayurvedic Pills').exists())

        # 2. Get Product Detail - Authorized
        response = self.client.get(
            reverse('api_admin_product_detail', kwargs={'product_id': self.product.id}),
            **self.admin_headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], self.product.id)

        # 3. Delete Product - Authorized
        response = self.client.delete(
            reverse('api_admin_product_detail', kwargs={'product_id': self.product.id}),
            **self.admin_headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

    def test_admin_results_crud_api(self):
        # 1. Add Result - Authorized
        result_data = {
            'patient_name': 'Geeta Devi',
            'condition_treated': 'Insomnia',
            'improvement_percentage': 90,
            'duration_weeks': 4,
            'testimonial': 'Slept peacefully.',
            'associated_product': self.product.id
        }
        response = self.client.post(
            reverse('api_case_study_create'),
            data=result_data,
            **self.admin_headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

        # 2. Get Result Detail - Authorized
        response = self.client.get(
            reverse('api_admin_result_detail', kwargs={'result_id': self.study.id}),
            **self.admin_headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], self.study.id)

        # 3. Delete Result - Authorized
        response = self.client.delete(
            reverse('api_admin_result_detail', kwargs={'result_id': self.study.id}),
            **self.admin_headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(CaseStudyResult.objects.filter(id=self.study.id).exists())

    def test_admin_enquiries_crud_api(self):
        # 1. List Enquiries - Authorized
        response = self.client.get(
            reverse('api_admin_enquiries_list'),
            **self.admin_headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('enquiries', response.json())

        # 2. Resolve Enquiry - Authorized
        response = self.client.post(
            reverse('api_admin_enquiry_detail', kwargs={'enquiry_id': self.enquiry.id}),
            data=json.dumps({'action': 'resolve'}),
            content_type='application/json',
            **self.admin_headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.enquiry.refresh_from_db()
        self.assertEqual(self.enquiry.status, 'Resolved')

        # 3. Delete Enquiry - Authorized
        response = self.client.delete(
            reverse('api_admin_enquiry_detail', kwargs={'enquiry_id': self.enquiry.id}),
            **self.admin_headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ContactEnquiry.objects.filter(id=self.enquiry.id).exists())
