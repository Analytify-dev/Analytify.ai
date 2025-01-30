import json
from django.core.management.base import BaseCommand
from sample.models import SupplyChain
from django.db import transaction, IntegrityError
from datetime import datetime


class Command(BaseCommand):
    help = 'Import supply chain data from a JSON file into the SupplyChain table'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file')

    def handle(self, *args, **kwargs):
        json_file = kwargs['json_file']

        try:
            with open(json_file, 'r') as file:
                data = json.load(file)

            # Insert records individually to handle duplicates
            with transaction.atomic():
                for item in data['supply_chain']:  # Assuming the supply chain data is inside the "supply_chain" key
                    try:
                        SupplyChain.objects.create(
                            order_id=item['order_id'],
                            order_date=datetime.strptime(item['order_date'], '%Y-%m-%d').date(),
                            supplier_id=item['supplier_id'],
                            supplier_name=item['supplier_name'],
                            product_id=item['product_id'],
                            product_name=item['product_name'],
                            product_category=item['product_category'],
                            quantity_ordered=item['quantity_ordered'],
                            quantity_received=item['quantity_received'],
                            order_status=item['order_status'],
                            lead_time_days=item['lead_time_days'],
                            cost_per_unit=item['cost_per_unit'],
                            total_cost=item['total_cost'],
                            shipping_cost=item['shipping_cost'],
                            warehouse_location=item['warehouse_location'],
                            inventory_level=item['inventory_level'],
                            backorder_status=item['backorder_status'],
                            delivery_date=datetime.strptime(item['delivery_date'], '%Y-%m-%d') if item['delivery_date'] else None,
                            supplier_rating=item['supplier_rating'],
                            order_comments=item.get('order_comments', '')  # Handle empty or missing comments
                        )
                    except IntegrityError:
                        pass
                        # self.stdout.write(
                        #     self.style.WARNING(f"Duplicate entry skipped for order_id: {item['order_id']}")
                        # )

            self.stdout.write(self.style.SUCCESS(
                f"Successfully imported supply chain data from {json_file}"
            ))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File {json_file} not found."))
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(f"File {json_file} is not a valid JSON file."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {str(e)}"))
