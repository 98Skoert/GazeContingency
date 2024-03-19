from pygaze import libscreen

class Screen():
    def __init__(self, gazeContingency, screen = None):
        if isinstance(screen, libscreen.Screen):
            self.screen = screen
        elif isinstance(screen, str):
            self.screen = libscreen.Screen()
            self.screen.draw_text(text=screen, fontsize=24)
        else:
            self.screen = libscreen.Screen()
        self.Rules = []
        self.Commands = []
        self.GC = gazeContingency

    def AddRule(self, rule, target, customBehaviour = None):
        self.Rules.append([rule,target,customBehaviour])

    def CallRules(self, frameStart):
        #this can be farbettered
        for rule, tar, cust in self.Rules:
            if rule.Evaluate(frameStart):
                if cust is None:
                    return self.GC.GotoScreen(tar)
                else:

                    return cust()

    def CallCommands(self):
        for com in self.Commands:
            com()


    #func replaceScreen
    #replaces the libscreen.Screen coupled to a GC Screen
    #useful for looping over multiple trials with the same rules
    #args:
    #       screen: GazeContingency.Screen object OR libscreen.Screen object OR string
    #
    #

    def ReplaceScreen(self, screen):
        if isinstance(screen, Screen):
            self.screen = screen.screen
        elif isinstance(screen, libscreen.Screen):
            self.screen = screen
        elif isinstance(screen, str):
            stringScreen = libscreen.Screen()
            stringScreen.draw_text(text=screen, fontsize = 24)
            self.screen = stringScreen
        else:
            raise Exception(f"{screen} is not a GazeContingency Screen, Pygaze.libscreen Screen, or string ")