# Utility of Creating users

import jwt
import random
import requests
import logging
from urllib.parse import urljoin

from config import *


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
        flag = False
        users_list_holds_posts = []

        for elem in list_op_likes:
            if elem != current_candidate:
                for item in elem.post_per_likes_list:
                    '''Pick all posts with 0likes, beside current'''
                    if item[list(item)[0]] == 0:
                        flag = True  # At least on post has 0 likes
                        built_up_list = users_by_post_for_likelihood_expand(elem, built_up_list)
                        break

            if not flag:  # No post for this user with 0 likes
                logging.warning('No posts for current user to perform like or unlike')

        if not built_up_list:
            raise Exception('No posts for current user to perform like or unlike')

        # Extract all user posts
        for j in built_up_list:
            posts_per_user = extract_posts_per_user(j.id, j.post_per_likes_list)
            users_list_holds_posts = users_list_holds_posts + posts_per_user

        logging.info(f'List of all user_, post_id')
        print_zerolist(users_list_holds_posts,current_candidate)
        return users_list_holds_posts

    except Exception as e:
        logging.warning(f'{e} Func: zero_post')
        return {e}

# Produce total list of all related users posts out of zero list#################

def users_by_post_for_likelihood_expand(new_user, list_of_users, opt_list_users=[]):
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

def extract_posts_per_user(user_id, posts_list):
    try:
        tmp = []
        for i in posts_list:
            op_post = dict.fromkeys([user_id], list(i)[0])
            tmp.append(op_post)
        return tmp

    except Exception as e:
        logging.warning(f'{e} Func: extract_posts_per_user')
        return {e}

# Choose posts randomly and deside action-like\unlike ###########################

def choose_posts(list_of_users_op_to_like, current_candidate, required_likes_for_iteration=0):
    chosen_list = []
    action_list = []

    try:
        ''' To draw randomly posts out of the list '''
        # Chosen_posts =>{user_id:post_id}'''


        if not required_likes_for_iteration:
            current_max_likes = current_candidate.number_of_likes
        else:
            current_max_likes = required_likes_for_iteration

        while current_max_likes or not list_of_users_op_to_like:
            '''This list contain pairs of user_id&post_id obj of lottery items '''
            '''randint alias for: randrange(start, stop+1 ) '''

            index = 0

            if not (len(list_of_users_op_to_like) < 2):
                '''Solve empty range for randrange() (0, 0, 0) '''
                index = random.randint(0, len(list_of_users_op_to_like) - 1)

            if not (list(list_of_users_op_to_like[index])[0] == current_candidate.id):
                '''User can not like his own posts'''
                chosen_list.append(list_of_users_op_to_like[index])
                list_of_users_op_to_like.pop(index)

            # Avoid post to be chosen more then once
            current_max_likes -= 1

        ''' Action determination => do_unlike, do_like '''
        ''' For posts already liked by current_user perform unlike , other perform like'''
        # Action_list => [0/1:chosen_posts_obj] 0=>unlike, 1 for like

        if chosen_list:
            action_list = divide_by_action(chosen_list, current_candidate)

        return action_list

    except Exception as e:
        logging.warning(f'{e} Func: chooseposts')
        return {e}


def divide_by_action(chosen_posts_list, current_user):
    ''' If current user liked chosen post-> do unlike : TAG 'unlike', else-> do like : TAG 'like'  '''
    ''' {action:{current_user:[chosen_list]}}'''

    try:
        action_list = []
        for current in range(len(chosen_posts_list)):
            '''initialize the key'''

            if list(chosen_posts_list[current])[0] == current_user.id:
                action_key = dict.fromkeys(['unlike'], 0)  # Initialize the key
            else:
                action_key = dict.fromkeys(['like'], 0)
            action_list.append(action_key)  # [{unlike}:{683:0}]

            action_list[current][list(action_list[current])[0]] = chosen_posts_list[
                current]  # {683:0}         # Initialize the value

        return action_list

    except Exception as e:
        logging.warning(f'{e} Func: divide_by_action')
        return {e}

###################### Print utility ############################################

def print_userlist(list_of_users):
    '''users after creation'''
    for i in list_of_users:
        print(f'user_id = {i.id}, user_email = {i.email}')


def print_postlist(list_of_users):
    '''users after post creation'''
    new_line = '\n'
    print(f'{new_line}users by their posts')
    for i in range(len(list_of_users)):
        print(f'user_id = {list_of_users[i].id}, total_posts =  {list_of_users[i].number_of_posts}, '
              f'list of user_posts ={list_of_users[i].post_per_likes_list}')


def print_zerolist(list_of_users_holds_post_0likes, current_candidate):
    '''users & post for users with at least 1 0 likes'''
    new_line = '\n'
    print(f'{new_line}The zero likes for user {current_candidate.id} is of {len(list_of_users_holds_post_0likes)} posts currently:{new_line}{list_of_users_holds_post_0likes}')


