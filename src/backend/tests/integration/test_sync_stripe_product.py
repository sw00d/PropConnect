from unittest.mock import patch, Mock

from commands.management.commands.generate_data import sync_stripe_products
from stripe_features.models import Product, Price
from tests.utils import CkcAPITestCase


class SyncStripeProductTestCase(CkcAPITestCase):

    @patch('commands.management.commands.generate_data.stripe.Product.list')
    @patch('commands.management.commands.generate_data.stripe.Price.list')
    def test_sync_stripe_products(self, mock_price_list, mock_product_list):
        # Sample mock data
        mock_products = [
            Mock(id="prod_1", name="Product A", active=True),
            Mock(id="prod_2", name="Product B", active=True)
        ]
        # Set the attributes directly
        mock_products[0].name = "Product A"
        mock_products[1].name = "Product B"

        mock_product_list.return_value = mock_products

        mock_price_list.side_effect = [
            [Mock(id="price_1", product="prod_1", unit_amount=1000, currency="usd", recurring=True)],
            [Mock(id="price_2", product="prod_2", unit_amount=2000, currency="usd", recurring=False)]
        ]

        # Call the function
        sync_stripe_products()

        # Validate Products
        self.assertTrue(Product.objects.filter(stripe_product_id="prod_1", name="Product A", active=True).exists())
        self.assertTrue(Product.objects.filter(stripe_product_id="prod_2", name="Product B", active=True).exists())

        # Validate Prices
        self.assertTrue(
            Price.objects.filter(stripe_price_id="price_1", product__stripe_product_id="prod_1", unit_amount=1000,
                                 currency="usd", recurring=True).exists())
        self.assertTrue(
            Price.objects.filter(stripe_price_id="price_2", product__stripe_product_id="prod_2", unit_amount=2000,
                                 currency="usd", recurring=False).exists())
