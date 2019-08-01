import time
import pyautogui

"""
Functions for moving around the GOT interface and conferring titles.
"""

memoized_buttons = {

}

REMOVE = "remove"
CONFER = "confer"

TOP = "top"
BOTTOM = "bottom"


def get_action_button_name(action_type):
    action_button = None
    if action_type == "remove":
        action_button = "remove.png"
    elif action_type == "confer":
        action_button = "confer.png"
    return action_button


def setup_top_menu_actions():
    drag_up()
    return {
        "Master of Coin": 0,
        "Lord Commander": 1,
        "Hand of the King": 2,
        "training": 3,
        "Master of Laws": 4
    }


def setup_bot_menu_actions():
    drag_down()
    return {
        "Most Devout": 0,
        "ships": 1,
        "builder": 2,
        "research": 3
    }


def perform_main_menu_action(action_type, top_or_bottom, role):

    if top_or_bottom == TOP:
        role_mapping = setup_top_menu_actions()
    elif top_or_bottom == BOTTOM:
        role_mapping = setup_bot_menu_actions

    if (action_type, role) in memoized_buttons:
        x, y = memoized_buttuons[(action_type, role)]
    else:
        action_button_name = get_action_button_name(action_type)
        all_action_buttons = list(
            pyautogui.locateAllOnScreen(action_button_name))
        action_button = all_action_buttons[role_mapping[role]]
        x, y = pyautogui.center(action_button)
        memoized_buttons[(action_type, role)] = (x, y)

    pyautogui.moveTo(x, y, duration=0.25)
    pyautogui.click()
    if action_type == REMOVE:
        pyautogui.click()
    time.sleep(1)


def reset_middle_screen():
    width, height = pyautogui.size()
    x, y = width // 2, height // 2
    pyautogui.moveTo(x, y, duration=0.25)


def remove_research():
    perform_main_menu_action(REMOVE, BOTTOM, "research")


def remove_lord_commander():
    perform_main_menu_action(REMOVE, BOTTOM, "Lord Commander")


def remove_construction():
    perform_main_menu_action(REMOVE, BOTTOM, "builder")


def remove_training():
    perform_main_menu_action(REMOVE, TOP, "training")


def confer_research(user):
    remove_research()
    confers = list(pyautogui.locateAllOnScreen("confer.png"))
    x, y = pyautogui.center(confers[-1])
    pyautogui.moveTo(x, y, duration=0.25)
    pyautogui.click()
    search_and_confer(user)


def confer_builder(user):
    remove_construction()
    confers = list(pyautogui.locateAllOnScreen("confer.png"))
    x, y = pyautogui.center(confers[-2])
    pyautogui.moveTo(x, y, duration=0.25)
    pyautogui.click()
    search_and_confer(user)


def confer_training(user):
    remove_training()
    confers = list(pyautogui.locateAllOnScreen("confer.png"))
    x, y = pyautogui.center(confers[0])
    pyautogui.moveTo(x, y, duration=0.25)
    pyautogui.click()
    search_and_confer(user)


def search_and_confer(user):
    time.sleep(2)
    pyautogui.moveTo(780, 252, duration=0.25)
    pyautogui.click()
    pyautogui.typewrite(user)

    x, y = pyautogui.center(pyautogui.locateOnScreen("search.png"))
    pyautogui.moveTo(x, y, duration=0.25)
    pyautogui.click()

    time.sleep(2)
    confers = list(pyautogui.locateAllOnScreen("confer.png"))

    # means we couldn't find a user
    if len(confers) != 3:
        # repeat of code below but this closes the window by clicking outside instead
        x, y = pyautogui.center(confers[0])
        pyautogui.moveTo(x, y, duration=0.25)
        pyautogui.click()
        raise ValueError("couldn't find given username", user)

    x, y = pyautogui.center(confers[0])
    pyautogui.moveTo(x, y, duration=0.25)
    pyautogui.click()
    time.sleep(4)

    # shouldn't still have search. if we do it means that the removal of this role wasn't processed corectly
    try:
        search = pyautogui.center(pyautogui.locateOnScreen("search.png"))
        # selects confer outside of the modal that opens
        x, y = pyautogui.center(confers[1])
        pyautogui.moveTo(x, y, duration=0.25)
        pyautogui.click()
        time.sleep(2)
        raise NameError("couldn't remove previous confer correctly")
    except TypeError as e:
        pass
    reset_middle_screen()


def drag_up():
    for _ in range(2):
        pyautogui.scroll(400)
        time.sleep(2)
        reset_middle_screen()


def drag_down():
    for _ in range(2):
        pyautogui.scroll(-400)
        time.sleep(2)
        reset_middle_screen()
