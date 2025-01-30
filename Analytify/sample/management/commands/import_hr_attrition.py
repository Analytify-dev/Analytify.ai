import json
from django.core.management.base import BaseCommand
from sample.models import HrAttrition
from django.db import transaction, IntegrityError

class Command(BaseCommand):
    help = 'Import HR Attrition data from a JSON file into the HR Attrition table'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file')

    def handle(self, *args, **kwargs):
        json_file = kwargs['json_file']

        try:
            with open(json_file, 'r') as file:
                data = json.load(file)

            # Insert records individually, handling duplicates
            with transaction.atomic():
                for item in data:
                    try:
                        HrAttrition.objects.create(
                            age=item['age'],
                            attrition=item['attrition'],
                            business_travel=item['business_travel'],
                            daily_rate=item['daily_rate'],
                            department=item['department'],
                            distance_from_home=item['distance_from_home'],
                            education=item['education'],
                            education_field=item['education_field'],
                            environment_satisfaction=item['environment_satisfaction'],
                            gender=item['gender'],
                            hourly_rate=item['hourlyrate'],
                            job_involvement=item['job_involvement'],
                            job_level=item['job_level'],
                            job_role=item['job_role'],
                            job_satisfaction=item['job_satisfaction'],
                            marital_status=item['marital_status'],
                            monthly_income=item['monthly_income'],
                            monthly_rate=item['monthly_rate'],
                            num_companies_worked=item['num_companies_worked'],
                            over18=item['over18'],
                            over_time=item['over_time'],
                            percent_salary_hike=item['percent_salary_hike'],
                            performance_rating=item['performance_rating'],
                            relationship_satisfaction=item['relationship_satisfaction'],
                            standard_hours=item['standard_hours'],
                            stock_option_level=item['stock_option_level'],
                            total_working_years=item['total_working_years'],
                            training_times_last_year=item['training_times_last_year'],
                            work_life_balance=item['work_life_balance'],
                            years_at_company=item['years_at_company'],
                            years_in_current_role=item['years_in_current_role'],
                            years_since_last_promotion=item['years_since_last_promotion'],
                            years_with_current_manager=item['years_with_current_manager']
                        )
                    except IntegrityError:
                        pass
                        # self.stdout.write(
                        #     self.style.WARNING(f"Duplicate entry skipped for record with age: {item['age']}")
                        # )

            self.stdout.write(self.style.SUCCESS(f"Successfully imported data from {json_file}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Import failed: {str(e)}"))
