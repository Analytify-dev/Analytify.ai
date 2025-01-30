import json
from django.core.management.base import BaseCommand
from sample.models import CovidData
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

                # Access the array inside "covid_data"
                covid_data = data.get('covid_data', [])

                if not isinstance(covid_data, list):
                    raise ValueError('"covid_data" key must contain a list.')

                # Insert records individually, handling duplicates
                with transaction.atomic():
                    for item in covid_data:
                        try:
                            CovidData.objects.create(
                                country=item['country'],
                                continent=item['continent'],
                                population=parse_value(item['population']),
                                total_cases=parse_value(item['total_cases']),
                                new_cases=parse_value(item.get('new_cases', None)),
                                total_deaths=parse_value(item['total_deaths']),
                                new_deaths=parse_value(item.get('new_deaths', None)),
                                total_recovered=parse_value(item.get('total_recovered', None)),
                                new_recovered=parse_value(item.get('new_recovered', None)),
                                active_cases=parse_value(item.get('active_cases', None)),
                                serious=parse_value(item.get('serious', None)),
                                total_cases_per_million=parse_value(item.get('Tot cases/1M pop', None)),
                                deaths_per_million=parse_value(item.get('Deaths/1M pop', None)),
                                total_tests=parse_value(item.get('total_tests', None)),
                                tests_per_million=parse_value(item.get('Tests/1M pop', None)),
                                who_region=item['WHO region']
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
