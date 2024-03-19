from typing import Callable


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

