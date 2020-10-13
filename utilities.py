# Utility for performing actions on server

import jwt
import random
import requests
import logging
from urllib.parse import urljoin

from config import *


# Hello & Chao
def print_chao(name):
    print(f'Hi, {name}')


###################### JWT related functions ###############################

def decode(verif_code):
    ''' Decode JWT code to user mail & user id '''
    try:
        jwt_code = jwt.decode(verif_code, 'secret', algorithms=['HS256'])
        if not jwt_code:
            raise Exception('JWT code not encrypted')

        mail = list(jwt_code)[0]
        return mail, str(jwt_code[mail])

    except Exception as e:
        logging.warning(f'{e} Func: JWT')
        return -1, -1


def encode(mail, id):
    ''' Encode JWT from user mail & user id '''
    try:
        jwt_code = jwt.encode({mail: id}, 'secret', algorithm='HS256')
        if not jwt_code:
            raise Exception('JWT code not created')
        else:
            return jwt_code
    except Exception as e:
        logging.warning(f'{e} Func: JWT')
        return {e}


###################### Produce the posts list for likelihood phase ###############################

# Produce users with at least 1 post with 0 likes ###############################

def zero_post(list_op_likes, current_candidate):
    ''' Descending order list of all users with at least 1 post with 0 likes
    list_op_liks is of the form: list of User class, current_candidate is a single User class '''
    built_up_list = []
    try:
        users_list_holds_posts = []

        for elem in list_op_likes:
            if elem != current_candidate:
                '''Pick all users who own, at least 1 post with 0likes, (exclude current)'''
                if _post_per_likes_serach(elem.post_per_likes_list, []):
                    built_up_list = _users_by_post_for_likelihood_expand(elem, built_up_list)
                    continue

        '''No posts under the criteria'''
        if not built_up_list:
            raise Exception(f'No posts for user {current_candidate.id}  to perform like or unlike')

        # Extract all user posts
        for j in built_up_list:
            posts_per_user = _extract_posts_per_user(j.id, j.post_per_likes_list)
            users_list_holds_posts = users_list_holds_posts + posts_per_user

        logging.info(f'List of all user_, post_id')
        print_zerolist(users_list_holds_posts, current_candidate)
        return users_list_holds_posts

    except Exception as e:
        logging.warning(f'{e}. Func: zero_post')
        return {e}


# Produce total list of all related users posts out of zero list#################

def _users_by_post_for_likelihood_expand(new_user, list_of_users, opt_list_users=[]):
    ''' Desc users by no of posts'''
    try:
        if not list_of_users:
            '''Empty from previous iteration'''
            opt_list_users.clear()
            ''' add at the beginning '''
            opt_list_users.append(new_user)
            return opt_list_users

        for current in range(len(list_of_users)):
            ''' add in the middle'''
            if new_user.number_of_posts >= list_of_users[current].number_of_posts:
                opt_list_users.insert(current, new_user)
                break
            else:
                if current == len(list_of_users) - 1:
                    ''' add at the end'''
                    opt_list_users.append(new_user)
                    break

        return opt_list_users

    except Exception as e:
        logging.warning(f'{e} Func: users_by_post_for_likelihood_expand')
        return {e}


def _extract_posts_per_user(user_id, posts_list):
    '''For each user, load all posts'''
    try:
        tmp = []
        for i in posts_list:
            op_post = dict.fromkeys([user_id], list(i)[0])
            tmp.append(op_post)
        return tmp

    except Exception as e:
        logging.warning(f'{e} Func: extract_posts_per_user')
        return {e}


# Choose posts randomly and decide action-like\unlike ###########################

def choose_posts(list_of_users_op_to_like, current_candidate, current_max_likes=0):
    '''Randomly chose from zero list posts. data form: Chosen_posts =>{user_id:post_id}'''
    chosen_list = []
    action_list = []

    try:
        while current_max_likes and list_of_users_op_to_like:
            '''Zero list not empty and post list is not match likes required for  this iteration '''

            index = 0

            if not (len(list_of_users_op_to_like) < 2):
                '''Solve empty range for randrange() (0, 0, 0) '''
                index = random.randint(1, len(list_of_users_op_to_like) - 1)

                chosen_list.append(list_of_users_op_to_like[index])

                '''void post to be chosen more then once'''
                list_of_users_op_to_like.pop(index)

            current_max_likes -= 1

        ''' Action choose procedure: do_unlike for posts already liked by current candidate. other: do_like 
            Action_list data form   => [unlike/like:{user_id:post_id}] '''

        print_chosen_post_list(current_candidate, chosen_list, 'before action assignment')

        if chosen_list:
            action_list = _divide_by_action(chosen_list, current_candidate)

        return action_list

    except Exception as e:
        logging.warning(f'{e} Func: choose_posts')
        return {e}


