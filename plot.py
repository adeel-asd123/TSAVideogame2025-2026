from main import Game
from panda3d.core import AsyncFuture
class Plot(Game):
    async def plotLine(self):
        self.researchNode() = None
        await self.plotAsync
        pass
    async def conditionBasedAdvancer(self):
        if self.plotConditionFunctions[0]:
            pass
    def __init__(self):
        super().__init__()
        self.plotAsync = AsyncFuture()
        self.advanceAsync = AsyncFuture()
        self.eventAdvanceFunc = {'finish': lambda: self.plotAsync.set_result(None), 'reset': lambda: self.plotAsync == AsyncFuture()}
        self.eventDoneFunc = {'finish': lambda: self.advanceAsync.set_result(None), 'reset': lambda: self.advanceAsync == AsyncFuture()}
        self.plotConditionFunctions = [lambda: True if self.researchNode.getName() == self.collision_queue.sortEntries().getEntry(1).getIntoNode().getName() else False]
        self.plotEvents = {"researchGoalAchieved": self.plotConditionFunctions[0]}