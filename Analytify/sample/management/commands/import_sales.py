import json
from django.core.management.base import BaseCommand
from sample.models import Sales
from django.db import transaction, IntegrityError
from datetime import datetime


class Command(BaseCommand):
    help = 'Import sales data from a JSON file into the Sales table'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file')

    def handle(self, *args, **kwargs):
        json_file = kwargs['json_file']

        try:
            with open(json_file, 'r') as file:
                data = json.load(file)

            # Insert records individually to handle duplicates
            with transaction.atomic():
                for item in data['sales']:  # Assuming the sales data is inside the "sales" key
                    try:
                        Sales.objects.create(
                            order_number=item['order_number'],
                            quantity_ordered=item['quantity_ordered'],
                            price_each=item['price_each'],
                            order_line_number=item['order_line_number'],
                            sales=item['sales'],
                            order_date=datetime.strptime(item['order_Date'], '%Y-%m-%d').date(),
                            status=item['status'],
                            month_id=item['month_id'],
                            year_id=item['Year_id'],
                            product_line=item['product_line'],
                            msrp=item['MSRP'],
                            product_code=item['product_code'],
                            customer_name=item['customer_name'],
                            phone_number=item['phone_number'],
                            address_1=item['address_1'],
                            address_2=item.get('address_2', ''),  # Handle empty address_2
                            city=item['City'],
                            state=item['state'],
                            postal_code=item['postal_code'],
                            country=item['country'],
                            territory=item['Territory'],
                            lastname=item['lastname'],
                            firstname=item['firstname'],
                            deal_size=item['deal_size']
                        )
                    except IntegrityError:
                        pass
                        # self.stdout.write(
                        #     self.style.WARNING(f"Duplicate entry skipped for order_number: {item['order_number']}")
                        # )

            self.stdout.write(self.style.SUCCESS(
                f"Successfully imported sales data from {json_file}"
            ))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File {json_file} not found."))
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(f"File {json_file} is not a valid JSON file."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {str(e)}"))
