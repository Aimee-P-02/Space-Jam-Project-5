from CollideObjectBase import SphereCollideObject
from panda3d.core import Loader, NodePath, Vec3, TransparencyAttrib
from direct.task.Task import TaskManager
from typing import Callable
from direct.task import Task
from SpaceJamClasses import Missile
from direct.gui.OnscreenImage import OnscreenImage



class SpaceShip(SphereCollideObject):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float, manager: Task, accept: Callable[[str, Callable], None]):
        super(SpaceShip, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0,0,0), 3)
        self.accept = accept
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)

        self.modelNode.setName(nodeName)
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)
        
        self.taskMgr = manager
        self.loader = loader

        self.render = parentNode
        self.setKeyBinding()
        self.reloadTime = .25
        self.missileDistance = 4000 # until the missile explodes
        self.missileBay = 1 # only one missile in the missile bay to be launched

        self.taskMgr.add(self.CheckIntervals, "checkMissiles", 34)
        self.EnableHud()


    def Thrust(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.applyThrust,"forward-thrust")
        else:
            self.taskMgr.remove("forward-thrust")

    def applyThrust(self,task):
        rate = 5
        trajectory = self.render.getRelativeVector(self.modelNode, Vec3.forward())
        trajectory.normalize()
        self.modelNode.setFluidPos(self.modelNode.getPos() + trajectory * rate)

        return Task.cont

    def setKeyBinding(self):
        #all key bindings here
        self.accept("space",self.Thrust, [1])
        self.accept("space-up",self.Thrust, [0])

        self.accept("arrow_left", self.LeftTurn, [1])
        self.accept("arrow_left-up", self.LeftTurn, [0])

        self.accept("arrow_right", self.RightTurn, [1])
        self.accept("arrow_right-up", self.RightTurn, [0])

        self.accept("arrow_up", self.TurnUp, [1])
        self.accept("arrow_up-up", self.TurnUp, [0])

        self.accept("arrow_down", self.TurnDown, [1])
        self.accept("arrow_down-up", self.TurnDown, [0])

        self.accept("a", self.RollLeft, [1])
        self.accept("a-up", self.RollLeft, [0])

        self.accept("s", self.RollRight, [1])
        self.accept("s-up", self.RollRight, [0])

        self.accept("f", self.Fire)

    def LeftTurn(self,keyDown):
        if keyDown:
            self.taskMgr.add(self.applyLeftTurn, "left-turn")

        else:
            self.taskMgr.remove("left-turn")

    def applyLeftTurn(self, task):
        rate = 0.5
        self.modelNode.setH(self.modelNode.getH() + rate)

        return Task.cont
    # turn right
    def RightTurn(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.applyRightTurn, "right-turn")

        else:
            self.taskMgr.remove("right-turn")

    def applyRightTurn(self, task):
        rate = 0.5
        self.modelNode.setH(self.modelNode.getH() - rate)

        return Task.cont



    #turn up

    def TurnUp(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.applyTurnUp, "up-turn")

        else:
            self.taskMgr.remove("up-turn")

    def applyTurnUp(self, task):
        rate = 0.5
        self.modelNode.setP(self.modelNode.getP() + rate)

        return Task.cont

    #turn down

    def TurnDown(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.applyTurnDown, "down-turn")

        else:
            self.taskMgr.remove("down-turn")

    def applyTurnDown(self, task):
        rate = 0.5
        self.modelNode.setP(self.modelNode.getP() - rate)

        return Task.cont

    #roll right

    def RollRight(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.applyRollRight, "roll-right")

        else:
            self.taskMgr.remove("roll-right")

    def applyRollRight(self, task):
        rate = 0.5
        self.modelNode.setR(self.modelNode.getR() - rate)

        return Task.cont

    #roll left

    def RollLeft(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.applyRollLeft, "roll-left")

        else:
            self.taskMgr.remove("roll-left")

    def applyRollLeft(self, task):
        rate = 0.5
        self.modelNode.setR(self.modelNode.getR() + rate)

        return Task.cont
    
    def Fire(self):
        if self.missileBay:
            travRate = self.missileDistance
            aim = self.render.getRelativeVector(self.modelNode, Vec3.forward()) # the direction the spaceship is facing
            # normalize to avoid math mistakes
            aim.normalize()
            fireSolution = aim * travRate
            inFront = aim * 150
            travVec = fireSolution + self.modelNode.getPos()
            self.missileBay -= 1
            tag = "Missile"+ str(Missile.missileCount)
            posVec = self.modelNode.getPos() + inFront # spawn missile in front of nose of ship
            currentMissile = Missile(self.loader,"./Assets/Phaser/phaser.egg", self.render, tag, posVec, 4.0)
            Missile.Intervals[tag] = currentMissile.modelNode.posInterval(2.0, travVec, startPos = posVec, fluid = 1)
            Missile.Intervals[tag].start()

        else:
            if not self.taskMgr.hasTaskNamed("reload"):
                print("initialize reload")
                self.taskMgr.doMethodLater(0, self.Reload, "reload")
                return Task.cont
            

    def Reload(self, task):
        if task.time > self.reloadTime:
            self.missileBay += 1

            if self.missileBay > 1:
                self.missileBay = 1

            print("reload complete")

            return Task.done
        
        elif task.time <= self.reloadTime:
            print("reload proceeding...")

            return Task.cont
        

    def CheckIntervals(self, tasK):
        for i in Missile.Intervals:
            if not Missile.Intervals[i].isPlaying():
                Missile.cNodes[i].detachNode()
                Missile.fireModels[i].detachNode()

                del Missile.Intervals[i]
                del Missile.fireModels[i]
                del Missile.cNodes[i]
                del Missile.collisionSolids[i]

                print(i + " has reached the end of its fire solution")

                break
                
        return Task.cont
    

    def EnableHud(self):
        self.Hud = OnscreenImage(image = "./Assets/HUD/center.png", pos = Vec3(0,0,0), scale = 0.3)
        self.Hud.setTransparency(TransparencyAttrib.MAlpha)

                
        
        

        
    


                                



