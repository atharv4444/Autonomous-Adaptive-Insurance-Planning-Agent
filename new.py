goal_achieved = False

def observe():
    print("Observing...")

def plan():
    print("Planning...")

def act():
    print("Acting...")

def evaluate():
    global goal_achieved
    print("Evaluating...")
    goal_achieved = True

while not goal_achieved:
    observe()
    plan()
    act()
    evaluate()