import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.core.template_interpolator import interpolate_template


class TestTemplateInterpolator(unittest.TestCase):
    def test_interpolates_flat_and_nested_variables(self):
        template = "Hello {{ user.name }}, your order #{{ order.id }} has shipped!"
        context = {
            'user': {'name': 'Lakshya'},
            'order': {'id': 'ORD-9871'},
        }
        res = interpolate_template(template, context)
        self.assertEqual(res, "Hello Lakshya, your order #ORD-9871 has shipped!")

    def test_uses_fallback_value_when_missing(self):
        template = "Welcome {{ user.name | Valued Shopper }}, get {{ discount | 10% }} off."
        res = interpolate_template(template, {})
        self.assertEqual(res, "Welcome Valued Shopper, get 10% off.")


if __name__ == '__main__':
    unittest.main()
