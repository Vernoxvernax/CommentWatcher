import time
import schedule
import os.path
import feedparser
import sqlite3
import gotify
import configparser
from datetime import datetime


def config_check():
    def reading_settings(header, setting, template):
        try:
            variable = config[header][setting]
            if variable == template:
                print("Please change \"{}\" in app/config.yml.".format(setting))
                exit()
            else:
                print("\"{}\" has been set to \"{}\"".format(setting, variable))
            return variable
        except:
            if setting != "delay":
                config[header][setting] = template
            else:
                config[header][setting] = "120"
            with open("app/config.yml", 'w') as configfile:
                config.write(configfile)
            print("Please edit app/config.yml and restart the script.")
            exit()

    def header_check(header):
        try:
            config[header]
        except:
            config[header] = {}
            with open("app/config.yml", 'w+') as configfile:
                config.write(configfile)
    global domain, meow_uploader, gotify_url, gotify_token, gotify_title, gotify_priority
    print("Checking for config...")
    config = configparser.ConfigParser()
    if not os.path.isdir("app"):
        os.mkdir("app")
    if os.path.isfile("app/config.yml"):
        print("Found config.yml.")
        config.read("app/config.yml")
        header_check("CommentsWatcher")
        domain = reading_settings("CommentsWatcher", "url", "<INSERT URL LIKE 'https://meow.com/?page=rss&u='>")
        meow_uploader = reading_settings("CommentsWatcher", "user", "<INSERT MEOW-USERNAME>")
        header_check("Gotify")
        gotify_url = reading_settings("Gotify", "gotify_url", "<INSERT GOTIFY-URL HERE>")
        gotify_token = reading_settings("Gotify", "token", "<INSERT GOTIFY-TOKEN HERE>")
        gotify_title = reading_settings("Gotify", "notification_title", "<INSERT NOTIFICATION TITLE HERE>")
        gotify_priority = int(reading_settings("Gotify", "priority", "<PRIORITY OF MESSAGE (0-15)>"))
        print("Settings have been successfully injected.")
        input()
    else:
        config["CommentsWatcher"] = {}
        config["CommentsWatcher"]["url"] = "<INSERT URL LIKE 'https://meow.com/?page=rss&u='>"
        config["CommentsWatcher"]["user"] = "<INSERT MEOW-USERNAME>"
        config["Gotify"] = {}
        config["Gotify"]["url"] = "<INSERT GOTIFY-URL HERE>"
        config["Gotify"]["token"] = "<INSERT GOTIFY-TOKEN HERE>"
        config["Gotify"]["notification_title"] = "<INSERT NOTIFICATION TITLE HERE>"
        config["Gotify"]["priority"] = "<PRIORITY OF MESSAGE (0-15)>"
        with open("app/config.yml", 'w') as configfile:
            config.write(configfile)
        print("Created config file.\nPlease edit config.yml and restart the script.")
        exit()


def db_check():
    print("Checking for database...")
    if os.path.isfile("app/commentswatcher.db"):
        print("Everything existent.")
    else:
        print("Creating database file.")
        database = open("app/commentswatcher.db", 'x')
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
    connection = sqlite3.connect("app/commentswatcher.db")
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
                print("The following release got {} new comments:\n {}".format(
                    comment_number_list[x] - db_result[0][2], title_list[x]))
                cursor.execute('''UPDATE UPLOADS SET Comments = {} WHERE Link="{}";'''.format(
                    comment_number_list[x], link_list[x]))
                # SENDING NOTIFICATIONS
                gotify_send(comment_number_list[x] - db_result[0][2], title_list[x])
        else:
            print("Found new release")
            cursor.execute('''INSERT INTO UPLOADS VALUES ("{}", "{}", {})'''.format(
                title_list[x], link_list[x], comment_number_list[x]))
    if not cursor:
        print("Fail :(")
    else:
        print("Checking again in 10 minutes.")
    connection.commit()
    connection.close()


def gotify_send(comments, title):
    gotify_server = gotify.gotify(
        base_url=gotify_url,
        app_token=gotify_token,
    )
    gotify_server.create_message(
        "{} just received {} new comments.".format(title, comments),
        title=gotify_title,
        priority=gotify_priority,
    )
    return


if __name__ == '__main__':
    config_check()
    db_check()
    get_user_page()
    all_good = True
    schedule.every(10).minutes.do(get_user_page)
    while all_good:
        schedule.run_pending()
        time.sleep(1)
