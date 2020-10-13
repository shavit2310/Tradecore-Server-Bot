# BOT-SERVER-TRADECORE
 
2 components in TradeCore system:
1. BOT written  in Python 2. Rest Api SERVER based on Django framework.

-General: BOT  initiates actions  to be performed on the SERVER;: sign_up, login, create post related to the user and like and unlike though posts. The  activity is restricted to ground rules of max users, posts creation and maximum for likelihood action. 
All communication parts fully supported by response on the BOT part and HttpResponse\HttpResponse on the SERVER side.

-Main FLow:
From main BOT->Phase I: create users up to max allowed: users list that is the base for next stage. Phase II: login & create posts till the max allowed: create list of users, with posts. From this list Phase 3 starts: a repeatable iteration of  deriving posts owned by users with at least one post with 0 likes + choosing randomly posts for likelihood action+split these posts to like/unlike under the verification if the current candidate has already liked the post or nor. BOT stops if there are no more 0 likes to a user, in any of his posts or max likes of all users are done.

-Server
Owns 3 entities: User, Post and Like. Each entity is considered as a table.

Post entity holds a one-To-many relation  to the User table. Each user can have a lot of posts, each post connected only to one user.

Like entity holds a many-To-many relation to both Post and User entities. Meaning:each user can have lots of likes to a lot of posts. Each like is unique to a user_pk combined with post_pk.

User: 3 fields(properties) mail,fullname and no_of_related_posts. In the back there is an auto 
PK of id. 
Method of sign_in (create)- rollout 3 process: mail validation (via https://hunter.io ), enrichment of user data based on clearbit (https://clearbit.com/enrichment), and encryption key based on JWT, for an authenticate user operation.
Method of inc_posts, that operates only when a post object is created.
In addition there are some administration utilities which handle the login, decode and encode of the JWT code. 

Post: 3 fields(properties) user (FK to User), post_text, number of likes per post.
In the back there is an auto PK of id.
Method of create_post which enforces number_of_posts increment in User related class.
In order to create a post, a user must login and authenticate via JWT code.

Like: 3 fields(properties) user (FK to User), post(FK to Post),like_text.   
            In the back there is an auto PK of id.
Method of create_like (do_like), method of delete like(do_unlike) which enforces number_of_likes increment\decrement in Post related class.
In order to create a post, a user must login and authenticate via JWT code.

* This implementation of one2many between User:Post tables and one2one Like:{Post&User} could have a many2many field in Post table, and no need of the Like table. But then an extra data on each like that is done, avoided. 
The administration function gives the ultimate service when a non-specific instance is operating. (The choice to put it in views , as a connection phase declined, due to two reasons: views distribute the functionality, not a platform to operate it, furthermore that it is only one app. It can be considered otherwise for multi connected apps that use these utilities, also.

In order to use clearbir and hunter tokens are used. it is from https://hunter.io and  (https://clearbit.com/enrichment). needed to be add when clone is done.
Each phase ende with maximum verification of synocronysem, between tables on the SERVER and in between SERVER and BOT.

-BOT 

A User class holds up most actions, and some administrative functions.

The BOT manipulates the server on 3 separate phases, which the BOT interacts on an api layer to the server.  Each server utility is supported by a BOT activity: sign_in, Log_in, create posts and create/delete likes (do/undo likes). And an aggregation data kept in the BOT.

-User class in the BOT holds the following properties:
  Id (updated from server), email (initiate a create new user in the server) ,num_of_posts user     
  allowed to be created (random value in the interval comes from the config parameter) , 
  num_of_likes user allowed to do (random value in the interval comes from the config 
  parameter) and current likes_status.a significant property post_per_likes_list
 List, which  holds dictionaries: post_id:num_likes.  That property controls likelihood proces. 
-Likelihood phase is like or unlike, depending if a chosen post is not likesby the candidate. This  
 section starts with a user created list, that transforms to a zero_list posts, of all users with at 
 least 1 post with 0 likes.posts are randomly chosen (chosen_list), and action determines upon If 
 the candidate already liked this post, his action will be unlike (action_list).Action_list data 
 structure is of the form :{Like or unlike:{candidate:{user_id:post_id}}}

-Exceptions: BOT_FINISHED\BOT_ERROR_FINISHED raised as for finishing BOT process.
                    CRITICAL_BET_ERROR raised as for mismatch between BOT and SERVER. 
                    CRITICAL_ERROR raised as for mismatch between BOT and SERVER and in 
                                                 between components in the BOT.

- After each action on the server, consistent updates were taken to match the recent updates.

 START:             create                                         login                                     Notes

User: Create: Creation fails on server->instance del. General nontes: Number of users up to max_users from config file.
______________________________________________________________________________________________________________________________________________________
Post: Create: Creation fails on server->instance del. Append element to post_per_likes_list. Login:Fails on login to server->instance del.
      General nontes: Handling inconsistency between 2 components or mismatches in the Bot: Append element to post_per_likes_list, post_id = -1.
      Number of posts defined on user creation, up to max_posts from config file.  
_______________________________________________________________________________________________________________________________________________________                    Like: Create: Creation fails on server->instance will not deleted, there are posts alread Update element to post_per_likes_list. Login: Continue to next. 
      General nontes: Number of likes are defined on user creation from config file. Must match max_likes or other stop flags.
                 
END:                  create                                         login                                     Notes

-Decisions & assumption:

Permissions:    Delete from User or Post  tables are restricted, only from Like entities.
                Edit utility is not provided to all entities.
    		          Create was granted to all 3. 
                Admin user has all permissions, which operate via browser , by entering a user&password, which represented at setting.py doc.
DB:             Usen inner Django sqLite DB.
Authentication: On user creation a JWT code is determined. For each activity a login is required, once, at the beginning. Only one user is activated in the system,  so  
                logout functionality is not required. 
Handle errors:  Mostly handled by logging on the warning level. As a decision only mismatch data consistency between models on the server or between the server and the BOT 
                causes to  raise a critical severity error. In a definition error in the server side not necessarily should receive the same severity, as in the BOT    
                side,due to differences rolls. Each error prompt twice, on general message of the action status and second time for specific related user & post & like 
                on board.
Config file:    This is of .py type, which brings some flexibility to import, approach the configuration params as variables, that can be changed during the progress of                 the program, (has its downsides) and contains other defined parameters.
Complexity:     Aspects of this issue leads to order the list of users & posts to_be_liked in descending order, prior to activity, so the rule of likelihood activity  
                order will be maintained in less time and computer consuming. Other aspects of complexity were not taken under consideration, and is a places to improve.

Furthermore improvements:
    -  A. improve Complexity. B. Segment limitation error to handle. C. Rollback when commit is 
       not performed completely. D. Uniform the logging-Exception handle. 
