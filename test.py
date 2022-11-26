from unittest import TestCase
from base64 import b64encode
import unittest

from main import app, s
from Models import engine
import json

app.testing = True
client = app.test_client()


class BaseTestCase(TestCase):
    client = app.test_client()

    def setUp(self):
        super().setUp()

        self.admin_data = {
            "TeacherId": "new_teacher",
            "Firstname": "Alex",
            "Surname": "John",
            "Password": "qwerty",
            "SubjectId": 1
        }

        self.wrong_admin_data = {
            "TeacherId": 23,
            "Firstname": "Alex",
            "Surname": "John",
            "Password": "qwerty",
            "SubjectId": "smth"
        }

        self.user_data = {
            "StudentId": "new_student",
            "Firstname": "Ann",
            "Surname": "Ganusia",
            "Password": "qwerty",
            "GroupId": 216
        }

        self.wrong_user_data = {
            "StudentId": "new_student",
            "Firstname": "Ann",
            "Surname": "Ganusia",
            "Password": "qwerty",
            "GroupId": "smth"
        }

        self.mark_data = {
            "MarkId": 7,
            "StudentId": "Alaska",
            "SubjectId": 1,
            "TeacherId": "petroPu",
            "Date": "2022-10-01",
            "Value": 4.5
        }

        self.admin_auth = b64encode(b"petroPu:qwerty").decode('utf-8')
        self.admin_wrong_auth = b64encode(b"petroPukach:qwerty").decode('utf-8')

        self.user_auth = b64encode(b"Alaska:qwerty1234").decode('utf-8')
        self.user2 = b64encode(b"KINEC:PochemRuberoid").decode('utf-8')
        self.user_wrong_auth = b64encode(b"Alaksa:qwerty1234").decode('utf-8')

        self.another_admin_auth = b64encode(b"bogdanPahalok:qwerty").decode('utf-8')
        self.new_admin_auth = b64encode(b"new_teacher:qwerty").decode('utf-8')

    def tearDown(self):
        self.close_session()

    def close_session(self):
        s.close()

    def create_app(self):
        app.config['TESTING'] = True
        return app

    def get_auth_headers(self, credentials):
        return {"Authorization": f"Basic {credentials}"}