def _divide_by_action(chosen_posts_list, current_candidate):
    ''' Current user likelihood action, by post
     data from the form of: {action:{current_user:[chosen_list]}}'''

    try:
        action_list = []
        for chosen_post in range(len(chosen_posts_list)):
            '''Initialize 'key' of dictionary'''

            '''Retrieve the user's posts per likes - to check if candidate already liked this post'''
            elem = _retrieve_user(list(chosen_posts_list[chosen_post])[0])

            '''User not found'''
            if not elem:
                raise CRITICAL_IN_ERROR(
                    f' Partial update taken in BOT - in addition Mismatch between server and BOT')

            if elem.handle_likes_per_post(chosen_posts_list[chosen_post][list(chosen_posts_list[chosen_post])[0]],
                                          'find', current_candidate):
                '''For each post check if candidate already liked it'''
                action_key = dict.fromkeys(['unlike'], 0)  # Initialize the key
            else:
                action_key = dict.fromkeys(['like'], 0)

            action_list.append(action_key)  # Exmpl: [{unlike}:{683:0}]
            '''Handle the 'value' of dictionary '''  # Exmpl: [{unlike}:{683:[5:76,8:7,9:88]}]
            action_list[chosen_post][list(action_list[chosen_post])[0]] = chosen_posts_list[chosen_post]

        return action_list

    except CRITICAL_IN_ERROR as e:
        logging.warning(f'{e} Func: divide_by_action')
        return {e}

    except Exception as e:
        logging.warning(f'{e} Func: divide_by_action')
        return {e}


def _retrieve_user(user_id):
    '''User instance from given id'''
    try:
        for tmp in users:
            if user_id == tmp.id:
                return tmp

    except CRITICAL_IN_ERROR as e:
        logging.critical(f'{e}. Func: retrieve  user')
        return type(e).__name__


def _post_per_likes_serach(likes_per_post, operand):
    '''Search on list post_per_likes if post has 0 likes'''

    for i in list(likes_per_post):
        if i[list(i)[0]] == operand:
            return True

    return False


###################### likelihood phase ##########################################################

def is_final(metch_all_likes, zero_list_flag, users_list_holds_posts):
    '''Is 2 final BOT flags, for all users raised?'''

    is_final_status(metch_all_likes, zero_list_flag,users_list_holds_posts)
    for i in range(len(users)):
        if not (metch_all_likes[i] or zero_list_flag[i]):
            return False
    return True


###################### Print utility ############################################

def print_userlist(list_of_users):
    '''users after creation'''
    print('This is the list of users that created. Func-main')
    for i in list_of_users:
        print(f'user_id = {i.id}, user_email = {i.email}, likes to distribute: {i.number_of_likes}')


def print_postlist(list_of_users):
    '''users after post creation'''
    print(f'users by their posts')
    for i in range(len(list_of_users)):
        print(f'user_id = {list_of_users[i].id}, total_posts =  {list_of_users[i].number_of_posts}, '
              f'list of user_posts ={list_of_users[i].post_per_likes_list}')


def print_zerolist(list_of_users_holds_post_0likes, current_candidate):
    '''users & post for users with at least 1 0 likes'''
    print(
        f'{new_line}The zero likes for user {current_candidate.id} is of {len(list_of_users_holds_post_0likes)} posts currently:{new_line}{list_of_users_holds_post_0likes}')


def print_chosen_post_list(current_user, action_list, before=0):
    '''chosen posts users & post out of for users with at least 1 0 likes list, by action'''
    pass
    '''
    if not before:
        print(
            f'{new_line}Chosen posts list for user {current_user.id} by their likelihood action:{new_line}{action_list}')
    else:
        print(f'{new_line}Chosen posts list for user {current_user.id} {before}:{new_line}{action_list}')
    '''

def print_user_total_likes_list(current_user):
    '''chosen posts users & post out of for users with at least 1 0 likes list, by action'''
    print(
        f'Totally, till now, {current_user.current_number_of_likes} likelihood actions taken out of total {current_user.number_of_likes} for user {current_user.id}. Func-main')


def is_final_status(match, zero, users_list_holds_posts):
    '''Status of Bot operation'''
    print(f'Status of Bot operation: {new_line}user match his max likes:{match}, user has posts to like?{zero}')


