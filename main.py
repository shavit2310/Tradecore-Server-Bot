#!/bin/python3
# ! Django 3.1.1

from utilities import *


# Hello
def _print_chao(name):
    print(f'Hi, {name}')

def main():
    users_list_holds_posts = []  # list of users that posts where created for them
    posts_available_for_likes = []  # list of posts for likelihood action
    action_list = []  # list of users that hat at least 1 0 likes post

    # Hello
    _print_chao('Welcome to Bot')

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
        logging.info('This is the list of users that created. Func-main')
        print_userlist(users)

        ###################### End of phase 1 - user creation ###############################

        ###################### Phase 2: Create random number of posts for each user##########
        '''Stop condition:  
         1. For all created users from phase 1 posts where creating - in succ or fail'''

        for current_user in users:
            req_posts = current_user.number_of_posts  # For each user different max of posts

            '''Login user'''
            if not current_user.login():
                logging.warning(f'Failed to sign in  to user: {current_user.id}  . Func-main')
                del current_user  # delete the instance
            else:
                while req_posts:
                    ''' Created posts for this user id  '''
                    response = current_user.create_post()
                    ''' Handle list of likes per post  '''
                    if response == 'CRITICAL_BET_ERROR':
                        logging.critical(f'A post created to user {current_user.id} '
                                         f'on the server, but fails to complete update in the BOT. Func-main')
                    elif not(response.isnumeric()):
                        logging.warning(f'Failed to create a post to user id: {current_user.id}. Func-main')

                    req_posts -= 1

                users_list_holds_posts.append(current_user)

        ''' Final users list created in DB (Server) '''
        logging.info('This is the list of users that posts were created for them. Func-main')

        print_postlist(users_list_holds_posts)

        ###################### End of phase 2 - posts creation ### ###########################

        ###################### Phase 3: Do likes under ruls instructions ######################

        '''Stop condition: in 3 options:
        1. No user with 0 likes to one post at least . 2. All  users reached their max likes'''

        # Phase 3.1 Create list of posts for likelihood action
        ''' Dividing the list by action: => do_unlike, do_like '''
        ''' For posts already liked by current_user perform unlike , other perform like'''


        while not users_list_holds_posts or not action_list:
            ''' End BOT Action check: All users achieved their max_likes distribution'''
            '''                       No post_with_0_likes list left'''

            ''' Randomly choose indexes of posts to perform like dec order of list by user id '''
            '''For each candidate:
                1. Produce a list of users with 0 likes+per post
                2. Chose randomly a req_likes posts 
                3. Assign it to like\\unlike operation 
                4. Perform action 
                5. Handle errors type of synchronisation
                6. While going on: verfay end BOT operation conditions'''
            for current_candidate in users_list_holds_posts:

                ''' End BOT flag '''
                if current_candidate.current_number_of_likes == current_candidate.number_of_likes:
                    '''No likes to distribute for this user'''
                    users_list_holds_posts.pop()

                ''' Number of max Likes per user  '''
                '''optionally be random number of likes, each iteration'''
                req_likes = current_candidate.number_of_likes

                ''' Desc user list (by no. of posts) of all users with at least 1 post with 0 likes  '''
                users_list_holds_posts_of_0likes = zero_post(users_list_holds_posts, current_candidate)

                ''' End of BOT action '''
                if not isinstance(users_list_holds_posts_of_0likes, list):
                    '''No optional posts to like'''
                    raise BOT_FINISHED('No users with 0 likes left')

                ''' To draw randomly posts out of the list, Dividing the list by action: => do_unlike, do_like '''
                ''' For posts already liked by current_user perform unlike , other perform like'''
                # Chosen_posts =>{user_id:post_id}
                action_list = choose_posts(users_list_holds_posts_of_0likes, current_candidate, req_likes)

                ''' Final list of chosen posets and rout of action phase '''
                logging.info(f'This is the list of posts to act, fro {current_candidate} user')
                print_chosenpost_list(current_candidate, action_list)

                # Phase 3.2 Perform likelihood action: like and unlike

                '''Login user'''
                if not current_candidate.login():
                    logging.warning(f'Failed to sign in  to user: {current_candidate.id}. Func-main ')
                else:
                    while req_likes:
                        ''' Continue till likelihood operation for current user finished '''
                        for current_action in action_list:
                            if list(current_action)[0] == 'like':  # Like Action by flag
                                likelihood_obj = current_candidate.do_like(current_action[list(current_action)[0]])
                            else:
                                likelihood_obj = current_candidate.do_unlike(current_action[list(current_action)[0]])

                            ''' Handle synchronise BOT   '''
                            if likelihood_obj == 'CRITICAL_BET_ERROR':
                                logging.critical(
                                    f'A like/unlike to user {current_candidate.id} posted on the server, \
                                    but fails to complete update in the BOT. Func-main')
                            elif likelihood_obj == 'CRITICAL_IN_ERROR':
                                logging.critical(f'Mismatch between users likes numerator for {current_candidate.id} '
                                                 f'and likes per post to user: {list(current_action)[0]} '
                                                 f'and between server\DB and BOT. Func-main')
                            elif likelihood_obj == True:  # SUCC
                                action_list.pop(0)  # Taken action removed from list, as a flag for BOT activity
                            else:
                                logging.warning(f'Failed to create a {list(current_action)[0]} to user id: {current_candidate.id}. Func-main')
                        req_likes -= 1

                    ''' End of user likelihood operation '''
                    print_user_total_likes_list(current_candidate)
        ###################### End of phase 3 - likes done ##########################################

    except BOT_ERROR_FINISHED as e:
        print(e)
        _print_chao('BOT Mission is finished....See you')
        return

    except BOT_FINISHED as e:
        print(e)
        _print_chao('BOT Mission is finished....See you')
        return

    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
