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
                # salesforce = data.get('salesforce', [])

                # if not isinstance(salesforce, list):
                #     raise ValueError('"quickbooks_data" key must contain a list.')

                # Insert records individually, handling duplicates
                with transaction.atomic():
                    for item in data:
                        try:
                            models.salesforce.objects.using('example').update_or_create(
                                pr_Id=item['pr_Id'],
                                defaults={
                                    'totalSize': item['totalSize'],
                                    'done': item['done'],
                                    'type': item['type'],
                                    'url': item['url'],
                                    'Username': item['Username'],
                                    'LastName': item['LastName'],
                                    'FirstName': item['FirstName'],
                                    'Name': item['Name'],
                                    'CompanyName': item['CompanyName'],
                                    'Division': item['Division'],
                                    'Department': item['Department'],
                                    'Title': item['Title'],
                                    'Street': item['Street'],
                                    'City': item['City'],
                                    'State': item['State'],
                                    'PostalCode': item['PostalCode'],
                                    'Country': item['Country'],
                                    'Latitude': item['Latitude'],
                                    'Longitude': item['Longitude'],
                                    'GeocodeAccuracy': item['GeocodeAccuracy'],
                                    'Email': item['Email'],
                                    'EmailPreferencesAutoBcc': item['EmailPreferencesAutoBcc'],
                                    'EmailPreferencesAutoBccStayInTouch': item['EmailPreferencesAutoBccStayInTouch'],
                                    'EmailPreferencesStayInTouchReminder': item['EmailPreferencesStayInTouchReminder'],
                                    'SenderEmail': item['SenderEmail'],
                                    'SenderName': item['SenderName'],
                                    'Signature': item['Signature'],
                                    'StayInTouchSubject': item['StayInTouchSubject'],
                                    'StayInTouchSignature': item['StayInTouchSignature'],
                                    'StayInTouchNote': item['StayInTouchNote'],
                                    'Phone': item['Phone'],
                                    'Fax': item['Fax'],
                                    'MobilePhone': item['MobilePhone'],
                                    'Alias': item['Alias'],
                                    'CommunityNickname': item['CommunityNickname'],
                                    'BadgeText': item['BadgeText'],
                                    'IsActive': item['IsActive'],
                                    'TimeZoneSidKey': item['TimeZoneSidKey'],
                                    # 'UserRoleId': item['UserRoleId'],
                                    'LocaleSidKey': item['LocaleSidKey'],
                                    'ReceivesInfoEmails': item['ReceivesInfoEmails'],
                                    'ReceivesAdminInfoEmails': item['ReceivesAdminInfoEmails'],
                                    'EmailEncodingKey': item['EmailEncodingKey'],
                                    'ProfileId': item['ProfileId'],
                                    # 'UserType': item['UserType'],
                                    'LanguageLocaleKey': item['LanguageLocaleKey'],
                                    'EmployeeNumber': item['EmployeeNumber'],
                                    'DelegatedApproverId': item['DelegatedApproverId'],
                                    'ManagerId': item['ManagerId'],
                                    'LastLoginDate': item['LastLoginDate'],
                                    'LastPasswordChangeDate': item['LastPasswordChangeDate'],
                                    'CreatedDate': item['CreatedDate'],
                                    'CreatedById': item['CreatedById'],
                                    'LastModifiedDate': item['LastModifiedDate'],
                                    'LastModifiedById': item['LastModifiedById'],
                                    'SystemModstamp': item['SystemModstamp'],
                                    'NumberOfFailedLogins': item['NumberOfFailedLogins'],
                                    'OfflineTrialExpirationDate': item['OfflineTrialExpirationDate'],
                                    'OfflinePdaTrialExpirationDate': item['OfflinePdaTrialExpirationDate'],
                                    # 'UserPermissionsMarketingUser': item['UserPermissionsMarketingUser'],
                                    # 'UserPermissionsOfflineUser': item['UserPermissionsOfflineUser'],
                                    # 'UserPermissionsCallCenterAutoLogin': item['UserPermissionsCallCenterAutoLogin'],
                                    # 'UserPreferencesActivityRemindersPopup': item['UserPreferencesActivityRemindersPopup'],
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
