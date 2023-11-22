from django.test import TestCase

# Create your tests here.
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import User

class RegisterUserTestCase(APITestCase):
    def test_register_new_user(self):
        url = reverse('register_user')
        data = {'name': 'Test User', 'email': 'test@example.com', 'password': 'testpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('status' in response.data)
        self.assertEqual(response.data['status'], True)
        self.assertTrue('data' in response.data)

    def test_register_existing_user(self):
        existing_user = User.objects.create(name='existing', email='existing@example.com', password='existingpassword')
        url = reverse('register_user')
        data = {'name': 'Existing User', 'email': 'existing@example.com', 'password': 'existingpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertTrue('status' in response.data)
        self.assertEqual(response.data['status'], False)
        self.assertTrue('error' in response.data)

# Similarly, create test cases for login_user and get_user_profile endpoints

class LoginUserTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(name='testuser', email='test@example.com', password='testpassword')

    def test_login_user_success(self):
        url = reverse('login_user')
        data = {'email': 'test@example.com', 'password': 'testpassword'}
        response = self.client.post(url, data, format='json')
        print("response",response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('status' in response.data)
        self.assertEqual(response.data['status'], True)
        self.assertTrue('token' in response.data)

    def test_login_user_incorrect_password(self):
        url = reverse('login_user')
        data = {'email': 'test@example.com', 'password': 'incorrectpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue('status' in response.data)
        self.assertEqual(response.data['status'], False)
        self.assertTrue('error' in response.data)

# Test cases for get_user_profile can include scenarios for authorized and unauthorized access

class GetUserProfileTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(name='testuser', email='test@example.com', password='testpassword')
        self.client.credentials(HTTP_AUTH_TOKEN='validtoken')

    def test_get_user_profile_success(self):
        url = reverse('get_user_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('status' in response.data)
        self.assertEqual(response.data['status'], True)
        self.assertTrue('data' in response.data)

    def test_get_user_profile_unauthorized(self):
        self.client.credentials()  # Clear credentials to simulate unauthorized access
        url = reverse('get_user_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue('error' in response.data)
        self.assertEqual(response.data['status'], False)

