import time
import pyautogui 

"""
Functions for moving around the GOT interface and conferring titles.
"""

buttons = {
    
}

def reset_middle_screen():
    width, height = pyautogui.size()
    x, y = width // 2, height // 2
    pyautogui.moveTo(x, y, duration=0.25)

def remove_research():
    drag_down()
    if "remove_research" in buttons:
        x, y = buttons["remove_research"]
    else:
        removes = list(pyautogui.locateAllOnScreen("remove.png"))
        x, y = pyautogui.center(removes[-1]) 
        buttons["remove_research"] = (x, y)
    pyautogui.moveTo(x, y, duration=0.25)
    pyautogui.click()
    pyautogui.click()
    time.sleep(1)

def remove_lord_commander():
    drag_up()
    removes = list(pyautogui.locateAllOnScreen("remove.png"))
    x, y = pyautogui.center(removes[2]) 
    pyautogui.moveTo(x, y, duration=0.25)
    pyautogui.click()
    pyautogui.click()
    time.sleep(1)

def remove_construction():
    drag_down()
    if "remove_builder" in buttons:
        x, y = buttons["remove_builder"]
    else:
        removes = list(pyautogui.locateAllOnScreen("remove.png"))
        x, y = pyautogui.center(removes[2]) 
        buttons["remove_builder"] = (x, y)
    pyautogui.moveTo(x, y, duration=0.25)
    pyautogui.click()
    pyautogui.click()
    time.sleep(1)

def remove_training():
    drag_up()
    if "remove_training" in buttons:
        x, y = buttons["remove_training"]
    else:
        removes = list(pyautogui.locateAllOnScreen("remove.png"))
        x, y = pyautogui.center(removes[3]) 
        buttons[remove_training] = (x, y)
    pyautogui.moveTo(x, y, duration=0.25)
    pyautogui.click()
    pyautogui.click()
    time.sleep(1)

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
    pyautogui.scroll(400) 
    time.sleep(2)
    reset_middle_screen()

def drag_down():
    pyautogui.scroll(-400) 
    time.sleep(2)
    reset_middle_screen()
