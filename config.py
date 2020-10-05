# This is BOT config file

number_of_users = 2
max_posts_per_user = 4
max_likes_per_user = 5

'''Bank of optional users'''
mail_bank_list = ['alex@clearbit.com', 'anat@eby.co.il', 'jobs@twingo.com', 'libat.gold@solaredge.com',
                  'inball@nucleon.sh', 'shlomo@deeponcology.ai',
                  'taya@govreensegal.com']  # deliverable,undeliverable,riski

'''URL settings '''''
URL ="{APP_URL}:{APP_PORT}".format(APP_URL='http://127.0.0.1',APP_PORT = '8000')

users = []  # List of actual created users in Server(DB)

class BOT_ERROR_FINISHED(Exception):
    #print('No users to create')
    pass


class BOT_FINISHED(Exception):
    #print('All likes distributed, and all users has no posts witn 0 likes')
    pass


class CRITICAL_BET_ERROR(Exception):
    '''A new object (post or like) created in the server\DB
    but failed to updated in the BOT'''
    #print('Mismatch between server and BOT')
    pass


class CRITICAL_IN_ERROR(Exception):
    '''In server\DB a new object was created. Failed to update fully in:
    post per user likes numerator failed or
    user likes numerator failed to updated'''
    #print (f'In server\DB a new object was created. Failed to update fully in BOT')
    #print(f'In server\DB a new action taken, in addition, partial update taken in BOT')

    pass