def print_chosenpost_list(current_user, action_list):
    '''chosen posts users & post out of for users with at least 1 0 likes list, by action'''
    new_line = '\n'
    print(f'{new_line}Chosen posts list for user {current_user.id} by their likelihood action:{new_line}{action_list}')

def print_user_total_likes_list(current_user):
    '''chosen posts users & post out of for users with at least 1 0 likes list, by action'''
    print(f'{current_user.current_number_of_likes} likelihood actions taken out of {current_user.number_of_likes} for user {current_user.id}. Func-main')


###################### User Class ############################################

# Handle User class
class User:
    ''' Handle user User class '''

    def __init__(self, email):
        self.number_of_posts = random.randint(1, max_posts_per_user)
        self.number_of_likes = random.randint(1, max_likes_per_user)
        self.id = -1
        self.email = email
        self.post_per_likes_list = []               # list of dict post_id : num_likes. num_likes is 0 or 1
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
                    return self.update_likes_per_post(data)  # Update new post: id, likes=diff_likes=0)
                else:  # Decrement the total posts for user  # decrement numerator of id_numerator =-1
                    self.adjust_related_posts_or_likes('post', -1)  # Post not created at all - No Mismatches
                    raise Exception('Post was not created')
            else:  # Update new post: id = -1, likes=diff_likes=0
                self.update_likes_per_post(-1)  # Flag for inconsistency to DB/Server
                raise CRITICAL_BET_ERROR('Communication failure, Mismatch between server and BOT')

        except CRITICAL_BET_ERROR as e:
            logging.critical(f'{e}. Func: create post')
            return type(e).__name__

        except Exception as e:
            logging.warning(f'{e}. Func: create post')
            return e

    ###################### synocrysem posts&likes  ############################################

    def update_likes_per_post(self, likelihood_obj, diff_likes=0):
        ''' For any post item of user:post-> update local repository-per post : post_id:likes_number '''
        '''Adjust likes numerator for liked post's user '''
        try:
            if not diff_likes:
                po_li = dict.fromkeys([likelihood_obj], 0)
                self.post_per_likes_list.append((po_li))
            else:
                for i in list(self.post_per_likes_list):
                    if likelihood_obj == list(i)[0]:
                        i[list(i)[0]] += diff_likes
                        break
            return likelihood_obj

        except CRITICAL_BET_ERROR as e:
            logging.critical(f'{e}. Func: update likes')
            return type(e).__name__

        except CRITICAL_IN_ERROR as e:
            logging.critical(f'{e}. Func: update likes')
            return type(e).__name__

    def adjust_related_posts_or_likes(self, obj, data=0, current_item=0):
        ''' Numerator update: posts number decremented if a creation in DB failed,
            *current_likes* status incremented when new like is added to a user'''
        try:
            if obj == 'like':
                '''object is  of type user_id:post_id'''
                self.current_number_of_likes += 1
                '''retrieve likelihood instance and update likes per post numerator '''
                tmp = self.retrieve_user(list(current_item)[0])
                tmp.update_likes_per_post(current_item[list(current_item)[0]], diff_likes=1)
            elif obj == 'unlike':
                self.current_number_of_likes += 1
                if not list(current_item)[0].update_likes_per_post(current_item[list(current_item)[0]], data):
                    raise CRITICAL_IN_ERROR(
                        f' Partial update taken in BOT - in addition Mismatch between server and BOT')
            elif obj == 'post':
                self.number_of_posts -= 1
            else:
                raise CRITICAL_IN_ERROR(f' Creation failure')

            return True

        except CRITICAL_IN_ERROR as e:
            logging.critical(f'{e}. Func: adjust related posts')
            return type(e).__name__

    def retrieve_user(self, update_user_id):
        try:
            for tmp in users:
                if update_user_id == tmp.id:
                    return tmp

        except CRITICAL_IN_ERROR as e:
            logging.critical(f'{e}. Func: retrieve  user')
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
                if data == 'True':
                    '''Synchronize likes status in the operate user and the user's posts'''
                    return self.adjust_related_posts_or_likes('like', 1, item_to_like)
                else:  # Like not created at all - No Mismatches
                    raise CRITICAL_BET_ERROR('Inconsistency between server tables, Mismatch between server and BOT')
            else:
                # inconsistency between Server and DB/Server  - handle separately
                raise CRITICAL_BET_ERROR('Communication failure, Mismatch between server and BOT')

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
                if data.isnumeric():
                    '''synchronize likes status in the operate user and the user's posts'''
                    return self.adjust_related_posts_or_likes('like', 1, item_to_unlike)
                else:  # Like not created at all - No Mismatches
                    raise Exception('Like was not created')
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
