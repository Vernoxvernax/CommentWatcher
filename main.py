import time
import schedule
import os.path
from datetime import datetime
import feedparser
import sqlite3
import configparser


def config_check():
    global domain, meow_uploader
    print("Checking for config...")
    config = configparser.ConfigParser()
    if os.path.isfile("config.yml"):
        print("Found config.yml.")
        config.read("config.yml")
        try:
            meow_uploader = config["CommentWatcher"]["user"]
        except:
            config["CommentWatcher"]["user"] = "<INSERT MEOW-USERNAME>"
            with open("config.yml", 'w') as configfile:
                config.write(configfile)
            print("Please edit config.yml and restart the script.")
            exit()
        try:
            domain = config["CommentWatcher"]["url"]
        except:
            config["CommentWatcher"]["url"] = "<INSERT URL LIKE 'https://meow.com/?page=rss&u='>"
            with open("config.yml", 'w') as configfile:
                config.write(configfile)
            print("Please edit config.yml and restart the script.")
            exit()
        if meow_uploader != "<INSERT MEOW-USERNAME>" and meow_uploader != "":
            print("Watching comments of the following user: \"{}\".".format(meow_uploader))
        else:
            print("Please edit the 'user' setting in config.yml!")
            exit()
        if domain != "<INSERT URL LIKE 'https://meow.com/?page=rss&u='>" and domain != "":
            print("On the following site {}.".format(domain))
        else:
            print("Please edit the 'url' setting in config.yml!")
            exit()
    else:
        config["CommentWatcher"] = {}
        config["CommentWatcher"]["url"] = "<INSERT URL LIKE 'https://meow.com/?page=rss&u='>"
        config["CommentWatcher"]["user"] = "<INSERT MEOW-USERNAME>"
        with open("config.yml", 'w') as configfile:
            config.write(configfile)
        print("Created config file.\nPlease edit config.yml and restart the script.")
        exit()


def db_check():
    print("Checking for database...")
    if os.path.isdir("db"):
        if os.path.isfile("commentwatcher.db"):
            print("Everything existent.")
        else:
            print("Creating database file.")
            database = open("commentwatcher.db", 'x')
            database.close()
    else:
        print("Creating database...")
        os.makedirs("db")
        database = open("commentwatcher.db", 'x')
        database.close()


def get_user_page():
    global timeout
    print("Requesting at {}.".format(datetime.now().strftime("%H:%M:%S")))
    timeout = 0
    url = "{}{}".format(domain, meow_uploader)
    try:
        rss = feedparser.parse(url)
        timeout = 0
    except:
        if timeout > 10:
            print("Connection failed more than 10 times, waiting 1 hour.")
            time.sleep(3600)
        print("Requesting information failed. Retrying in 10 minutes.")
        timeout = timeout + 1
    else:
        print("  Connection: SUCCESS")
        if "'status': 200" not in str(rss):
            print("Cannot parse information.")
            return
        timeout = 0
        parsing_inf(rss)
    return


def parsing_inf(rss):
    entries = rss["entries"]
    title_list = []
    link_list = []
    comment_number_list = []
    for item in entries:
        item_index = entries.index(item)
        item_title = entries[item_index]["title"]
        item_link = entries[item_index]["link"]
        item_comment_number = entries[item_index]["nyaa_comments"]
        title_list.append(item_title)
        link_list.append(item_link)
        comment_number_list.append(int(item_comment_number))
    # FOR DEBUGGING PURPOSES
    # for x in link_list:
        # print("{} - {} - comments: {}".format(title_list[link_list.index(x)],
        #                                       x, comment_number_list[link_list.index(x)]))
    connection = sqlite3.connect("commentwatcher.db")
    cursor = connection.cursor()
    createTable = '''CREATE TABLE if NOT exists UPLOADS(
    Title VARCHAR(100), Link VARCHAR(100), Comments int
    )'''
    cursor.execute(createTable)
    for x in range(len(link_list)):
        # print("Computing item:", link_list[x])
        cursor.execute('''SELECT * FROM UPLOADS WHERE Link="{}"'''.format(link_list[x]))
        db_result = list(map(list, cursor.fetchall()))
        # DEBUGGING SHIT:
        # print(type(db_result[0][2]), type(comment_number_list[x]))
        if db_result:
            if db_result[0][2] != comment_number_list[x]:
                print("The following upload got {} new comments:\n {}".format(
                    comment_number_list[x] - db_result[0][2], title_list[x]))
                cursor.execute('''UPDATE UPLOADS SET Comments = {} WHERE Link="{}";'''.format(
                    comment_number_list[x], link_list[x]))
        else:
            print("Found new release")
            cursor.execute('''INSERT INTO UPLOADS VALUES ("{}", "{}", {})'''.format(
                title_list[x], link_list[x], comment_number_list[x]))
    if not cursor:
        print("Fail :(")
    connection.commit()
    connection.close()


if __name__ == '__main__':
    config_check()
    db_check()
    all_good = True
    schedule.every(10).minutes.do(get_user_page)
    while all_good:
        schedule.run_pending()
        time.sleep(1)
