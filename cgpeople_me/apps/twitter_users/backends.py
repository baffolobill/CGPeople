
from django.contrib.auth.models import User

from twitter_users.models import TwitterInfo
from twitter_users import settings
from generic.models import Profile

class TwitterBackend(object):
    def authenticate(self, twitter_id=None, username=None, token=None, secret=None):
        # find or create the user
        try:
            info = TwitterInfo.objects.get(id=twitter_id)
            # make sure the screen name is current
            if info.name != username:
                info.name = username
                info.save()
            user = info.user
        except TwitterInfo.DoesNotExist:
            email = None  # "%s@twitter.com" % username
            try:
                user = User.objects.get(username=username)
            except:
                user = User.objects.create_user(settings.USERS_FORMAT % username)
                user.save()

            info, created = TwitterInfo.objects.get_or_create(user=user, name=username,  \
                    id=twitter_id, token=token, secret=secret)
            info.save()

        try:
            profile = Profile.objects.get(user=user)
        except:
            profile = Profile(user=user, name=username, page_url=username)
            profile.save()

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
