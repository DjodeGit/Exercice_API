from django.test import TestCase

# Create your tests here.
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

class TestCategoryAPI(APITestCase):
    def setUp(self):
        # Créer un utilisateur pour les tests d'auth
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        # Endpoint pour la liste des catégories
        self.list_url = reverse('category-list')  # 'category-list' vient du router DRF
        # Créer une catégorie de test
        self.category = Category.objects.create(name='Test Category', description='Description test')

    def test_get_categories_unauthenticated(self):
        # Test liste sans auth : doit échouer (403 Forbidden)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_categories_authenticated(self):
        # Simuler une session authentifiée
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Une catégorie créée dans setUp

    def test_create_category(self):
        self.client.force_authenticate(user=self.user)
        data = {'name': 'New Category', 'description': 'New desc'}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)  # Une existante + une nouvelle

    def test_update_category(self):
        self.client.force_authenticate(user=self.user)
        detail_url = reverse('category-detail', kwargs={'pk': self.category.pk})
        data = {'name': 'Updated Category', 'description': 'Updated desc'}
        response = self.client.put(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Updated Category')

    def test_delete_category(self):
        self.client.force_authenticate(user=self.user)
        detail_url = reverse('category-detail', kwargs={'pk': self.category.pk})
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 0)

class TestProductAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product', quantity=10, price=99.99, 
            description='Test desc', category=self.category
        )
        self.list_url = reverse('product-list')

    def test_get_products_unauthenticated(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_products_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_product(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'New Product', 'quantity': 5, 'price': 49.99, 
            'description': 'New desc', 'category': self.category.pk
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)

    def test_update_product(self):
        self.client.force_authenticate(user=self.user)
        detail_url = reverse('product-detail', kwargs={'pk': self.product.pk})
        data = {'name': 'Updated Product', 'quantity': 20, 'price': 199.99, 'description': 'Updated', 'category': self.category.pk}
        response = self.client.put(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Updated Product')

    def test_delete_product(self):
        self.client.force_authenticate(user=self.user)
        detail_url = reverse('product-detail', kwargs={'pk': self.product.pk})
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)

class TestSerializers(APITestCase):
    def test_category_serializer(self):
        category = Category(name='Test')
        serializer = CategorySerializer(category)
        self.assertEqual(serializer.data['name'], 'Test')