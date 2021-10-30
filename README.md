# Bot: Server Tradecore
 
2 components in TradeCore system:
1. BOT written  in Python 2. Rest Api SERVER based on Django framework.

-General: BOT  initiates actions  to be performed on the SERVER; sign_up, login, create post related to specific user and like \ unlike posts. The  activity is restricted to ground rules of max users, max posts creation and a likelihood action maximum. 
All communication parts fully supported by requests library on the BOT part and HttpResponse\HttpResponse from the SERVER side.

-Main FLow:
From main BOT->Phase I: Create users up to defined maximum, based on pre-prepered mail list. This users is the base for next stage. One iteration for the stage.
               Phase II: Login & create posts till the max allowed, per user.manufactiors list of users, by their posts. One iteration for the stage.
               Phase III starts: Repeatable iteration of likelihood actions, via randomly chosen posts. Strart by the user who owned max posts, and not match his max  
                         likelihood action (like or unlike). Each post can be liked ones by a user, but multiplay times, for unlike\like all over again.
               BOT stops if there are no more 0 likes to a user, in any of his posts or max likes of all users are done.             

-Server
Owns 3 entities: User, Post and Like. Each entity is considered as a table.

Post entity holds a many-To-many relation to the User table, through Like. Each user can have a lot of posts, each post connected only to one user.

Like entity holds a many-To-many relation to both Post and User entities (implemented by FK). Meanning:each user can have lots of likes to a lot of posts. 
Each like is unique to a {user_pk, post_pk} combination.

