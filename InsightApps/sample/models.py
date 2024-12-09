# sample/models.py

from django.db import models

class Employees(models.Model):
    eeid = models.CharField(primary_key=True,max_length=10)  # Employee ID
    full_name = models.CharField(max_length=100)  # Full Name
    job_title = models.CharField(max_length=100)  # Job Title
    department = models.CharField(max_length=50)  # Department
    business_unit = models.CharField(max_length=50)  # Business Unit
    gender = models.CharField(max_length=10)  # Gender
    ethnicity = models.CharField(max_length=50)  # Ethnicity
    age = models.PositiveIntegerField()  # Age
    hire_date = models.DateTimeField()  # Hire Date
    annual_salary = models.DecimalField(max_digits=10, decimal_places=2)  # Annual Salary
    bonus_percentage = models.DecimalField(max_digits=5, decimal_places=2)  # Bonus Percentage
    country = models.CharField(max_length=50)  # Country
    city = models.CharField(max_length=50)  # City

    class Meta:
        db_table = 'employees'
        
class HrAttrition(models.Model):
    age = models.IntegerField()
    attrition = models.CharField(max_length=50)
    business_travel = models.CharField(max_length=50)
    daily_rate = models.IntegerField()
    department = models.CharField(max_length=100)
    distance_from_home = models.IntegerField()
    education = models.IntegerField()
    education_field = models.CharField(max_length=100)
    environment_satisfaction = models.IntegerField()
    gender = models.CharField(max_length=10)
    hourly_rate = models.IntegerField()
    job_involvement = models.IntegerField()
    job_level = models.IntegerField()
    job_role = models.CharField(max_length=100)
    job_satisfaction = models.IntegerField()
    marital_status = models.CharField(max_length=50)
    monthly_income = models.IntegerField()
    monthly_rate = models.IntegerField()
    num_companies_worked = models.IntegerField()
    over18 = models.CharField(max_length=1)
    over_time = models.CharField(max_length=50)
    percent_salary_hike = models.IntegerField()
    performance_rating = models.IntegerField()
    relationship_satisfaction = models.IntegerField()
    standard_hours = models.IntegerField()
    stock_option_level = models.IntegerField()
    total_working_years = models.IntegerField()
    training_times_last_year = models.IntegerField()
    work_life_balance = models.IntegerField()
    years_at_company = models.IntegerField()
    years_in_current_role = models.IntegerField()
    years_since_last_promotion = models.IntegerField()
    years_with_current_manager = models.IntegerField()
    class Meta:
        db_table = 'hr_attrition'


class CovidData(models.Model):
    country = models.CharField(max_length=100)
    continent = models.CharField(max_length=100)
    population = models.BigIntegerField()
    total_cases = models.BigIntegerField()
    new_cases = models.BigIntegerField(null=True, blank=True)
    total_deaths = models.BigIntegerField()
    new_deaths = models.BigIntegerField(null=True, blank=True)
    total_recovered = models.BigIntegerField(null=True, blank=True)
    new_recovered = models.BigIntegerField(null=True, blank=True)
    active_cases = models.BigIntegerField(null=True, blank=True)
    serious = models.BigIntegerField(null=True, blank=True)
    total_cases_per_million = models.FloatField(null=True, blank=True)
    deaths_per_million = models.FloatField(null=True, blank=True)
    total_tests = models.BigIntegerField(null=True, blank=True)
    tests_per_million = models.FloatField(null=True, blank=True)
    who_region = models.CharField(max_length=100)

    class Meta:
            db_table = 'covid_data'

class Sales(models.Model):
    order_number = models.IntegerField()
    quantity_ordered = models.IntegerField()
    price_each = models.FloatField()
    order_line_number = models.IntegerField()
    sales = models.FloatField()
    order_date = models.DateField()
    status = models.CharField(max_length=50)
    month_id = models.IntegerField()
    year_id = models.IntegerField()
    product_line = models.CharField(max_length=100)
    msrp = models.FloatField()
    product_code = models.CharField(max_length=50)
    customer_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    address_1 = models.CharField(max_length=255)
    address_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    territory = models.CharField(max_length=50)
    lastname = models.CharField(max_length=100)
    firstname = models.CharField(max_length=100)
    deal_size = models.CharField(max_length=50)

    class Meta:
            db_table = 'sales'

class SupplyChain(models.Model):
    order_id = models.CharField(max_length=50)
    order_date = models.DateField()
    supplier_id = models.CharField(max_length=50)
    supplier_name = models.CharField(max_length=200)
    product_id = models.CharField(max_length=50)
    product_name = models.CharField(max_length=200)
    product_category = models.CharField(max_length=100)
    quantity_ordered = models.IntegerField()
    quantity_received = models.IntegerField()
    order_status = models.CharField(max_length=50)
    lead_time_days = models.IntegerField()
    cost_per_unit = models.FloatField()
    total_cost = models.FloatField()
    shipping_cost = models.FloatField()
    warehouse_location = models.CharField(max_length=200)
    inventory_level = models.IntegerField()
    backorder_status = models.CharField(max_length=1)
    delivery_date = models.DateField(blank=True, null=True)
    supplier_rating = models.IntegerField()
    order_comments = models.TextField()

    class Meta:
            db_table = 'supply_chain'