# from django.urls import reverse
# from rest_framework import status
#
# from factories import CompanyFactory, UserFactory, PaymentMethodFactory
# from tests.utils import CkcAPITestCase
#
#
# class TestPaymentMethods(CkcAPITestCase):
#
#     def setUp(self):
#         self.test_company = CompanyFactory()
#         self.admin_user = UserFactory(is_staff=True, company=self.test_company)
#         self.payment_method = PaymentMethodFactory()
#         self.client.force_authenticate(self.admin_user)
#
#     def test_add_payment_method_to_company(self):
#         url = reverse('company-detail', kwargs={'pk': self.test_company.pk})
#         data = {
#             'payment_method': self.payment_method.pk,
#         }
#         response = self.client.patch(url, data, format='json')
#         assert response.status_code == status.HTTP_200_OK
#
#         self.test_company.refresh_from_db()
#         assert self.test_company.payment_method == self.payment_method