def status_msg(*args):
    '''logging.info messages & a print status'''
    if args[0] == 'post':
        print(f'{new_line}Start Create post phase')
    elif args[1] == 'like':
        logging.info(f'This is the list of posts to act, for {args[0]} user')
    elif args[1] == 'user':
        print(f'{new_line}Creating {args[0]} users')
    elif args[1] == 'rec_likes':
        logging.info(f'User {args[0]} is not doing any likes this iteration')
    elif args[1] == 'zero_list':
        logging.info(f'No posts available to like in this iteration for user: {args[0]}')
    elif args[1] == 'match':
        print(f'{new_line}User {args[0].id}, finished his {args[0].current_number_of_likes} likes')
    elif args[2] == 'like':
        print(f'{new_line}Start Likelihood process to user {args[1]} with {args[0]} likes ')
    elif args[2] == 'user':
        logging.info(f'User {args[0].id} is done with likes, he did all {args[1]} likes he has')
    elif args[3] == 'like':
        logging.info(f'post {args[0]}, added liked user {args[1]} of obj {args[2]}')
    elif args[3] == 'unlike':
        logging.info(f'post {args[0]}, removed like of user {args[1]} of obj {args[2].id}')
    elif args[3] == 'find':
        logging.info(f'post {args[0]}, found for like of user {args[1]} of obj {args[2]}')



###################### User Class ############################################

