import jwt
import clearbit
from django.db import models
from pyhunter import PyHunter
from datetime import datetime
import logging


my_hunter_api_key = #########
clearbit.key = ###########


class MISMATCH_BETWEEN_ENTITIES_ERROR(Exception):
    pass


class NOT_UNIQUE_ERROR(Exception):
    pass


# Handle general utilities

def _mail_verification(mail):
    """Mail validation via hunter site"""
    try:
        hunter = PyHunter(my_hunter_api_key)
        user_data = hunter.email_verifier(mail)
        # On risky & deliverable continue
        if user_data['result'] == 'undeliverable':
            raise Exception('Mail not approved')
        return user_data
    except Exception as e:
        logging.warning(e)
        return {e}


def _encode(mail, user_id):
    """ Encode JWT from user mail & user id"""
    try:
        jwt_code = jwt.encode({mail: user_id}, 'secret', algorithm='HS256')
        if not jwt_code:
            raise Exception('JWT code not created')

        return jwt_code

    except Exception as e:
        logging.warning(e)
        return {e}


def _decode(verify_code):
    """Decode JWT code to user mail & user id"""
    try:
        jwt_code = jwt.decode(verify_code, 'secret', algorithms=['HS256'])
        if not jwt_code:
            raise Exception('JWT code not encrypted')

        mail = list(jwt_code)[0]
        return mail, jwt_code[mail]

    except Exception as e:
        logging.warning(e)
        return {e, -1}


# Handle users
class User(models.Model):
    fullname = models.CharField(max_length=50, default='Anonymous')
    email = models.EmailField(unique=True)
    number_of_posts = models.IntegerField(default=0)

    @classmethod
    def create(cls, email):
        """Create new user object in table"""
        try:
            fullname = 'Anonymous'

            # Mail validation
            mail_auth = _mail_verification(email)

            if isinstance(mail_auth, dict):
                # User data enrichment
                add_data = clearbit.Enrichment.find(email=email, stream=True)
                if add_data:
                    if add_data['person']:
                        fullname = add_data['person']['name']['fullName']
                else:
                    logging.warning('Clearbit data addition failed')

                user = cls(email=email.decode('utf-8'), fullname=fullname)
                user.save()
                return _encode(user.email, user.pk)

        except Exception as e:
            logging.warning(e)
            return {e}

    def inc_posts(self):
        """ increment post numerator"""
        try:
            self.number_of_posts += 1
            self.save()

            return self.number_of_posts

        except MISMATCH_BETWEEN_ENTITIES_ERROR as e:
            logging.warning(f'User {self.number_of_posts} update error')
            return type(e).__name__

    def __str__(self):
        return f'{self.fullname} id {self.pk}'


# Handle posts
class Post(models.Model):
    post_text = models.CharField(max_length=150, default='Empty')
    users = models.ManyToManyField(
        'User',
        through='Like',
    )
    number_of_likes = models.IntegerField(default=0)

    @classmethod
    def create(cls, user_id):
        """Create new post object in table"""
        try:
            post = Post.objects.create()

            if post:
                post.users.add(user_id)
                post.post_text = f'Post number {user_id.inc_posts()} of user {user_id.pk}'

                post.save()
                if post is None:
                    raise MISMATCH_BETWEEN_ENTITIES_ERROR(f'Like {post} saved but')

            return post.pk

        except MISMATCH_BETWEEN_ENTITIES_ERROR as e:
            if post:
                post.delete()
            logging.warning(f'{e},Post obj deleted, no mismatches')
            return {f'{e},Post obj deleted, no mismatches'}

        except Exception as e:
            logging.warning(e)
            return {e}

    def update_likes(self, diff):
        """update likes numerator for the post"""
        try:
            self.number_of_likes += diff
            self.save()

            return self.number_of_likes

        except Exception as e:
            logging.warning(f'{e}, Post {self.number_of_likes} update error')
            return False

    def __str__(self):
        return self.post_text

# Handle Likes


class Like(models.Model):
    post_related = models.ForeignKey(Post, on_delete=models.CASCADE)
    user_related = models.ForeignKey(User, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=datetime.now(), blank=True)
    any_likes = models.BooleanField(default=False)

    class Meta:
        unique_together = [['user_related', 'post_related']]

    '''Do like'''
    def do_like(self):
        flag = False                # Monitoring likes flag for mismatch updates
        try:
            if not self.any_likes:
                self.any_likes = not self.any_likes
                self.save()
                flag = True

            '''Update user's posts_numerator'''
            if not isinstance(self.post_related.update_likes(1), int):
                raise MISMATCH_BETWEEN_ENTITIES_ERROR(
                    f'Unlike {self.pk} done, but mismatch on updating other tables')

            return self.pk

        except MISMATCH_BETWEEN_ENTITIES_ERROR as e:
            ''' Disposal if on post_save works '''
            if flag:
                self.any_likes = not self.any_likes
                self.save()
            logging.warning(e)
            return {f'{e},like obj deleted, no mismatches'}

        except Exception as e:
            ''' Did not perform action, can be due to: DB lock '''
            logging.warning(e)
            return {e}

    '''do_unlike'''
    def do_unlike(self):

        try:
            num = self.post_related.update_likes(-1)
            '''Update user's posts_numerator'''
            if isinstance(num, int) and not num:
                self.any_likes = not self.any_likes
                self.save()
            elif not isinstance(num, int):
                return num

            return True

        except Exception as e:
            ''' Did not perform action, can be due to: DB lock '''
            logging.warning(e)
            return {e}

    def __str__(self):
        """ Represent post text as the object"""
        return (f'Like {self.pk} for {self.post_related}, '
                f'which has in total {self.post_related.number_of_likes}')
