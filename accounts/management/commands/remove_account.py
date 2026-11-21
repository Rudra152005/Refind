from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = 'Remove specified user account(s) by email address'

    def add_arguments(self, parser):
        parser.add_argument(
            'emails',
            nargs='*',
            default=['www.rudra152005@gmail.com', 'rudratiwari152005@gmail.com'],
            help='Email addresses of the users to remove'
        )

    def handle(self, *args, **options):
        emails = options['emails']
        qs = User.objects.filter(email__in=emails)
        count = qs.count()
        if count == 0:
            self.stdout.write(self.style.WARNING(f"No user found matching: {', '.join(emails)}"))
            return

        deleted_emails = list(qs.values_list('email', flat=True))
        deleted_count, details = qs.delete()
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully removed {deleted_count} record(s) for email(s): {', '.join(deleted_emails)}"
            )
        )
