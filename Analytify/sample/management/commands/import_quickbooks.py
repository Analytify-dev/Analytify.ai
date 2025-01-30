import json
from django.core.management.base import BaseCommand
from sample import models
from django.db import transaction, IntegrityError

class Command(BaseCommand):
    help = 'Import country-level statistics from a JSON file into the CovidData table'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file')

    def handle(self, *args, **kwargs):
        json_file = kwargs['json_file']

        def parse_value(value):
            """Convert 'NULL' or invalid values to None, leave valid values unchanged."""
            if value == "NULL" or value is None:
                return None
            try:
                return float(value) if '.' in str(value) else int(value)
            except ValueError:
                return None

        try:
            with open(json_file, 'r') as file:
                # Load the JSON file
                data = json.load(file)

                # # Access the array inside "covid_data"
                # quickbooks = data.get('quickbooks', [])

                # if not isinstance(quickbooks, list):
                #     raise ValueError('"quickbooks" key must contain a list.')

                # Insert records individually, handling duplicates
                with transaction.atomic():
                    for item in data:
                        try:
                            models.quickbooks.objects.using('example').update_or_create(
                                pr_Id=item['pr_Id'],
                                defaults={
                                    'Taxable': item['Taxable'],
                                    'Job': item['Job'],
                                    'BillWithParent': item['BillWithParent'],
                                    'Balance': item['Balance'],
                                    'BalanceWithJobs': item['BalanceWithJobs'],
                                    'value': item['value'],
                                    'name': item['name'],
                                    'PreferredDeliveryMethod': item['PreferredDeliveryMethod'],
                                    'IsProject': item['IsProject'],
                                    'ClientEntityId': item['ClientEntityId'],
                                    'domain': item['domain'],
                                    'sparse': item['sparse'],
                                    'SyncToken': item['SyncToken'],
                                    'CreateTime': item['CreateTime'],
                                    'LastUpdatedTime': item['LastUpdatedTime'],
                                    'FullyQualifiedName': item['FullyQualifiedName'],
                                    'DisplayName': item['DisplayName'],
                                    'PrintOnCheckName': item['PrintOnCheckName'],
                                    'Active': item['Active'],
                                    'V4IDPseudonym': item['V4IDPseudonym'],
                                    'Address': item['Address'],
                                    'Line1': item['Line1'],
                                    'City': item['City'],
                                    'Country': item['Country'],
                                    'CountrySubDivisionCode': item['CountrySubDivisionCode'],
                                    'PostalCode': item['PostalCode'],
                                    'Notes': item['Notes'],
                                    'Title': item['Title'],
                                    'GivenName': item['GivenName'],
                                    'MiddleName': item['MiddleName'],
                                    'FamilyName': item['FamilyName'],
                                    'Suffix': item['Suffix'],
                                    'CompanyName': item['CompanyName'],
                                    'FreeFormNumber': item['FreeFormNumber'],
                                    'Lat': item['Lat'],
                                    'Long': item['Long'],
                                    'URI': item['URI'],
                                    'Level': item['Level'],
                                    'startPosition': item['startPosition'],
                                    'maxResults': item['maxResults'],
                                    'time': item['time']
                                }
                            )
                        except IntegrityError:
                            pass
                            # self.stdout.write(
                            #     self.style.WARNING(f"Duplicate entry skipped")
                            # )

                self.stdout.write(self.style.SUCCESS(
                    f"Successfully imported data from {json_file}"
                ))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File {json_file} not found."))
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(f"File {json_file} is not a valid JSON file."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {str(e)}"))
