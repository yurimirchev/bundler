# Problem definition
We are platform for outdoor enthusiasts where you can follow your friends and like-minded people to be informed about their latest tours. Some have only a few friends, others follow hundreds of users. At the moment every time a tour is uploaded, all followers get a push notification on their mobile.
We identified that this can lead to a huge amount of notifications for some users. That’s not acceptable as those users will be annoyed and eventually uninstall the app. We came up with the idea of bundling notifications to reduce the amount of notifications we send. That means we need to wait a bit to collect notifications until we can send those bundles. But we also know how important it is to send notifications as soon as possible: users want to know about the tours of their friends as soon as possible and start to talk about it.
Our goal is
1. To not send more than 4 notifications a day to a user (should happen only few times)
2. To keep sending delay minimal

# Algorithm
The proposed algorithm is based on the hypothesis that a user’s daily friends notifications arrive according to distribution close to uniform. I calculate average of friends notifications the user gets per day. Then divide this number by 4 and this will be a number of friends notifications in a bundle.
During user lifetime I gather friends notifications for a user and when the bundle arrives to its limit it is released and sent to the user. The last (the 4th bundle) is released at the end of the day instead of when its messages number exceeds the limit.
Due to the fact that we learn user’s daily “habits” means that the algorithm is supervised. And the learnt user’s daily average friends notifications is the model. In case of a new user which is not a part of the model his mean number of daily friends notifications is calculated as an average of all existing users. Such a user is called an “average user”.

# Program execution
Install python 3.5.X
Run “pip install numpy pandas“
Place bundle_alg.py and model.pkl to the same folder
Run “python bundle_alg.py <path-to-notifications-csv-file>”
# Output interpretation
The program’s output example:

sending bundle E734 2017-08-01 12:55:33
('2017-08-01 04:29:04', 'E0A8’)
('2017-08-01 04:32:35', '2A79’)
('2017-08-01 05:19:21', 'D89F’)

Means that we are sending a bundle of messages to a user with ID ‘E734’ 
at time 2017-08-01 12:55:33. Then the bundle itself follows: 
notification from friend with ID 'E0A8’ which was sent at time 2017-08-01 04:29:04
notification from friend with ID '2A79’ which was sent at time 2017-08-01 04:32:35
etc.


# Evaluation
To check the algorithm performance from the data mining point of view the evaluation was conducted. I defined an evaluation measurement as an average delay time which passed between route was announced (by a friend) and the time it was actually sent (to a user). This value should be minimized. Current training error is 210 min. It means that it takes in average 3.5 hours for a user to know about his friend’s route announcement.

# Future work
### Algorithm evaluation extensions
1. Calculate test error dividing user data to training and testing parts considering timestamps. Calculate statistical significance using Unpaired TTest between different algorithm versions.
2. Calculate evaluation error per user. Calculate statistical significance using Paired TTest between different algorithm versions
### Algorithm extensions
1. Using hypothesis that friends notifications are not distributed uniformly, learn model, clustering the notifications by their timestamps. And gather notifications which belong to a current time cluster and when a notification belongs to the next cluster release all the notifications from the current cluster to the user as a bundle. Since we know the exact number of clusters = 4, create them by K-Means algorithm. But Hierarchical Clustering can be used too.
2. The same idea as in (1) but for each cluster probability function is calculated and we release messages which belong to the current cluster if probability that there will be more routes notifications to the current cluster is relatively small (less than 0.5)
3. Update user model as his friends number is being changed
4. Create model per day. May be friends routes notification has different behaviour let’s say on Sunday rather than on Monday?
5. Create model per month period (week 1, weeks 2 & 3, week 4). May be by the end of the month there is different behaviour about of notifications than in the beginning. 
6. Take into account user’s activity with specific friend (If the user already went to a ride with some friend it means that this friend is important) so this fact can influence to reduce the time delay. So that the user will be messaged as soon as possible.
7. Take into account the actual friend’s route time. So that if a friend goes to the route in one month there is no hurry to notify the user about that ride.
8. To ensure algorithm scalability the user current state (i.e. bundled notifications) can be kept in Redis - in memory data structure store.
# Conclusions
The proposed algorithm uses the most basic assumption about universe distribution of daily friends announcements. It can serve as a base-line. The strength of the algorithm proposed is that it is very straightforward and easy to understand but uses a very basic assumption about uniform friends daily notifications distribution. So, more research directions can be considered to check other hypothesis. Also, the algorithm is not adaptive to user profile changes (e.g. new friends).
