import pandas as pd
import numpy as np
from datetime import datetime
import pickle
import sys

BUNDLES_N = 4
AVG_USER_ID = 'AVG_USER_ID'


class UserState:
    """Holds current bundle of notifications for a user. The bundle will be appended and released
    according to the logic defined in Notifier.track_route()"""

    def __init__(self):
        self.bundled_daily_routs = []
        self.bundle_i = 1


class Notifier:
    """Manages user notifications"""

    def __init__(self):
        # Average daily routs arrive per user (trained)
        self.avg_day_routs = {}

        # Current user's state
        self.current_day = {}

        # Last timestamp
        self.last_timestamp = None

    @staticmethod
    def _date_str_to_ts(ts_str):
        return datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")

    def train_model(self, notifications_path, output_model_path=None):
        """Learn the model"""

        df = pd.read_csv(notifications_path, header=None)
        df.columns = ['timestamp', 'user_id', 'friend_id', 'friend_name']

        df['year_month'] = df['timestamp'].apply(lambda x: Notifier._date_str_to_ts(x).month)
        df['month_day'] = df['timestamp'].apply(lambda x: Notifier._date_str_to_ts(x).day)

        # routs per user
        user_routes = df['user_id'].value_counts()

        # days per user - print
        res = df[['user_id', 'year_month', 'month_day']].groupby(['user_id', 'year_month', 'month_day']).size()
        user_days = pd.Series([i[0] for i, _ in res.iteritems()])
        user_days = user_days.value_counts()

        # map: user=>routs per day
        for uid, user_routs in user_routes.iteritems():
            self.avg_day_routs[uid] = float(user_routs) / user_days[uid]

        # average user
        self.avg_day_routs[AVG_USER_ID] = np.mean(list(self.avg_day_routs.values()))

        if output_model_path:
            with open(output_model_path, 'wb') as f:
                pickle.dump(self.avg_day_routs, f)

    def load_model(self, model_path):
        """Load learnt model"""

        with open(model_path, 'rb') as f:
            self.avg_day_routs = pickle.load(f)

    def track_route(self, timestamp, user_id, friend_id):
        """Use the learnt model to predict the best time to message a user"""

        results = {}
        timestamp = Notifier._date_str_to_ts(timestamp)

        if user_id not in self.current_day:
            self.current_day[user_id] = UserState()

        user_state = self.current_day[user_id]
        user_state.bundled_daily_routs.append((timestamp, friend_id))

        if (len(user_state.bundled_daily_routs) >= self.avg_day_routs.get(user_id, self.avg_day_routs[AVG_USER_ID]) / BUNDLES_N)\
                and user_state.bundle_i < BUNDLES_N:
            """ Release bundle for the previous bundle period """

            results[user_id] = (timestamp, user_state.bundled_daily_routs)
            user_state.bundle_i += 1
            user_state.bundled_daily_routs = []

        if ((self.last_timestamp is not None)
                and (timestamp.day > self.last_timestamp.day or
                     timestamp.month > self.last_timestamp.month or
                     timestamp.year > self.last_timestamp.year)):
            """ Release bundle for the previous day """

            print("day change")
            self._release_all_notifications(results, timestamp)

        self.last_timestamp = timestamp
        return results

    def _release_all_notifications(self, results, timestamp):
        for uid, ustate in self.current_day.items():
            if len(ustate.bundled_daily_routs) > 0:
                results[uid] = (timestamp, ustate.bundled_daily_routs)
                self.current_day[uid] = UserState()

    def release_all_notifications(self):
        results = {}
        self._release_all_notifications(results, self.last_timestamp)
        return results


def simulate(train_notifications_path, model_path, track_notifications_path):
    """Simulate incoming friends notifications"""

    notifier = Notifier()

    if train_notifications_path:
        print("training ...")
        notifier.train_model(train_notifications_path, model_path)
    else:
        print("loading model ...")
        notifier.load_model(model_path)

    print("simulate tracking ...")
    df = pd.read_csv(track_notifications_path, header=None)
    df.columns = ['timestamp', 'user_id', 'friend_id', 'friend_name']

    delays = []
    for _, msg in df.iterrows():
        results = notifier.track_route(msg['timestamp'], msg['user_id'], msg['friend_id'])
        parse_results(results, delays)

    print("getting rest notifications")
    results = notifier.release_all_notifications()
    parse_results(results, delays)

    print(np.mean(delays))


def parse_results(results, delays):
    """Parse bundles gathering delays for the subsequent evaluation"""

    for uid, result in results.items():
        send_message(uid, result)
        for notif_time, _ in result[1]:
            delays.append((result[0] - notif_time).seconds / 60)


def send_message(uid, notifications):
    """This function can be overridden to provide actual message send functionality"""

    print("sending bundle", uid, notifications[0])
    for n in notifications[1]:
        print((str(n[0]), n[1]))
    print()


def debug():
    """Learn the users model and simulate incoming friends notifications"""

    path = '/notifications.csv'
    model_path_ = '/model.pkl'
    simulate(path, model_path_, path)


def release():
    """Load pre learnt model and simulate incoming friends notifications"""

    model_path_ = 'model.pkl'
    notif_path = sys.argv[1]
    simulate(None, model_path_, notif_path)


if __name__ == "__main__":
    release()
