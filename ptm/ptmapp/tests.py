from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User


class UserTestCase(APITestCase):
    registration_url = reverse('registration')
    user_correct = {'username': 'Billy-Jean', 'password': 'barbstraisand%@#'}
    user_incorrect = {'username': 'Billy-Jean', 'password': '123456'}
    user_blank = {'username': '', 'password': '123456'}

    def register_user(self, data):
        return self.client.post(self.registration_url, data=data)

    def test_create_user_success(self):
        response = self.register_user(data=self.user_correct)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'Billy-Jean')

    def test_create_user_already_exist(self):
        self.register_user(data=self.user_correct)
        response = self.register_user(data=self.user_correct)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_create_user_invalid(self):
        response1 = self.register_user(data=self.user_incorrect)
        response2 = self.register_user(data=None)
        response3 = self.register_user(data=self.user_blank)
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response3.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)


class AuthTokenTestCase(APITestCase):
    registration_url = reverse('registration')
    get_token_url = reverse('get_token')
    user_correct = {'username': 'Billy-Jean', 'password': 'barbstraisand%@#'}
    user_incorrect = {'username': 'Michael Jackson', 'password': 'barbstraisand%@#'}

    def setUp(self):
        self.client.post(self.registration_url, data=self.user_correct)

    def test_get_token_success(self):
        response = self.client.post(self.get_token_url, data=self.user_correct)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_token_incorrect_data(self):
        response1 = self.client.post(self.get_token_url, data=None)
        response2 = self.client.post(self.get_token_url, data=self.user_incorrect)
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)


class TaskTestCase(APITestCase):
    registration_url = reverse('registration')
    get_token_url = reverse('get_token')
    tasks = reverse('tasks')

    def setUp(self):
        user = {'username': 'Billy-Jean', 'password': 'barbstraisand%@#'}
        self.client.post(self.registration_url, data=user)
        response = self.client.post(self.get_token_url, data=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['token'])

    def test_tasks_list_authenticated(self):
        response = self.client.get(self.tasks)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tasks_list_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.tasks)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
