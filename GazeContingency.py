from __future__ import annotations
from pygaze import libscreen
from pygaze import libtime
from pygaze import liblog
from pygaze import libinput
from pygaze import eyetracker


from typing import Callable




class Screen():
    def __init__(self, gazeContingency: GazeContingency, screen = None):
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


class GazeContingency:
    def __init__(self, display: libscreen.Display, eyetracker: eyetracker.EyeTracker, framerate: int):

        self.disp = display
        self.track = eyetracker
        self.loop = True
        
        self.timeOnScreen = 0
        self.framerate = framerate
        self.frameTime = 1000/framerate

        self.screens = {}
        self.screenCurrent = None

        self.rules = []



    def Loop(self, libTime, startingScreen):
        self.GotoScreen(startingScreen)

        startTime = libTime.get_time()
        frameStart = startTime
        while(self.loop):

            frameStart = libTime.get_time()
            self.CallRules(frameStart)

            frameTime = libTime.get_time() - frameStart

            if frameTime > self.frameTime:
                self.timeOnScreen += frameTime

            else:
                libTime.pause(self.frameTime - frameTime)
                self.timeOnScreen += self.frameTime

            



    #function for adding a screen. 
    #args:
    #   screen:     PyGaze.libscreen.Screen object
    #   screentype: string
    #               one of the allowed screens from dict screenTypes

    def AddScreen(self, screen, screentype):
        if screentype in self.screens:
            self.screens[screentype].ReplaceScreen(screen)
        else:
            if isinstance(screen, Screen):
                self.screens[screentype] = screen 

            elif isinstance(screen, libscreen.Screen):
                self.screens[screentype] = Screen(self, screen)

            elif isinstance(screen, str):
                self.screens[screentype] = Screen(self, screen)
            else: 
                raise Exception(f"{screen} is not a GazeContingency Screen, Pygaze.libscreen Screen, or string ")
    
    #function for adding rules
    #args:
    #   screen:     PyGaze.libscreen.Screen object
    #   target:     PyGaze.libscreen.Screen object
    #   rule:       GazeContingency.Rule object
    def AddRule(self, screenType, target, rule):
        if screenType != None:
            self.screens[screenType].AddRule(rule, target, None)
        else:
            self.rules.append([rule, target])

    def AddRuleCommand(self, screenType, targetCommand, rule):
        if screenType != None:
            self.screens[screenType].AddRule(rule, None, targetCommand)
        else:
            self.rules.append([rule, targetCommand])

    def AddOnScreenEnterCommand(self, screenType, command):
        if screenType in self.screens:
            self.screens[screenType].AddRule(command)  
        else:
            Exception (f"AddOnScreenEnterCommand received arg {screenType}, which is not a key in the screens dict")


    def CallRules(self, time):
        #call all rules coupled to the GC obj
        for rule, target in self.rules:
            if rule.Evaluate(time):
                if isinstance(target, str):
                    self.GotoScreen(target)
                if isinstance(target, Callable[[]]):
                    return target()
        #call all rules coupled to the current screen
        self.screenCurrent.CallRules(time)

    #function for getting a Screen object, even if it does not exist
    def Screen(self, screenType):
        if screenType in self.screens:
            return self.screens[screenType]
        else:
            try:
                tempScreen = libscreen.Screen()
                tempScreen.draw_text(text=f"{screenType}", fontsize=24)
                return Screen(self, tempScreen)
            except:
                tempScreen.draw_text(text=f"error: {screenType} is not a string", fontsize=24)


    def GotoScreen(self, screenType: str, final = False):
        if final:
            self.loop = False

        self.track.log("showing screen %s" % screenType)
        self.timeOnScreen = 0
        self.screenCurrent = self.Screen(screenType)
        self.disp.fill(self.screenCurrent.screen)
        self.disp.show()




#class Rule:
#saves a reference to a function, and Evaluates the function when called by the GazeContingentScreen
#is coupled to two screens by the AddRule function called from a GazeContingentScreen
#I was definitely sober when I wrote this
class Rule:
    def __init__(self, interval: int, func:Callable[[], bool]):
        self.f = func
        self.interval = interval
        self.nextCall = 0

    #no function description
    #TODO:  move this evaluation to GCScreen
    #       because optimalisation is life
    def Evaluate(self, time):
        if time > self.nextCall:
            self.nextCall = time + self.interval
            return self._Evaluate()

    def _Evaluate(self):
        res = self.f()
        return(res)