Detailes:
User: 3 fields(properties) mail,fullname and no_of_related_posts. In the back there is an auto PK of id. 
Method of sign_in (create)- rollout 3 process: mail validation (via https://hunter.io ), enrichment of user data based on clearbit (https://clearbit.com/enrichment), and encryption key based on JWT, for an authenticate user operation.
Method of inc_posts, that executes when a new post added.
In addition there are some administration utilities which handle the login, decode and encode of the JWT code. 

Post: 3 fields(properties) user (ManyToManyField to User with  through='Like'), post_text, number of likes per post. In the back there is an auto PK of id.
Method create_post which enforces number_of_posts increment in User related class.
In order to create a post, a user must login and authenticate via JWT code.

Like: 4 fields(properties) user (FK to User), post(FK to Post) [with uniqu_together flag to verify only one "like" per post&user] and extra data of create_date and boolean_flag to sign that one like at least done. In the back there is an auto PK of id.
Methods of create_like,  do_like and perform unlike. Likelihood action enforces number_of_likes increment\decrement in the related Post.
* In order to create a post, a user must login and authenticate via JWT code.
*On this implementation, There is a usage of m2m , and an extra related like data, which controls by through. The option to use only 2 tables is clear, 
     but 3 Entities are maintain in order to give the opuronity to reveal an extra data on Likelihood action, as interval of time fro posted post by the 
     count of like etc. Each like created on post creation, with a False flag. on do_like is set on, and on undo likw it sets off. From one hand it couse overloaded of like        instanses, which might not be in use. on the othe hand it open the utility to the user in advance and not on-the-spot. 

* The administration function gives the ultimate service when a non-specific instance is operating. 

* In order to use clearbir and hunter tokens are used. it is from https://hunter.io and  (https://clearbit.com/enrichment). needed to be add when clone is done.
Each phase ende with maximum verification of synocronysem, between tables on the SERVER and in between SERVER and BOT.

-BOT 

A User class holds up most actions, and some administrative functions. The BOT (main &Utilities & Configuration files) are the same for 2 implementation options.

The BOT manipulates the server on 3 separate phases, which the BOT interacts on an api layer to the server.  Each server utility is supported by a BOT activity: sign_in, Log_in, create posts and do/undo likes (which supported as append\remove from likes per post list). Only BOT aggreigstion activities kept in the BOT.

-User class holds the BOT following properties:  Id (updated from server), email (initiate from the bot to a new server user creation) ,num_of_posts user     
  allowed to be created (random value in the interval defined in the config.py parameter) , num_of_likes user allowed to do (random value in the interval defined in the 
  config.py parameter) and current likes_status. Significant property for each user is post_per_likes_list of the form of data structure: {post_id:[user_likes this_post_id]}. 

-Likelihood phase include like or unlike, depending if a chosen post is not liked by the candidate, already. Each user likelihood phase, starts with login, and only if 
 it's approved, The likelihood action itself starts. A. Collect all posts available for likelihood (their user has at least 1 0 likes post)- Zero list. 
 B. Randomly choose from Zero_list, how many posts and which ones- Chosen list. 
 C. For each post an action determines upon If candidate already liked this post or not (User can not like his own posts). Data structure is of the form :{Like or 
    unlike:{candidate:{user_id:post_id}}}. 
 D. Till now, all made offline with astored data on the BOT. Now a Login & likelihood action made after comunicate with the server.

-Exceptions: BOT_FINISHED_NO_ERROR\BOT_FINISHED_ERROR raised as for finishing BOT process.
                    CRITICAL_BET_ERROR raised as for mismatch between BOT and SERVER. 
                    CRITICAL_ERROR raised as for mismatch between BOT and SERVER and in between components in the BOT.

- After each action on the server, consistentecy operations are taken to keep match aggrigations to the server.

 START:             create                                         login                                     Notes

User: Create: Creation fails on server->instance on the bot deleted. General nontes: Number of users up to max_users from config file.
______________________________________________________________________________________________________________________________________________________
Post: Create: Creation fails on server->instance deleted. Append post id to post_per_likes_list. Login: If fails on login to server->instance deleted.
      General notes: Handling inconsistency between 2 components or mismatches in the Bot: Append element to post_per_likes_list. Error flag is the defaule 
      value of post_id = -1. Number of posts defined, per user, on user creation, up to max_posts from config file.  
_______________________________________________________________________________________________________________________________________________________                    Like: Create: Creation fails on server->instance will not be deleted (there are posts alread Update element to post_per_likes_list). 
      Login failes,continue to next user. General nontes: Number of likes are defined on user creation from config file. Must match max_likes or other stop flags.
                 
END:                  create                                         login                                     Notes

-Decisions & assumption:

Permissions:    Delete User Post or Like is not implemented. number of likes updated up and down to the limit of 0. 
                No edit utility, to all entities.
    		          Create was granted to all 3. 
                Admin user has all permissions, which operate via browser , by entering a user&password, which represented at setting.py doc.

DB:             Use of inner Django sqLite DB.

Authentication: On user creation a JWT code is determined. At the beggining of each activity a login is required. Only one user is activated in the system, at a time.
                so logout functionality is not required. 

Handle errors:  Mostly handled by logging on the warning level. As a decision only mismatch data consistency between models on the server or between the server and the  
                BOT receives an explicite exception and considers a critical severity error. Error in the server side not necessarily should receive the same severity, 
                as in the BOT side, due to differences rolls. Each error prompt twice, on general message of the action status and second time for specific related user 
                & post & like on board.

Config file:    Is of *.py type, which brings some flexibility to import, manipulate the params as variables, that can be changed during the progress of                 
                the program, (has its downsides) and contains other defined parameters.

Complexity:     Aspects of this issue leads to order the list of users & posts to_be_liked in descending order, prior to activity, so the rule of likelihood activity  
                order will be maintained and consuem the minimum (time & computer efforts). Other aspects of complexity were not taken under consideration, and is a 
                places to improve.

Furthermore improvements:
    -  A. improve Complexity. B. Uniform the logging-Exception handle. C. Format DateTime field. D. This implementation divide the web activity by phases, which in
       reality is not a clear division. The random likelihood operation can easily mplemented for the other 2 phases, on creating users and posts, in a mixture.
