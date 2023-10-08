from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.users.models import CustomUser
from apps.banking.models import Wallet


@receiver(post_save, sender=CustomUser)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)


post_save.connect(create_user_wallet, sender=CustomUser)
