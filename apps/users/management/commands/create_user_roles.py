from django.core.management.base import BaseCommand
from apps.users.models import UserRole

class Command(BaseCommand):
    help = 'Create default UserRole objects for SuperAdmin, Admin, and User'

    def handle(self, *args, **options):
        default_roles = [
            {'role_code': 'SuperAdmin', 'role_name': 'SuperAdmin'},
            {'role_code': 'Admin', 'role_name': 'Admin'},
            {'role_code': 'User', 'role_name': 'User'},
        ]

        for role in default_roles:
            if not UserRole.objects.filter(role_name=role['role_name']).exists():
                UserRole.objects.create(role_code=role['role_code'], role_name=role['role_name'])
                self.stdout.write(self.style.SUCCESS(f"Created role: {role['role_name']}"))
            else:
                self.stdout.write(f"Role already exists: {role['role_name']}")

        self.stdout.write(self.style.SUCCESS(" All default roles checked/created."))
