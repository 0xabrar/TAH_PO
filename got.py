import time
import pyautogui

"""
Functions for moving around the GOT interface and conferring titles.
"""

memoized_buttons = {

}

"""
Button type constants.
"""
REMOVE = "remove"
CONFER = "confer"

TOP = "top"
BOTTOM = "bottom"

"""
Role constants
"""
MASTER_OF_COIN = "Master of Coin"
LORD_COMMANDER = "Lord Commander"
HAND_OF_THE_KING = "Hand of the King"
MASTER_OF_LAWS = "Master of Laws"
MOST_DEVOUT = "Most Devout"

TRAINING = "training"
SHIPS = "ships"
BUILDER = "builder"
RESEARCH = "research"


def get_action_button_name(action_type):
    action_button = None
    if action_type == REMOVE:
        action_button = "remove.png"
    elif action_type == CONFER:
        action_button = "confer.png"
    return action_button


TOP_ROLES = {
    MASTER_OF_COIN: 0,
    LORD_COMMANDER: 1,
    HAND_OF_THE_KING: 2,
    TRAINING: 3,
    MASTER_OF_LAWS: 4
}

BOTTOM_ROLES = {
    MOST_DEVOUT: 0,
    SHIPS: 1,
    BUILDER: 2,
    RESEARCH: -1
}


def setup_top_menu_actions():
    drag_up()
    return TOP_ROLES


def setup_bot_menu_actions():
    drag_down()
    return BOTTOM_ROLES


def perform_main_menu_action(action_type, top_or_bottom, role):

    if top_or_bottom == TOP:
        role_mapping = setup_top_menu_actions()
    elif top_or_bottom == BOTTOM:
        role_mapping = setup_bot_menu_actions()

    if (action_type, role) in memoized_buttons:
        x, y = memoized_buttons[(action_type, role)]
    else:
        action_button_name = get_action_button_name(action_type)
        all_action_buttons = list(
            pyautogui.locateAllOnScreen(action_button_name))
        action_button = all_action_buttons[role_mapping[role]]
        x, y = pyautogui.center(action_button)
        memoized_buttons[(action_type, role)] = (x, y)

    pyautogui.moveTo(x, y, duration=0.25)
    pyautogui.click()
    time.sleep(5)


def reset_middle_screen():
    width, height = pyautogui.size()
    x, y = width // 2, height // 2
    pyautogui.moveTo(x, y, duration=0.25)


def remove_role_action(role):
    top_or_bottom = BOTTOM if role in BOTTOM_ROLES.keys() else TOP
    perform_main_menu_action(REMOVE, top_or_bottom, role)


def confer_role_action(user, role):
    remove_role_action(role)
    top_or_bottom = BOTTOM if role in BOTTOM_ROLES.keys() else TOP
    perform_main_menu_action(CONFER, top_or_bottom, role)
    search_and_confer(user, role)


def search_and_confer(user, role):
    time.sleep(10)
    pyautogui.moveTo(780, 252, duration=0.25)
    pyautogui.click()
    pyautogui.typewrite(user)

    x, y = pyautogui.center(pyautogui.locateOnScreen("search.png"))
    pyautogui.moveTo(x, y, duration=0.25)
    pyautogui.click()

    time.sleep(5)
    confers = list(pyautogui.locateAllOnScreen("confer.png"))

    top_roles = {LORD_COMMANDER, MASTER_OF_COIN, HAND_OF_THE_KING}
    # means we couldn't find a user
    if role in top_roles:
        if len(confers) != 4:
            # repeat of code below but this closes the window by clicking outside instead
            x, y = pyautogui.center(confers[0])
            pyautogui.moveTo(x, y, duration=0.25)
            pyautogui.click()
            raise ValueError("couldn't find given username", user)
    elif len(confers) != 3:
        # repeat of code below but this closes the window by clicking outside instead
        x, y = pyautogui.center(confers[0])
        pyautogui.moveTo(x, y, duration=0.25)
        pyautogui.click()
        raise ValueError("couldn't find given username", user)

    x, y = pyautogui.center(confers[0])
    pyautogui.moveTo(x, y, duration=0.25)
    pyautogui.click()
    time.sleep(5)

    # shouldn't still have search. if we do it means that the removal of this role wasn't processed corectly
    try:
        search = pyautogui.center(pyautogui.locateOnScreen("search.png"))
        # selects confer outside of the modal that opens
        x, y = pyautogui.center(confers[1])
        pyautogui.moveTo(x, y, duration=0.25)
        pyautogui.click()
        time.sleep(5)
        raise NameError("couldn't remove previous confer correctly")
    except TypeError as e:
        pass
    reset_middle_screen()

def full_reset():
    pyautogui.press('f5')
    time.sleep(30)
    start = int(time.time())

    # waiting for page to load
    while True:
        try: 
            x, y = pyautogui.center(pyautogui.locateOnScreen("close.png"))
            break
        except TypeError as e:
            compare = int(time.time())
            if compare - start > 300:
                raise TypeError("page didn't load")
            time.sleep(10)
    
    for _ in range(2):
        try:
            x, y = pyautogui.center(pyautogui.locateOnScreen("close.png"))
            pyautogui.moveTo(x, y, duration=0.25)
            pyautogui.click()
            reset_middle_screen()
            time.sleep(3)
        except NameError as e:
            pass

    # world button
    pyautogui.moveTo(1554, 839, duration=0.25)
    pyautogui.click()
    time.sleep(30)

    # coordinate search button
    pyautogui.moveTo(1573, 356, duration=0.25)
    pyautogui.click()
    time.sleep(2)

    # search x coordinate
    pyautogui.moveTo(945, 490, duration=0.25)
    pyautogui.click()
    for _ in range(3):
        pyautogui.press("backspace")
    pyautogui.typewrite("467")
    
    # search y coordinate
    pyautogui.moveTo(1092, 493, duration=0.25)
    pyautogui.click()
    for _ in range(3):
        pyautogui.press("backspace")
    pyautogui.typewrite("496")

    # click search enter button
    pyautogui.moveTo(1005, 634, duration=0.25)
    pyautogui.click()
    time.sleep(10)

    # click KL
    pyautogui.moveTo(904, 559, duration=0.25)
    pyautogui.click()
    time.sleep(2)

    # click enter
    pyautogui.moveTo(1201, 806, duration=0.25)
    pyautogui.click()
    time.sleep(2)

    # click titles 
    pyautogui.moveTo(1346, 266, duration=0.25)
    pyautogui.click()
    time.sleep(2)

def drag_up():
    for _ in range(2):
        pyautogui.scroll(400)
        time.sleep(4)
        reset_middle_screen()

def drag_down():
    for _ in range(2):
        pyautogui.scroll(-400)
        time.sleep(4)
        reset_middle_screen()