# Handle User class
class User:
    ''' Handle user User class '''

    def __init__(self, email):
        self.number_of_posts = random.randint(1, max_posts_per_user)
        self.number_of_likes = random.randint(1, max_likes_per_user)
        self.id = -1
        self.email = email
        self.post_per_likes_list = []  # list of dict post_id : num_likes. num_likes is 0 or 1
        self.current_number_of_likes = 0

    ###################### sign up  ############################################

    def sign_up(self):
        ''' Connect to server and create new user '''
        query_url = 'core/sign_up'
        origin_url = urljoin(URL, query_url)

        try:
            response = requests.post(origin_url, data=self.email)

            # Communication Status
            if response.status_code == 200:
                # Bypass the segment error to be handled further on
                if response.content.decode('utf-8').startswith('Mail verification failed') or \
                        response.content.decode('utf-8').startswith('UNIQUE constraint failed') or \
                        response.content.decode('utf-8').startswith('Clearbit data addition failed') or \
                        response.content.decode('utf-8').endswith('is not defined'):
                    raise Exception('User creation failed')
                elif response.content.decode('utf-8') == 'None':
                    raise Exception('User creation failed')
                elif response.content.decode('utf-8') != self.email or \
                        response.content.decode('utf-8').startswith('JWT code not created'):

                    self.email, self.id = decode(response.text)
                    if self.id == -1:
                        raise CRITICAL_BET_ERROR('Mismatch between server and BOT')

                    return True
            else:
                raise Exception('Communication failure')

        except CRITICAL_BET_ERROR as e:
            logging.critical(f'{e}. Func:sign up')
            return False

        except Exception as e:
            logging.warning(f'{e}. Func: sign up')
            return False

    ###################### sign in  ############################################

    def login(self, cond=''):
        ''' Login to user '''
        query_url = 'core/login'

        origin_url = urljoin(URL, query_url)
        try:
            response = requests.post(origin_url, data=encode(self.email, self.id))

            # Communication Status
            if response.status_code != 200:
                raise Exception('Communication failure')
            else:
                if response.content.decode('utf-8').endswith('is not defined'):
                    raise Exception('User is not defined')
                if response.content.decode('utf-8').endswith('Not enough segments'):
                    raise Exception('User is not defined')

            return True

        except Exception as e:
            logging.critical(f'{e}. Func: login')
            return False

    ###################### create post  ############################################

    def create_post(self):
        ''' Creating post '''
        query_url = 'core/create_post'
        origin_url = urljoin(URL, query_url)

        try:
            response = requests.post(origin_url, data=self.id)

            # Communication Status
            if response.status_code == 200:
                data = response.content.decode('utf-8')
                if data.isnumeric():
                    return self.handle_likes_per_post(data, 'add')  # Update new post: id, likes=diff_likes=0)
                else:  # Decrement the total posts for user  # decrement numerator of id_numerator =-1
                    self.number_of_posts -= 1  # Post not created at all - No Mismatches

                    raise Exception('Post was not created')
            else:  # Update new post: id = -1, likes=diff_likes=0
                self.handle_likes_per_post(-1, 'add')  # Flag for inconsistency to DB/Server
                raise CRITICAL_BET_ERROR('Communication failure, Mismatch between server and BOT')

        except CRITICAL_BET_ERROR as e:
            logging.critical(f'{e}. Func: create post')
            return type(e).__name__

        except Exception as e:
            logging.warning(f'{e}. Func: create post')
            return {e}

    ###################### Synchronization posts&likes  ############################################

    def handle_likes_per_post(self, likelihood_obj, action, diff_likes=0):
        ''' For any post item of user:post-> handle local repository-per post :
            post_id:user_id , of user  '''
        '''Adjust likes list of who liked post's user '''
        try:
            if action == 'add':
                '''When post created, post_id: null list of likes'''
                po_li = dict.fromkeys([likelihood_obj], [])
                self.post_per_likes_list.append(po_li)
            elif action == 'like':
                '''When like done, for specific post, list of likes 
               updated with the user performed like for this post'''
                for i in list(self.post_per_likes_list):
                    if likelihood_obj == list(i)[0]:
                        i[list(i)[0]].append(diff_likes)

                        status_msg(likelihood_obj, diff_likes.id, diff_likes, 'like')
                        break
            elif action == 'unlike':
                '''When unlike done, for specific post, list of likes 
               deletes the user performed likelihood action for this post'''
                for i in list(self.post_per_likes_list):
                    if likelihood_obj == list(i)[0]:
                        status_msg(likelihood_obj, diff_likes.id, diff_likes, 'unlike')
                        return i[list(i)[0]].pop(0)
            else:
                for i in list(self.post_per_likes_list):
                    '''Find chosen post'''
                    if likelihood_obj == list(i)[0]:
                        if not (i[list(i)[0]] and (diff_likes in i[list(i)[0]])):
                            return False
                        status_msg(likelihood_obj, diff_likes.id, diff_likes, 'find')
                        break

            return True

        except CRITICAL_BET_ERROR as e:
            logging.critical(f'{e}. Func: update likes')
            return type(e).__name__

        except CRITICAL_IN_ERROR as e:
            logging.critical(f'{e}. Func: update likes')
            return type(e).__name__

    def adjust_related_posts_or_likes(self, obj, current_item):
        ''' Numerator update: posts number decremented if a creation in DB failed,
            *current_likes* status appended/removed user_id new element to like as the likelihood activated'''
        try:
            self.current_number_of_likes += 1
            '''retrieve likelihood instance and update likes per post numerator '''
            tmp = _retrieve_user(list(current_item)[0])

            if obj == 'like':
                '''current_item is  of type user_id:post_id, self is the likelihood user, obj is like '''
                response = tmp.handle_likes_per_post(current_item[list(current_item)[0]], obj, self)
            elif obj == 'unlike':
                response = tmp.handle_likes_per_post(current_item[list(current_item)[0]], obj, self)

            if not response:
                raise CRITICAL_IN_ERROR(
                    f' Partial update taken in BOT - in addition Mismatch between server and BOT')

            return True

        except CRITICAL_IN_ERROR as e:
            logging.critical(f'{e}. Func: adjust related posts')
            return type(e).__name__

    ###################### perform Likelihood operation  ############################################

    def do_like(self, item_to_like):
        ''' Do like to chosen post '''
        query_url = 'core/do_like'
        origin_url = urljoin(URL, query_url)

        try:
            response = requests.post(origin_url, data=item_to_like)

            # Communication Status
            if response.status_code == 200:
                data = response.content.decode('utf-8')
                if data.isnumeric():
                    '''Synchronize likes status in the operate user and the user's posts'''
                    return self.adjust_related_posts_or_likes('like', item_to_like)
                else:  # Like not created at all - No Mismatches
                    raise Exception('The like object was not created at all. No Mismatch')
            else:
                # inconsistency between Server and DB/Server  - handle separately
                raise CRITICAL_BET_ERROR('Most likely a communication failure, Mismatch between server and BOT')

        except CRITICAL_BET_ERROR as e:
            logging.critical(f'{e}. Func: do like')
            return type(e).__name__

        except CRITICAL_IN_ERROR as e:
            logging.critical(f'{e}, Func: do like')
            return type(e).__name__

        except Exception as e:
            logging.warning(f'{e}, Func: do like')
            return {e}

    def do_unlike(self, item_to_unlike):
        ''' Do unlike to chosen post '''
        query_url = 'core/do_unlike'
        origin_url = urljoin(URL, query_url)

        try:
            response = requests.post(origin_url, data=item_to_unlike)

            # Communication Status
            if response.status_code == 200:
                data = response.content.decode('utf-8')
                if data == 'True':
                    '''synchronize likes status in the operate user and the user's posts'''
                    return self.adjust_related_posts_or_likes('unlike', item_to_unlike)
                else:  # Like not created at all - No Mismatches
                    raise Exception('Unlike was not done')
            else:
                # inconsistency between Server and DB/Server  - handle separately
                raise CRITICAL_BET_ERROR('Communication failure, Mismatch between server and BOT')

        except CRITICAL_BET_ERROR as e:
            logging.critical(f'{e}. Func: do unlike')
            return type(e).__name__

        except CRITICAL_IN_ERROR as e:
            logging.critical(f'{e}. Func: do unlike')
            return type(e).__name__

        except Exception as e:
            logging.warning(f'{e}. Func: do unlike')
            return {e}
