#!/bin/python3
# ! Django 3.1.1

from utilities import *


def main():
    users_list_holds_posts = []  # list of users that posts where created for them

    # Hello
    print_chao('Welcome to Bot')

    try:
        ###################### Phase 1: Sign up users #######################################
        '''Stop condition:  2 options:
        1. Reaches max users required. 2. Finish all mails from mail_bank_list  '''

        ''' End of BOT action '''
        req_users = number_of_users
        if not req_users:
            raise BOT_ERROR_FINISHED('No users to create')

        if len(mail_bank_list) < req_users:
            logging.warning('list of available mails is too shorts. Func-main')

        '''create users'''
        status_msg(req_users, 'user')
        for email in mail_bank_list:
            ''' Stop when all required users created - Success stop flag'''
            my_user = User(email)  # Create instance of User class
            response = my_user.sign_up()  # Connect to server & create new user
            if not response:
                logging.warning(f'Failed to sign up user with: {my_user.email} mail. Func-main')
                del my_user
            else:
                ''' Saving  created users id in an instances list in the class and in a list '''
                users.append(my_user)
                req_users -= 1
                if not req_users or email == mail_bank_list[len(mail_bank_list) - 1]:
                    break

        ''' Error: short in created users '''
        if not users:
            raise BOT_ERROR_FINISHED('No users to create')
        elif len(users) < number_of_users:
            logging.warning('Did not create all required users. Func-main')

        ''' Final users list created in DB (Server) '''
        zero_list_flag = [False] * len(users)
        match_all_likes = [False] * len(users)
        print_userlist(users)

        ###################### End of phase 1 - user creation ###############################

        ###################### Phase 2: Create random number of posts for each user##########

        '''Stop condition:  
         1. For all created users from phase 1 posts where creating - in success or fail'''
        status_msg('post')

        post_num = 0  # Verify post creation

        for current_user in users:
            ''' For each user different max of posts'''
            req_posts = current_user.number_of_posts

            '''Login user'''
            if not current_user.login():
                logging.warning(f'Failed to sign in  to user: {current_user.id}  . Func-main')
                del current_user  # delete the instance of user
            else:
                while req_posts:
                    ''' Created posts for this user id  '''
                    response = current_user.create_post()
                    ''' Handle list of likes per post  '''
                    if response == 'CRITICAL_BET_ERROR':
                        logging.critical(
                            f'A post created to user {current_user.id} on the server, but fails to complete update in the BOT. Func-main')
                    elif response == True:
                        post_num += 1
                    else:
                        logging.warning(f'Failed to create a post to user id: {current_user.id}. Func-main')

                    req_posts -= 1

                if not post_num:
                    '''No posts, user deleted'''
                    del current_user
                    zero_list_flag.remove(current_user)
                    match_all_likes.remove(current_user)

                else:
                    users_list_holds_posts.append(current_user)

        ''' Final users list created in DB (Server) '''
        print_postlist(users_list_holds_posts)

        ###################### End of phase 2 - posts creation ### ###########################

        ###################### Phase 3: Do likes under ruls instructions ######################

        '''Stop condition: in 3 options:
        1. No user with 0 likes to one post at least . 2. All  users reached their max likes'''

        # Phase 3.1 Create list of posts for likelihood action
        ''' Dividing the list by action: => do_unlike, do_like '''
        ''' For posts already liked by current_user perform unlike , other perform like'''

        while users_list_holds_posts:
            ''' Randomly choose indexes of posts to perform like dec order of list by user id '''
            '''For each candidate:
                1. Produce a list of users with 0 likes per post
                2. Randomly decide how many posts for this likelihood iteration 
                3. Randomly decide which posts for likelihood action 
                4. Assign it to like\\unlike operation 
                5. Perform likelihood action 
                6. Handle errors type of synchronisation
                7. On going : verify End BOT operation conditions'''

            for current_candidate in users_list_holds_posts:

                '''' End of BOT action check & update status '''
                if is_final(match_all_likes, zero_list_flag,users_list_holds_posts):
                    raise BOT_FINISHED('No users with 0 likes left, or likes to do')

                ''' Number of max Likes per user for this iteration '''
                if not match_all_likes[users.index(current_candidate)]:
                    '''For a user that did not natch his max likes'''
                    print(f'WATCH',current_candidate.number_of_likes, current_candidate.current_number_of_likes)
                    req_likes = random.randint(1, (
                            current_candidate.number_of_likes - current_candidate.current_number_of_likes))

                '''Randomly 0 likes for this user at this iteration'''
                if not req_likes:
                    status_msg(current_candidate, req_likes, 'user')
                    continue

                status_msg(req_likes, current_candidate.id, 'like')

                ''' Desc user list (via no. of posts) of all users (beside current user) 
                    with at least 1 post with 0 likes  '''
                users_list_holds_posts_of_0likes = zero_post(users_list_holds_posts, current_candidate)

                ''' End of BOT action check & update status '''
                if not isinstance(users_list_holds_posts_of_0likes, list):
                    '''No optional posts to like'''
                    zero_list_flag[users.index(current_candidate)] = True
                    status_msg(current_candidate, 'zero_list')
                    if is_final(match_all_likes, zero_list_flag,users_list_holds_posts):
                        raise BOT_FINISHED('No users with 0 likes left, or likes to do')
                    continue

                ''' Randomly draw posts out of zero list, Dividing the list by action: 
                    => do_unlike, do_like, For liked posts by current_user perform unlike, other perform like
                    Data format: chosen_posts =>{user_id:post_id}'''
                action_list = choose_posts(users_list_holds_posts_of_0likes, current_candidate, req_likes)

                ''' Final list of chosen posts by action type '''
                status_msg(current_candidate, 'like')
                print_chosen_post_list(current_candidate, action_list)

                # Phase 3.2 Perform likelihood action: like and unlike ###############

                '''Login user'''
                if not current_candidate.login():
                    logging.warning(f'Failed to sign in  to user: {current_candidate.id}. Func-main ')
                else:
                    '''likelihood action for all list of posts'''
                    while req_likes and action_list:
                        for current_action in action_list:
                            '''Choose like or unlike action'''
                            if list(current_action)[0] == 'like':
                                likelihood_obj = current_candidate.do_like(current_action[list(current_action)[0]])
                            else:
                                likelihood_obj = current_candidate.do_unlike(current_action[list(current_action)[0]])

                            ''' Handle synchronise BOT - Server  '''
                            if likelihood_obj == 'CRITICAL_BET_ERROR':
                                logging.critical(
                                    f'Likelihood action to user {current_candidate.id} failed due to inconsistency '
                                    f'between  server\DB and BOT. Func-main')
                            elif likelihood_obj == 'CRITICAL_IN_ERROR':
                                logging.critical(
                                    f'Mismatch between users likes numerator for {current_candidate.id} and likes per '
                                    f'post to user: {list(current_action)[0]} in BOT and between server\DB and BOT. '
                                    f'Func-main')
                            elif likelihood_obj == True:
                                '''Set End BOT flag'''
                                zero_list_flag = [
                                    False if users_list_holds_posts.index(current_candidate) != j else True for j in
                                    range(len(users))]
                            else:
                                logging.warning(
                                    f'Failed to create a {list(current_action)[0]} to user id: {current_candidate.id}. Func-main')

                            '''Taken action removed from action_list, as a flag for BOT activity'''
                            action_list.remove(
                                current_action)
                        req_likes -= 1

                    ''' Summation for each End of user likelihood operation '''
                    print_user_total_likes_list(current_candidate)

                    ''' End of BOT action check & update status '''
                    if current_candidate.current_number_of_likes == current_candidate.number_of_likes:
                        '''No likes to distribute for this user'''
                        match_all_likes[users.index(current_candidate)] = True
                        status_msg(current_candidate,'match')
                        if is_final(match_all_likes, zero_list_flag,users_list_holds_posts):
                            raise BOT_FINISHED('No users with 0 likes left, or likes to do')

        raise BOT_FINISHED('All likes of all users distributed')
        ###################### End of phase 3 - likes done ##########################################

    except BOT_ERROR_FINISHED as e:
        print(f'{e}. Func: main')
        print_chao('BOT Mission is finished....See you')
        return

    except BOT_FINISHED as e:
        print(f'{e}. Func: main')
        print_chao('BOT Mission is finished....See you')
        return

    except Exception as e:
        print(f'{e}. Func: main')


if __name__ == '__main__':
    main()
