from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from accounts.models import User, UserStatus

class Command(BaseCommand):
    help = "Permanently delete users deactivated for more than 30 days."

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=User.SOFT_DELETE_WINDOW_DAYS)
        qs = User.objects.filter(status=UserStatus.DEACTIVATED, deactivated_at__lt=cutoff)
        count = qs.count()
        qs.delete()
        self.stdout.write(self.style.SUCCESS(f"Purged {count} user(s)."))
