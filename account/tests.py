# from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from .models import User, Company, Member , Card
from datetime import date
# Create your tests here.


class TestSetUp(APITestCase):
    def setUp(self):

        self.user_signup_data = {
            "name": "dealermart",
            "email": 'admin@gmail.com',
            'is_admin': False
        }
        self.password = 'admin'

        # create a new user
        self.testUser = User.objects.create(**self.user_signup_data)
        self.testUser.set_password(self.password)
        self.testUser.save()

        # create company
        company_obj = Company()
        company_obj.name='Epochs'
        company_obj.save()
        
        # create member 
        self.member = Member()
        self.member.user = self.testUser
        self.member.company = company_obj
        self.member.user_role = 'admin'
        self.member.save()
        
        
        self.card_data={
            "user": self.testUser,
            'expiration_date': date.today(),
            "masked_number":5587477,
            'limit':1000,
            'purchased_amount':500,
            'current_balance':500
        }
        # create_card
        self.card = Card(**self.card_data)
        self.card.save()
        
        
        self.user_signin_data = {
            "email": 'admin@gmail.com',
            'password': self.password,
        }
    

    
         
    def test_user_login_with_correct_data(self):
        signin_url = reverse('signin')   
        login_res = self.client.post(signin_url, self.user_signin_data)
        self.assertEqual(login_res.status_code, 200)
        self.assertIn('access_token', login_res.data['data'])
        self.assertIn('refresh_token', login_res.data['data'])       
       
    def test_user_login_with_wrong_data(self):
        signin_url = reverse('signin')  
        self.user_signin_data['password'] = '123'
        res = self.client.post(signin_url, self.user_signin_data)
        self.assertEqual(res.status_code, 400, msg="Login with wrong data test passed")
        
    def signin_authentication(self):
        signin_url = reverse('signin') 
        login_res = self.client.post(signin_url, self.user_signin_data)
        access_token = "{}".format(login_res.data['data']['access_token'])
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))
        
        
    def test_get_user_detail(self):
        user_detail = reverse('user-detail-view', kwargs={'m_id': self.member.id, 'id': self.testUser.id})
        self.signin_authentication()
        detail_response = self.client.get(user_detail, format='json')
        self.assertEqual(detail_response.status_code, 200)
        
        
    def test_get_user_list(self):
        user_list = reverse('user-list-view', kwargs={'m_id': self.member.id})
        self.signin_authentication()
        list_response = self.client.get(user_list, format='json')
        self.assertEqual(list_response.status_code, 200)
        
    def test_create_card(self):
        self.card.delete()
        self.signin_authentication()
        card_url = reverse('card-list-view', kwargs={'m_id': self.member.id})
        card_response = self.client.post(card_url, data=self.card_data)
        # obj = Card.objects.get(id = card_response.data['id'])
        self.assertEqual(card_response.status_code, 200)
        
    def test_get_card(self):
        self.signin_authentication()
        card_list_url = reverse('card-list-view',  kwargs={'m_id': self.member.id})
        card_response = self.client.get(card_list_url, format='json')
        self.assertEqual(card_response.status_code, 200)
        
    def test_get_detail_card(self):
        self.signin_authentication()
        card_detail=reverse('card-detail-view', kwargs={'m_id': self.member.id, 'id': self.card.id})
        card_response_detail = self.client.get(card_detail, format='json')
        self.assertEqual(card_response_detail.status_code, 200)
        
    def test_get_delete_card(self):
        self.signin_authentication()
        card_delete=reverse('card-detail-view', kwargs={'m_id': self.member.id, 'id': self.card.id})
        card_response = self.client.delete(card_delete)
        self.assertEqual(card_response.status_code, 204)
        
    def test_update_cards(self):
        self.signin_authentication()
        self.card_data['limit']=1000
        self.card_data["user"]=self.testUser.id
    
        card_update = reverse('card-detail-view', kwargs={'m_id': self.member.id, 'id': self.card.id})
        card_response = self.client.put(card_update, data=self.card_data)
        print(card_response.data)
        self.assertEqual(card_response.status_code, 200)
        self.assertEqual(card_response.data['limit'],self.card_data['limit'])
        self.assertEqual(self.card.id,card_response.data['id'])