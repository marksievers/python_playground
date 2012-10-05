import uuid

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User, check_password, UNUSABLE_PASSWORD
from django.contrib.auth.hashers import make_password
from django.db import models
from django.db.models import get_model
from django.db.models.signals import post_save
from django.dispatch import receiver

#monkey patch to emulate djangos get_profile
def get_account(self):
    django_user_id = self.id

    obj, created = TangyUser.objects.get_or_create(django_user_id=django_user_id)
    get_account.id = obj.id
    get_account.name = obj.full_name
    get_account.email = obj.email
    get_account.user = obj

    return get_account

auth.models.User.add_to_class('get_account', get_account)


class TangyUser(models.Model):
    email = models.EmailField(null=True) # TODO: unique=True back on
    password = models.CharField(max_length=128, help_text="Enter plain text password here and it will be hashed and set.", blank=True)
    django_user_id = models.IntegerField(db_index=True, null=True)

    first_name = models.CharField(max_length=256, blank=True)
    last_name = models.CharField(max_length=256, blank=True)
    salutation = models.CharField(max_length=32, blank=True)
    org_title = models.CharField(max_length=64, blank=True)
    org_name = models.CharField(max_length=256, blank = True)
    duplicate = models.ForeignKey('self', null=True, blank=True)
    imported_id = models.CharField(max_length=64, null=True, unique=True)
    last_update = models.DateTimeField(auto_now = True, auto_now_add=True)

    class Meta:
        verbose_name = 'subscriber'

    def __init__(self, *args, **kwargs):
        super(TangyUser, self).__init__(*args, **kwargs)

        if kwargs.has_key('password'):
            self.set_password(kwargs['password'])

    def __unicode__(self):
        description = None

        if self.full_name and self.org_name:
            description = u", ".join([self.full_name, self.org_name])
        elif self.org_title and self.org_name:
            description = u", ".join([self.org_title, self.org_name])
        elif self.full_name:
            description = self.full_name
        elif self.org_name:
            description = self.org_name
        elif self.org_title:
            description = self.org_title
        else:
            description = self.pk

        return description

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def set_password(self, raw_password):
        if raw_password is None:
            self.set_unusable_password()
        else:
            self.password = make_password(raw_password)

    def set_unusable_password(self):
        # Sets a value that will never be a valid hash
        self.password = UNUSABLE_PASSWORD

    def has_usable_password(self):
        if self.password is None or self.password == UNUSABLE_PASSWORD:
            return False
        else:
            return True

    def find_duplicate(self):
        if self.email != None and self.email.strip() != '' and self.full_name:
            dupes = TangyUser.objects.filter(models.Q(name=self.full_name) | models.Q(email=self.email)).filter(duplicate__isnull=True).exclude(pk=self.pk)
        elif self.full_name:
            dupes = TangyUser.objects.filter(models.Q(name=self.full_name)).filter(duplicate__isnull=True).exclude(pk=self.pk)
        elif self.email != None and self.email.strip() != '':
            dupes = TangyUser.objects.filter(models.Q(email=self.email)).filter(duplicate__isnull=True).exclude(pk=self.pk)
        else:
            return False

        if len(dupes) > 0:
            self.duplicate = dupes[0]

            self.save()
            return True

        return False

    def num_subscriptions(self):
        return self.subscriptions.count()

    @property
    def full_name(self):
        return " ".join([self.first_name or '', self.last_name + '']).strip()

    @property
    def profile(self):
        return self.get_profile()

    def get_profile(self):
        """Get the TangyUser's related Django User profile"""
        if self.django_user_id == None:
            return None

        try:
            u = User.objects.get(pk=self.django_user_id)
        except User.DoesNotExist:
            return None

        return u.get_profile()

def generate_short_uuid():
    # base-62 encode a uuid so it fits in the django auth 30 char limit
    # doesn't need to be reversable, we just need a unique username
    # if you need to reverse it, I stole the code from http://stackoverflow.com/questions/1119722/base-62-conversion-in-python

    uuid_str = str(uuid.uuid4()).replace('-', '')
    uuid_int = int(uuid_str, 16)

    alphabet = "01234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIKLMNOPQRSTUVWXYZ"

    if (uuid_int == 0):
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while uuid_int:
        rem = uuid_int % base
        uuid_int = uuid_int // base
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)

# When TangyUser is created, make sure regular user is created too
@receiver(post_save, sender=TangyUser)
def create_django_user(sender, instance, created, raw, **kwargs):
    if created and not raw:
        django_user = User(username=generate_short_uuid(), email=instance.email or '')

        django_user.set_unusable_password()
        django_user.save()
        instance.django_user_id = django_user.pk
        instance.save()

# When User is saved, make sure there's a Profile too
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, raw, **kwargs):
    if raw or (not hasattr(settings, 'AUTH_PROFILE_MODULE')) or (not settings.AUTH_PROFILE_MODULE):
        return

    profile_model = get_model(*settings.AUTH_PROFILE_MODULE.split('.'))

    profile_model.objects.get_or_create(user=instance)

@receiver(post_save, sender=TangyUser)
def welcome_user(sender, instance, created, raw, **kwargs):
    if created and not raw:
        #TODO: email user:
        pass
