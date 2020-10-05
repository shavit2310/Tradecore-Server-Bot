#!/bin/python3

import jwt
import clearbit
from django.db import models
from pyhunter import PyHunter
import logging

my_hunter_api_key = '''NEED TO ADD ON CLONE'''
clearbit.key = '''NEED TO ADD ON CLONE'''


class MISMATCH_BETWEEN_ENTITIES(Exception):
    # print
    pass


class NOT_UNIQUE(Exception):
    # print
    pass


# Handle general utilities

def _mail_verification(mail):
    '''Mail validation via hunter site'''
    try:

        hunter = PyHunter(my_hunter_api_key)
        user_data = hunter.email_verifier(mail)
        # On riski & deliverable continue
        if user_data['result'] == 'undeliverable':
            raise Exception('Mail not approved')
        return user_data
    except Exception as e:
        logging.warning(e)
        return {e}


def _encode(mail, id):
    ''' Encode JWT from user mail & user id'''
    try:
        jwt_code = jwt.encode({mail: id}, 'secret', algorithm='HS256')
        if not jwt_code:
            raise Exception('JWT code not created')

        return jwt_code

    except Exception as e:
        logging.warning(e)
        return {e}


def _decode(verif_code):
    '''Decode JWT code to user mail & user id'''
    try:
        jwt_code = jwt.decode(verif_code, 'secret', algorithms=['HS256'])
        if not jwt_code:
            raise Exception('JWT code not encrypted')

        mail = list(jwt_code)[0]
        return mail, jwt_code[mail]

    except Exception as e:
        logging.warning(e)
        return {e, -1}


def _login(verif_code):
    '''Verify known user'''
    try:
        op_mail, op_id = _decode(verif_code)
        if op_id == -1:
            raise Exception('JWT code not decrypted')

        user_obj = User.objects.get(pk=op_id)
        if user_obj.pk != None:
            if user_obj.email == op_mail:
                return user_obj.id
        else:
            raise Exception('Verification failed')

    except Exception as e:
        return {e}


def _retreive_user(user_id):
    ''' Uploading user object '''
    try:
        user_obj = User.objects.get(pk=user_id)
        if not user_obj:
            raise Exception('User object is not found')

        return user_obj

    except Exception as e:
        logging.warning(e)
        return {e}


def _is_post(post_id):
    ''' Uploading post object '''
    try:
        post_obj = Post.objects.get(pk=post_id)
        if not post_obj:
            raise Exception('Post object is Not found')

        return post_obj

    except Exception as e:
        logging.warning(e)
        return {e}


def _is_like(user_obj, post_obj):
    ''' Uploading like object '''
    try:

        like_op = Like.objects.value_list(user_related_like=user_obj, post_related_like =post_obj)
        print (like_op)
        '''              
        if not isinstance(like, models.Like):
            raise Exception('Like obj to post per user obj is Not unique')
        '''

        return False

    except Exception as e:
        logging.warning(e)
        return {type(e).__name__, like}


# Handle users
class User(models.Model):
    fullname = models.CharField(max_length=100, default='Name_not_known')
    email = models.EmailField(unique=True)
    number_of_posts = models.IntegerField(default=0)

    @classmethod
    def create(cls, email):
        '''Create new user object in table'''

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
                return (_encode(user.email, user.id))

        except Exception as e:
            logging.warning(e)
            return {e}

    def inc_posts(self):
        ''' dispose if on save works'''

        try:
            self.number_of_posts += 1
            self.save()

            return True

        except Exception:
            logging.warning(f'User {self.number_of_posts} update error')
            return False

    def __str__(self):
        '''Represent user name as the object'''
        return self.fullname


# handle post : Relate many -> one to user
class Post(models.Model):
    post_text = models.CharField(max_length=150)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    number_of_likes = models.IntegerField(default=0)

    @classmethod
    def create(cls, user_obj):
        '''Create new post object in table'''
        try:
            post_text = f'Post number {user_obj.number_of_posts + 1} of user {user_obj.id} named: {user_obj.fullname}'

            post = cls(user=user_obj, post_text=post_text)

            ''' Update user's posts_numerator when saving post '''
            post.save()
            if post.pk is None:
                raise Exception('Post Can not be created')

            '''  disposal if on post_save works   '''
            # Update user's posts_numerator
            if not post.user.inc_posts():
                raise MISMATCH_BETWEEN_ENTITIES(
                    f'Post {post.pk} saved but user number_of_posts in related user {user_obj.pk} did not ')

            return post.pk

        except Exception as e:
            del post
            logging.warning(e)
            return {e, f'Post obj deleted, no mismatches'}

    def update_post(self, diff):
        ''' dispose if on save works'''

        try:
            self.number_of_likes += diff
            self.save()

            return True

        except Exception:
            logging.warning(f'Post {self.number_of_likes} update error')
            return False


    def __str__(self):
        ''' Represent post text as the object'''
        return self.post_text

    def __repr__(self):
        return str(self.post.pk)


# handle like: Relate many -> many to user, Relate many -> many to user
class Like(models.Model):
    like_text = models.CharField(max_length=150, default='Empty')
    user_related_like = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post_related_like = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)

    # Do like
    @classmethod
    def create(cls, user_related_like, post_related_like):
        '''Create new like object in table'''
        try:

            like_text = f'Like number {post_related_like.number_of_likes + 1} of {post_related_like.post_text}'

            like = cls(user_related_like=user_related_like, post_related_like=post_related_like, like_text=like_text)
            like.save()

            '''  disposal if on post_save works   '''
            # Update user's posts_numerator
            if not like.post_related_like.update_post(1):

                raise MISMATCH_BETWEEN_ENTITIES(
                    f'Like {like.pk} saved but user number_of_posts in related user {post_related_like.pk} did not ')

            return True

        except Exception as e:
            del like
            logging.warning(e)
            return {e, f'like obj deleted, no mismatches'}

    def retreive_like(self,user_object,post_object):
        try:

            op_likes = Like.objects.value_list(user_related_like =user_object)

            #, post_related_like =post_object)
            if not isinstance(op_likes, models.Like):
                raise Exception('Like obj to post per user obj is Not unique')

            return False

        except Exception as e:
            logging.warning(e)
            return {type(e).__name__, op_likes}


    def __str__(self):
        ''' Represent post text as the object'''
        return self.like_text

    def __repr__(self):
        return self.pk


