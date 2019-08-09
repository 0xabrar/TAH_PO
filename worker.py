import time
import traceback
import sqlite3
from got import (
    confer_role_action, remove_role_action,
    TRAINING, SHIPS, RESEARCH, BUILDER
)

conn = sqlite3.connect("queue.db")
c = conn.cursor()


# 3 minutes min time guaranteed
BUFF_MIN_TIME = 180


def buff_time_remaining(compare):
    now = int(time.time())
    result = now - compare
    if result > BUFF_MIN_TIME:
        return 0
    return BUFF_MIN_TIME - result


'''
c.execute("""CREATE TABLE current (role text primary key, user text, start integer, mention text)""")
c.execute("""CREATE TABLE logs (user text primary key, role text, state text, timestamp integer, mention text)""")
c.execute("""CREATE TABLE times (last_entry integer)""")
'''
c.execute("""CREATE TABLE blacklist (user text primary key)""")

"""
Functions for interacting with the DB.
"""


def get_blacklist():
    return list(c.execute("SELECT * FROM blacklist"))


def add_to_blacklist(user):
    stmt = "REPLACE INTO blacklist (user) VALUES(%s)" % (user)
    c.execute(stmt)
    conn.commit()


def remove_from_blacklist(user):
    c.execute("DELETE FROM blacklist WHERE user=(?)", (user,))
    conn.commit()


def get_last_time():
    stmt = "SELECT * FROM times"
    return list(c.execute(stmt))


def update_last_time():
    stmt = "DELETE FROM times"
    c.execute(stmt)
    conn.commit()

    now = int(time.time())
    stmt = "REPLACE INTO times (last_entry) VALUES(%d)" % (now)
    c.execute(stmt)
    conn.commit()


def add_to_queue(user, role, mention):
    now = int(time.time())
    stmt = "REPLACE INTO logs (user, role, state, timestamp, mention) VALUES(\"%s\", \"%s\", \"%s\", %d, \"%s\")" % (
        user, role, "queued", now, mention)
    c.execute(stmt)
    conn.commit()


def remove_from_queue(user):
    c.execute("DELETE FROM logs WHERE user=(?)", (user,))
    conn.commit()


def clear_queue():
    c.execute("DELETE FROM logs")
    conn.commit()


def clear_current():
    c.execute("DELETE FROM current")
    conn.commit()


def update_current(user, role, time, mention):
    stmt = "REPLACE INTO current (role, user, start, mention) VALUES(\"%s\", \"%s\", %d, \"%s\")" % (
        role, user, time, mention)
    c.execute(stmt)
    conn.commit()


def update_state_processing(user, role, state, timestamp, mention):
    stmt = "REPLACE INTO logs (user, role, state, timestamp, mention) VALUES(\"%s\", \"%s\", \"%s\", %d, \"%s\")" % (
        user, role, state, timestamp, mention)
    c.execute(stmt)
    conn.commit()


def get_queue():
    logs = list(c.execute(
        "SELECT * FROM logs WHERE state=\"queued\" OR state=\"processing\" ORDER BY timestamp"))
    logs = [format_request(request) for request in logs]
    return logs


def get_current():
    return format_current(list(c.execute("SELECT * FROM current")))


def get_completed():
    logs = list(
        c.execute("SELECT * FROM logs WHERE state=\"completed\" ORDER BY timestamp"))
    logs = [format_request(request) for request in logs]
    return logs


def get_not_found():
    logs = list(
        c.execute("SELECT * FROM logs WHERE state=\"not_found\" ORDER BY timestamp"))
    logs = [format_request(request) for request in logs]
    return logs


def get_unknown():
    logs = list(c.execute(
        "SELECT * FROM logs WHERE state=\"unknown_error\" ORDER BY timestamp"))
    logs = [format_request(request) for request in logs]
    return logs


"""
Maintain consistency when updating
"""


def full_reset(mention):
    remove_role(TRAINING, mention)
    remove_role(RESEARCH, mention)
    remove_role(SHIPS, mention)
    remove_role(BUILDER, mention)


def remove_role(role, mention):
    remove_role_action(role)
    update_current(None, role, 0, None)


"""
Formatting
"""


def format_current(current):
    result = {}
    for item in current:
        result[item[0]] = {
            "user": item[1],
            "start": item[2],
            "mention": item[3]
        }
    return result


def format_request(request):
    return {
        "user": request[0],
        "role": request[1],
        "state": request[2],
        "timestamp": request[3],
        "mention": request[4]
    }


"""
Updating large queues
"""


def process_request(request):
    user = request["user"]
    role = request["role"]
    mention = request["mention"]
    update_state_processing(user, role, "processing",
                            request["timestamp"], mention)

    current = get_current()
    # remove an existing role for a user if they already have that
    for item in current.keys():
        if user == current[item]["user"]:
            remove_role(item, mention)

    timestamp = request["timestamp"]
    mention = request["mention"]

    try:
        confer_role_action(user, role)
    except ValueError as e:
        update_state_processing(user, role, "not_found", timestamp, mention)
        raise Exception("user not found")
    except NameError as e:
        update_state_processing(
            user, role, "unknown_error", timestamp, mention)
        full_reset(mention)
        return

    now = int(time.time())
    update_current(user, role, now, mention)
    update_state_processing(user, role, "completed", timestamp, mention)


def process_queue():
    logs = get_queue()
    current = get_current()

    for request in logs:
        role = request["role"]
        compare_role = current.get(role, {"user": "None", "start": 0})
        if buff_time_remaining(compare_role["start"]) > 0:
            continue

        process_request(request)
        return


if __name__ == "__main__":
    print("starting worker")
    while True:
        try:
            time.sleep(5)
            now = int(time.time())
            last_time = get_last_time()[0][0]
            if now - last_time < 45:
                continue
            process_queue()
            update_last_time()
        except Exception as e:
            traceback.print_exc()

    conn.close()