class TestUser(BaseTestCase):
    def test_get_student(self):
        response = self.client.get('/student/Alaska',
                                   headers=self.get_auth_headers(self.user_auth))
        self.assertEqual(response.status_code, 200)

    def test_get_student_marks(self):
        response = self.client.get('/students/KINEC',
                                   headers=self.get_auth_headers(self.user2))
        self.assertEqual(response.status_code, 200)

    def test_get_student_marks_by_subject(self):
        response = self.client.get('/students/1/KINEC',
                                   headers=self.get_auth_headers(self.user2))
        self.assertEqual(response.status_code, 200)

    def test_get_teachers(self):
        response = self.client.get('/teachers')
        self.assertEqual(response.status_code, 200)

    def test_get_teachers_by_subject(self):
        response = self.client.get('/teachers/1')
        self.assertEqual(response.status_code, 200)

    def test_get_teacher_by_id(self):
        response = self.client.get('/teachers/petroPu')
        self.assertEqual(response.status_code, 200)

    def test_create_mark(self):
        response = self.client.post('/teacher', json=self.mark_data,
                                    headers=self.get_auth_headers(self.admin_auth))
        self.assertEqual(response.status_code, 200)

    def test_update_mark(self):
        response = self.client.put('/teacher/KINEC/1', data=json.dumps({
            "MarkId": 1,
            "StudentId": "KINEC",
            "SubjectId": 1,
            "TeacherId": "petroPu",
            "Date": "2022-10-01",
            "Value": 10
        }), content_type='application/json', headers=self.get_auth_headers(self.admin_auth))
        self.assertEqual(response.status_code, 200)

    def test_delete_mark(self):
        response = self.client.delete('/teacher/Alaska/7/petroPu',
                                      headers=self.get_auth_headers(self.admin_auth))
        self.assertEqual(response.status_code, 200)

    def test_create_student(self):
        response = self.client.post('/groups', json=self.user_data,
                                    headers=self.get_auth_headers(self.admin_auth))
        self.assertEqual(response.status_code, 200)

    def test_update_student(self):
        response = self.client.put('/student/Alaska', data=json.dumps({
            "StudentId": "Alaska",
            "Firstname": "Kornelia",
            "Surname": "Drozd",
            "Password": "qwerty1234",
            "GroupId": 216
        }), content_type='application/json', headers=self.get_auth_headers(self.user_auth))
        self.assertEqual(response.status_code, 200)

    def test_delete_student(self):
        response = self.client.delete('/student/new_student',
                                      headers=self.get_auth_headers(self.admin_auth))
        self.assertEqual(response.status_code, 200)

    def test_create_teacher(self):
        response = self.client.post('/teachers', json=self.admin_data,
                                    headers=self.get_auth_headers(self.admin_auth))
        self.assertEqual(response.status_code, 200)

    def test_update_teacher(self):
        response = self.client.put('/teachers/petroPu', data=json.dumps({
            "TeacherId": "petroPu",
            "Firstname": "Petro",
            "Surname": "John",
            "Password": "qwerty",
            "SubjectId": 1
        }), content_type='application/json', headers=self.get_auth_headers(self.admin_auth))
        self.assertEqual(response.status_code, 200)

    def test_delete_teacher(self):
        response = self.client.delete('/teachers/new_teacher',
                                      headers=self.get_auth_headers(self.new_admin_auth))
        self.assertEqual(response.status_code, 200)

    def test_get_student_wrong(self):
        response = self.client.get('/student/KINEC',
                                   headers=self.get_auth_headers(self.admin_auth))
        self.assertEqual(response.status_code, 403)

    def test_wrong_auth_update_teacher(self):
        response = self.client.put('/teachers/bogdanPahalok', data=json.dumps({
            "TeacherId": "bogdanPahalok",
            "Firstname": "Bogdan",
            "Surname": "John",
            "Password": "qwerty",
            "SubjectId": 1
        }), content_type='application/json', headers=self.get_auth_headers(self.user_auth))
        self.assertEqual(response.status_code, 403)

    def test_unauthorized_update_teacher(self):
        response = self.client.put('/teachers/bogdanPahalok', json={
            "TeacherId": "bogdanPahalok",
            "Firstname": "Bogdan",
            "Surname": "John",
            "Password": "qwerty",
            "SubjectId": 1
        })
        self.assertEqual(response.status_code, 401)

    def test_wrong_auth_delete_teacher(self):
        response = self.client.delete('/teachers/new_teacher',
                                      headers=self.get_auth_headers(self.user_auth))
        self.assertEqual(response.status_code, 403)

    def test_wrong_auth_create_student(self):
        response = self.client.post('/groups', json=self.user_data,
                                    headers=self.get_auth_headers(self.user_auth))
        self.assertEqual(response.status_code, 403)

    def test_unauthorized_update_student(self):
        response = self.client.put('/student/Alaska', json={
            "StudentId": "Alaska",
            "Firstname": "Kornelia",
            "Surname": "Drozd",
            "Password": "qwerty1234",
        })
        self.assertEqual(response.status_code, 401)

    def test_get_wrong_student_marks(self):
        response = self.client.get('/students/KINEC',
                                   headers=self.get_auth_headers(self.admin_auth))
        self.assertEqual(response.status_code, 403)

    def test_get_wrong_student_marks_by_subject(self):
        response = self.client.get('/students/1/KINEC',
                                   headers=self.get_auth_headers(self.admin_auth))
        self.assertEqual(response.status_code, 403)

    def test_wrong_auth_update_mark(self):
        response = self.client.put('/teacher/KINEC/1'
                                   , data=json.dumps({
                "MarkId": 1,
                "StudentId": "KINEC",
                "SubjectId": 1,
                "TeacherId": "petroPu",
                "Date": "2022-10-01",
                "Value": 10
            }), content_type='application/json', headers=self.get_auth_headers(self.user_auth))
        self.assertEqual(response.status_code, 403)

    def test_wrong_auth2_delete_mark(self):
        response = self.client.delete('/teacher/Alaska/4/petroPu',
                                      headers=self.get_auth_headers(self.user_auth))
        self.assertEqual(response.status_code, 403)

    def test_wrong_auth1_delete_mark(self):
        response = self.client.delete('/teacher/Alaska/4/petroPu',
                                      headers=self.get_auth_headers(self.another_admin_auth))
        self.assertEqual(response.status_code, 401)

    def test_wrong_auth_1_create_mark(self):
        response = self.client.post('/teacher', json=self.mark_data,
                                    headers=self.get_auth_headers(self.another_admin_auth))
        self.assertEqual(response.status_code, 401)

    def test_wrong_update_mark(self):
        response = self.client.put('/teacher/KINEC/1', data=json.dumps({
            "MarkId": 1,
            "StudentId": "KINEC",
            "SubjectId": 1,
            "TeacherId": "petroPu",
            "Date": "2022-10-01",
            "Value": "smth"
        }), content_type='application/json', headers=self.get_auth_headers(self.admin_auth))
        self.assertEqual(response.status_code, 400)

    def test_get_wrong_auth_student(self):
        response = self.client.get('/student/Alaska',
                                   headers=self.get_auth_headers(self.user_wrong_auth))
        self.assertEqual(response.status_code, 401)

    def test_get_wrong_auth_student_marks(self):
        response = self.client.get('/students/Alaska',
                                   headers=self.get_auth_headers(self.user_wrong_auth))
        self.assertEqual(response.status_code, 401)

    def test_wrong_create_teacher(self):
        response = self.client.post('/teachers', json=self.admin_data,
                                    headers=self.get_auth_headers(self.user_auth))
        self.assertEqual(response.status_code, 403)












