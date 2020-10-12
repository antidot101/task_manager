from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Task
from datetime import datetime as dt


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
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertEqual(get_user_model().objects.get().username, self.user_correct['username'])

    def test_create_user_already_exist(self):
        self.register_user(data=self.user_correct)
        response = self.register_user(data=self.user_correct)
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_invalid(self):
        responses = [
            self.register_user(data=self.user_incorrect),
            self.register_user(data=None),
            self.register_user(data=self.user_blank)
        ]
        for response in responses:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(get_user_model().objects.count(), 0)


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
    tasks_url = reverse('tasks')

    task_correct = {
        "task_name": "Preparing presentation",
        "description": "To collect materials from departments ...",
        "status": "New",
        "completion_date": "2020-11-10T10:00"
    }
    task_upd_correct = {
        "task_name": "To pay taxes",
        "description": "Make an upload from 1C for the reporting period",
        "status": "Planned",
        "completion_date": "2020-11-15T12:30"
    }

    # preparing incorrect test data
    tasks_incorrect = []
    for k in task_correct.keys():
        task_blank_field = task_correct.copy()
        task_blank_field[k] = " "
        tasks_incorrect.append(task_blank_field)

    task_length_invalid_1 = task_correct.copy()
    task_length_invalid_1['task_name'] = 151*'t'
    task_length_invalid_2 = task_correct.copy()
    task_length_invalid_2['description'] = 1001*'t'
    task_status_invalid = task_correct.copy()
    task_status_invalid['status'] = 'Another status'
    task_date_invalid_1 = task_correct.copy()
    task_date_invalid_1['completion_date'] = "2020-13-10T17:24"
    task_date_invalid_2 = task_correct.copy()
    task_date_invalid_2['completion_date'] = dt.now().isoformat()

    tasks_incorrect.extend([task_length_invalid_1, task_length_invalid_2, task_status_invalid,
                            task_date_invalid_1, task_date_invalid_2])

    def setUp(self):
        user = {'username': 'Billy-Jean', 'password': 'barbstraisand%@#'}
        self.client.post(self.registration_url, data=user)
        response = self.client.post(self.get_token_url, data=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['token'])

    def test_tasks_list_authenticated(self):
        response = self.client.get(self.tasks_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tasks_list_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.tasks_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_task_success(self):
        response = self.client.post(self.tasks_url, data=self.task_correct)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Task.objects.get().task_name, self.task_correct['task_name'])

    def test_create_task_invalid(self):
        for task_incorrect in self.tasks_incorrect:
            response = self.client.post(self.tasks_url, data=task_incorrect)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Task.objects.count(), 0)

    def test_retrieve_task(self):
        self.client.post(self.tasks_url, data=self.task_correct)
        response = self.client.get(reverse('task_update', args=[Task.objects.get().id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.objects.get().task_name, self.task_correct['task_name'])

    def test_update_task_success(self):
        self.client.post(self.tasks_url, data=self.task_correct)
        response1 = self.client.put(reverse('task_update', args=[Task.objects.get().id]), data=self.task_correct)
        response2 = self.client.put(reverse('task_update', args=[Task.objects.get().id]), data=self.task_upd_correct)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.objects.get().task_name, self.task_upd_correct['task_name'])

    def test_update_task_invalid(self):
        self.client.post(self.tasks_url, data=self.task_correct)
        for task_incorrect in self.tasks_incorrect:
            response = self.client.put(reverse('task_update', args=[Task.objects.get().id]), data=task_incorrect)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)