
def repl():
    while True:
        print eval(raw_input('> '))


def entry_point(argv):
    repl()
    return 0


def target(driver, *args):
    return entry_point, None
