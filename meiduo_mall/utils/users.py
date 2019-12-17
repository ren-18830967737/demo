import re
from django.contrib.auth import authenticate
import logging



logger = logging.getLogger('django')



from django.contrib.auth.backends import  ModelBackend

from apps.users.models import User


class UsernameModelBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:

            if re.match(r'1[3-9]\d{9}',username):
                user = User.objects.get(mobile=username)
            else:
                user = User.objects.get(username=username)
        except Exception as e:
            logger.error(e)
            return None

        else:
            if user.check_password(password):
                return user