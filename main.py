# /// script
# dependencies = [
#    "panda3d",
# ]
# ///

'''
This is Doomed to Europa
A game made for TSA Videogame design 2025-2026 
'''
__author__ = ''


import os
import random
import math
import sys
from direct.showbase.Transitions import Transitions
from direct.actor.Actor import Actor
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
import direct.showbase.PhysicsManagerGlobal
from direct.showbase.DirectObject import DirectObject
from direct.controls.InputState import InputState
from direct.particles.ParticleEffect import ParticleEffect
import direct.gui.DirectGuiGlobals as DGG
from panda3d.ai import AIWorld, AICharacter
from panda3d.core import (
    Camera,
    PandaSystem,
    FrameBufferProperties, 
    WindowProperties,
    GraphicsOutput, 
    GraphicsPipe,
    StringStream,
    AsyncFuture,
    LVecBase3f,
    LVecBase4f,
    LPoint3f, 
    NodePath,
    TextNode, 
    CollisionTraverser, 
    CollisionNode, 
    CollisionHandlerPusher,  
    CollisionBox,
    LVector3, 
    CollisionRay, 
    BitMask32, 
    CollisionHandlerQueue,
    loadPrcFileData,
    CollisionTraverser,
    BitMask32,
    TransparencyAttrib,
    CardMaker,
    SamplerState,
    VirtualFileSystem,
    Filename,
    DirectionalLight,
    AmbientLight,
    Camera,
    OrthographicLens,
    Texture,
    TexturePool,
    Vec3,
    Vec4,
    Shader,
    CollisionHandlerEvent
)
from direct.gui.DirectGui import (
    OnscreenImage,
    OnscreenText, 
    DirectButton,
    DirectSlider,
    DirectScrolledFrame,
    DirectLabel,
    DirectFrame,
    DirectEntry,
    DirectWaitBar
)
loadPrcFileData('', 'gl-version 4 1')
'''
The camera controller is a class that handles the movement and rotation of the camera in the game.
This is the core of the camera, and it is responsible for handling the input from the user and updating the camera accordingly.
The default values are set to 9 for velocity and 0.2 for mouse sensitivity, and the initial position of the camera is set to (-0.5, -12, 7.7).
The default view is First Person. I will add a third person view later
'''
class CameraControllerBehaviour(DirectObject):
    _instances = 0
    def __init__(self, camera, velocity=9, gravity=-2, mouse_sensitivity=0.2, initial_pos=(0, 0, 0), lockPitch = False, showbase=None):
        self._camera = camera
        self._velocity = velocity
        self._mouse_sensitivity = mouse_sensitivity
        self._keys = None
        self._input_state = InputState()
        self._lockPitch = lockPitch
        self._heading = 0.0
        self._pitch = 0.0
        self._yaw = 0.0
        self._roll = 0.0
        self._prev_mouse = None
        self._showbase = base if showbase is None else showbase
        self._gravity = LVector3(0, 0, gravity)  # Set gravity vector pointing downward
        self._instance = CameraControllerBehaviour._instances
        CameraControllerBehaviour._instances += 1
        self._camera.setPos(*initial_pos)
        # Set the initial position of the camera

    def setup(self, keys={
        'w':"forward", 
        's':"backward",
        'a':"left",
        'd':"right",
        'space':"up",
        'e':"down"
    }):
        self._keys = keys
        for key in self._keys:
            self._input_state.watchWithModifiers(self._keys[key], key)

        self._showbase.disableMouse()
        
        self._showbase.taskMgr.add(self.update, "UpdateCameraTask" + str(self._instance))
    
    def rewatch(self, keys=None, mouse_sensitivity=.2):
        if keys is not None:
            self._keys = keys
        for key in self._keys:
            self._mouse_sensitivity = mouse_sensitivity
            self._showbase.taskMgr.add(self.update, "UpdateCameraTask" + str(self._instance))
            self._input_state.watchWithModifiers(self._keys[key], key)
    
    def destroy(self):
        self.disable()
        self._input_state.delete()

        del self

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, velocity):
        self._velocity = velocity
    
    @property
    def mouse_sensitivity(self):
        return self._mouse_sensitivity

    @mouse_sensitivity.setter
    def mouse_sensitivity(self, sensitivity):
        self._mouse_sensitivity = sensitivity

    def disable(self):
        self._showbase.taskMgr.remove("UpdateCameraTask" + str(self._instance))

        props = WindowProperties()
        props.setCursorHidden(False)

        self._showbase.win.requestProperties(props)
                
    def update(self, task):
        dt = globalClock.getDt()
        
        # Get mouse movement for rotation
        md = self._showbase.win.getPointer(0)
        x = md.getX()
        y = md.getY()
        #center_x = self._showbase.win.getXSize() // 2
        #center_y = self._showbase.win.getYSize() // 2

        if self._prev_mouse is not None:
            prev_x, prev_y = self._prev_mouse
            self._yaw = self._yaw - (x - prev_x) * self._mouse_sensitivity
            self._pitch = self._pitch - (y - prev_y) * self._mouse_sensitivity
        self._prev_mouse = (x, y)

        # Clamp or lock the pitch to prevent camera flipping over
        self._pitch = 0 if self._lockPitch else max(-89, min(89, self._pitch))
        
        # Set the camera's orientation
        self._showbase.camera.setHpr(self._yaw, self._pitch, self._roll)
        
        # Access the camera's lens and set the focal length
        lens = self._showbase.cam.node().getLens()
        lens.setFocalLength(0.25)
        
        # Calculate the position increment
        pos_increment = self._velocity * dt
        
        # Handle keyboard input for movement
        if  self._input_state.isSet('forward'):
            self._showbase.camera.setY(self._showbase.camera, pos_increment)

        if  self._input_state.isSet('backward'):
            self._showbase.camera.setY(self._showbase.camera, -pos_increment)

        if  self._input_state.isSet('left'):
            self._showbase.camera.setX(self._showbase.camera, -pos_increment)

        if  self._input_state.isSet('right'):
            self._showbase.camera.setX(self._showbase.camera, pos_increment)

        if  self._input_state.isSet('up'):
            self._showbase.camera.setZ(self._showbase.camera, pos_increment)

        if  self._input_state.isSet('down'):
            self._showbase.camera.setZ(self._showbase.camera, -pos_increment)
        
        self.cam_pos = self._showbase.camera.getPos(self._showbase.render)
        # Apply gravity to the camera's position
        (self.cam_pos) += self._gravity * min(dt, 1/64.0)
        
        # Update the camera's position
        self._showbase.camera.setPos(self.cam_pos)

        return Task.cont
class EnemyController():
    def __init__(self,  Game: 'Game', showbase=None):
        self.showbase = base if showbase is None else showbase
        self.EnemyModelDict = {}
        self.EnemyAIDotDict = {}
        self.EnemyCollisionDict = {}
        self.EnemyColliderPathDict = {}
        self.EnemyAICharDict = {}
        self.EnemyAIBehaviourDict = {}
        self.EnemyHealthDict = {}
        self.EnemyAnimControlDict = {}
        self.EnemyDict = {'model':self.EnemyModelDict,
                          'ai_dot':self.EnemyAIDotDict,
                          'collision':self.EnemyCollisionDict,
                          'collision_path':self.EnemyColliderPathDict,
                          'ai_char':self.EnemyAICharDict,
                          'ai_behaviour':self.EnemyAIBehaviourDict,
                          'health':self.EnemyHealthDict,
                          }
        self.EnemyAIWorld = AIWorld(self.showbase.render)
        self.EnemyCollisionHandler = CollisionHandlerEvent()
        self.EnemyCollisionHandler.addInPattern('into-camera')
        self.showbase.accept("into-camera",self.DamagePlayer)

        self.gameInstance = Game
        
        if hasattr(self.gameInstance, 'levelDone'):
            delattr(self.gameInstance, 'levelDone')

        #Because it will spam message in update
        self.Messagesent = False
        self.Run = True
        self._gravity = LVector3(0, 0, -2)
        self.EnemyCount = 0
        self.waveCount = 1
        self.Font = self.showbase.loader.loadFont('assets/fonts/propaganda.ttf')
    async def setup(self, modelpath, extraAnims, num, height, health, waves= 5, changePerWave=1):
        self.waveMethod = AsyncFuture()
        self.num = num
        self.Run = True
        # Creating the wave count
        self.WaveCounttext = OnscreenText(text="Wave: 1", pos=(0,0.9), scale=0.1)
        self.WaveCounttext.setFont(self.Font)
        for i in range(waves):
            for j in range(self.num):
                if self.waveCount > i:
                    continue    
                if self.Run == False:
                    print('Break')
                    break
                # Set up models and make them loop animations
                
                self.EnemyModelDict['enemy' + str(j)] = Actor(modelpath, extraAnims if extraAnims is not None else None)
                self.EnemyModelDict['enemy' + str(j)].loop(self.EnemyModelDict['enemy' + str(j)].getAnimNames()[0])
                self.EnemyModelDict['enemy' + str(j)].reparentTo(self.showbase.render)
                self.EnemyModelDict['enemy' + str(j)].setPos(random.randint(-100, 100), random.randint(-100, 100), random.randint(height[0], height[1]) if isinstance(height, tuple) else height)
                
                # Set up shaders, pretty custom


                # We need to use a place holder model because the model will point at the user, so we just set position of the actual model
                self.EnemyAIDotDict['enemy' + str(j)] = self.showbase.loader.loadModel("assets/models/aidotupdater.bam")
                self.EnemyAIDotDict['enemy' + str(j)].reparentTo(self.showbase.render)
                self.EnemyAIDotDict['enemy' + str(j)].setPos(random.randint(-100, 100), random.randint(-100, 100), random.randint(height[0], height[1]) if isinstance(height, tuple) else height)
                
                # Collision
                self.EnemyCollisionDict['enemy' + str(j)] = CollisionNode('enemy' + str(j))
                self.EnemyCollisionDict['enemy' + str(j)].addSolid(CollisionBox(LPoint3f(2, 0, 9), 4,3,12))
                self.EnemyColliderPathDict['enemy' + str(j)] = self.EnemyModelDict['enemy' + str(j)].attachNewNode(self.EnemyCollisionDict['enemy' + str(j)])

                # AI
                self.EnemyAICharDict['enemy' + str(j)] = AICharacter('enemy' + str(j), self.EnemyAIDotDict['enemy' + str(j)], 10, 5, 5)
                self.EnemyAIWorld.addAiChar(self.EnemyAICharDict['enemy' + str(j)])
                self.EnemyAIBehaviourDict['enemy' + str(j)] = self.EnemyAICharDict['enemy' + str(j)].getAiBehaviors()
                self.EnemyAIBehaviourDict['enemy' + str(j)].pursue(self.showbase.camera)
                self.EnemyAIBehaviourDict['enemy' + str(j)].arrival(1)
                self.EnemyHealthDict['enemy' + str(j)] = health

                # Add collisions
                self.showbase.cTrav.addCollider(self.EnemyColliderPathDict['enemy' + str(j)], self.EnemyCollisionHandler)
                self.gameInstance.pusher.addCollider(self.EnemyColliderPathDict['enemy' + str(j)], self.EnemyModelDict['enemy' + str(j)])
            if self.waveCount > i:
                continue
            else:
                await self.waveMethod
                self.waveMethod = AsyncFuture()
                self.WaveCounttext.setText("Wave: " + str(i+2))
                self.waveCount += 1
                self.Messagesent = False
                self.num += changePerWave
        self.destroy()
        self.gameInstance.levelDone = None
    def DamagePlayer(self, collision='nothing'):
        for i in range(len(self.EnemyDict['model'])+1):
            if 'enemy' + str(i) in str(collision) and 'camera' in str(collision):
                self.gameInstance.PlayerHull -= 1
    def EnemyHit(self, enemy):
        if not self.EnemyDict['model'][enemy.getName()].isEmpty():
            self.EnemyDict['health'][enemy.getName()] -= 1
            AnimControl = self.EnemyDict['model'][enemy.getName()].getAnimControl('hit')
            if AnimControl.isPlaying():
                return None
            else:
                AnimControl.setPlayRate(.5)
                self.EnemyDict['ai_behaviour'][enemy.getName()].pauseAi('all')
                self.EnemyDict['model'][enemy.getName()].play('hit')
    def MainUpdate(self):
        self.EnemyAIWorld.update()
        for enemy, aidot in zip(self.EnemyDict['model'].values(), self.EnemyDict['ai_dot'].values()):
            if not enemy.isEmpty() and not aidot.isEmpty():
                dt = globalClock.getDt()
                aidotpos = aidot.getPos()
                (aidotpos) += self._gravity * min(dt, 1/64.0)
                aidot.setPos(aidotpos)
                enemy.setH((aidot.getH())-180)
                enemy.setPos(aidotpos)
        for key in list(self.EnemyDict['health'].keys()):
            if self.EnemyDict['health'][key] <= 0:
                self.EnemyDict['model'][key].cleanup()
                self.EnemyDict['ai_dot'][key].removeNode()
                self.EnemyAIWorld.removeAiChar(key)
                self.EnemyDict['ai_behaviour'][key].removeAi(key)
                self.gameInstance.cTrav.removeCollider(self.EnemyDict['model'][key])
                self.gameInstance.pusher.removeCollider(self.EnemyDict['collision_path'][key])
                del self.EnemyDict['model'][key]
                del self.EnemyDict['ai_dot'][key]
                del self.EnemyDict['collision'][key]
                del self.EnemyDict['ai_char'][key]
                del self.EnemyDict['ai_behaviour'][key]
                del self.EnemyDict['health'][key]
                self.EnemyCount += 1
        
        if hasattr(self, 'waveMethod') and self.EnemyDict['model'] == {} and not self.Messagesent:
            self.Messagesent = True
            self.waveMethod.set_result(None)
        
        for enemy in list(self.EnemyDict['model'].values()):
            key = list(self.EnemyDict['model'].keys())[list(self.EnemyDict['model'].values()).index(enemy)]
            if not enemy.isEmpty() and not enemy.getAnimControl('hit').isPlaying() and self.EnemyDict['ai_behaviour'][key].behaviorStatus('pursue') == 'paused':
                self.EnemyDict['ai_behaviour'][key].resumeAi('all')
                enemy.stop()
                enemy.loop('Walk')
    def destroy(self, KeepAI=False):
        self.Run = False
        self.WaveCounttext.destroy()
        if KeepAI:
            for enemy in list(self.EnemyDict['model'].keys()):
                self.EnemyAIWorld.removeAiChar(enemy)
                self.EnemyDict['ai_behaviour'][enemy].removeAi(enemy)
        self.EnemyDict['model'] = {}
        self.EnemyDict['ai_dot'] = {}
        self.EnemyDict['collision'] = {}
        self.EnemyDict['ai_char'] = {}
        self.EnemyDict['ai_behaviour'] = {}
        self.EnemyDict['health'] = {}

class Game(ShowBase):
    vfs = VirtualFileSystem.getGlobalPtr()
    baseFolder = (f"{sys.argv[0]}").replace(r'\main.py', "")
    inaMenu = True
    mouse_sensitivity = 0.5
    PlayerHull = 100
    MaxHull = 100
    PowerCapacity = 100
    PowerValue = 100
    Speed = 10
    sunDirection = -.2
    cycleOscillation = {'dawnOrDusk' : 'down', 'notQiyamah': .45}
    keys = {'w':"forward",
            's':"backward",
            'a':"left",
            'd':"right",
#            'space':"up",
#            'e':"down"
            }
    def repower(self, task):
        if self.PowerValue < self.PowerCapacity:
            self.PowerValue += .1
            return task.cont
        else:
            return Task.done
    def enemies(self, fish, number, height, health):
        self.fishyController = EnemyController(Game=self)
        fishType = ({1:"small", 2:"big", 3:'biggest'}).get(fish)
        taskMgr.add(self.fishyController.setup(f"assets/models/{fishType}Fish.bam", {"hit":f"assets/models/{fishType}Fish-hit.bam"}, number, height, health, waves=10, changePerWave=2,))
    def printPos(self):
        print(self.camera.getPos())
    def textTypewriteAnimation(self, parent, textPos, text, scale = 0.07, interval=0.05):
        textSplit = list(text)
        textNode = OnscreenText(parent=parent, text='', pos=textPos, scale=scale, fg=(0,1,0,1), align=TextNode.ALeft, font=self.transmissionFont)
        def cleanup(task):
            textNode.destroy()
        async def typewrite():
            for char in textSplit:
                textNode.setText(textNode.getText() + char)
                await Task.pause(interval)
            await Task.pause(1)
            return Task.done
        taskMgr.add(typewrite(), 'typewriteTask', uponDeath=cleanup)
    def dayNightCycle(self):
        steps = {'sunSpeed': 0.0005, 'rotationSpeed': 0.000375}
        self.cycleOscillation['notQiyamah'] -= steps['rotationSpeed']
        if self.cycleOscillation['dawnOrDusk'] == 'down':
            self.sunDirection += steps['sunSpeed']
            if self.sunDirection >= .3:
                self.cycleOscillation['dawnOrDusk'] = 'up'
                self.cycleOscillation['notQiyamah'] = 0.45
                steps['rotationSpeed'] = 0.000375
        elif self.cycleOscillation['dawnOrDusk'] == 'up':
            self.sunDirection -= steps['sunSpeed']
            if self.sunDirection <= -.3:
                self.cycleOscillation['dawnOrDusk'] = 'down'
                steps['rotationSpeed'] = 0.00017
        for models in self.currentModels:
            models.setShaderInput('light0_direction', (self.cycleOscillation['notQiyamah'], self.sunDirection, 0))
    def PlayerHUD(self):
        delattr(self, 'stopHullBarUpdate') if hasattr(self, 'stopHullBarUpdate') else None
        delattr(self, 'stopPowerBarUpdate') if hasattr(self, 'stopPowerBarUpdate') else None
        delattr(self, 'stopRover2PersonUpdate') if hasattr(self, 'stopRover2PersonUpdate') else None
        delattr(self, 'transponderHidden') if hasattr(self, 'transponderHidden') else None
        self.HUDMainFrame = DirectFrame(frameColor=(0.6, 0.6, 0.6, 1),
                                        frameSize=(-1.25, 1.25, -0.15, 0.15),
                                        pos=(0, 0, -.75))
        self.rover2PersonFrame = DirectFrame(frameColor=(0.2, 0.2, 0.2, 1),
                                             frameSize=(-.125, .125, -0.125, 0.125),
                                             pos=(0, 0, -.75))
        
        self.crosshairDot = DirectFrame(frameColor=(1, 0, 0, 1), frameSize=(-0.0025, 0.0025, -0.0025, 0.0025), pos=(0, 0, 0))

        self.transponderFrame = DirectFrame(frameColor=(.2, .2, .2, 1),
                                        frameSize=(-1.5, 1.5, -.2, .2), 
                                        pos=(0, 0, .75), 
                                        scale=(1, 1, 1), 
                                        relief=DGG.RIDGE,
                                        borderWidth=(0.05, 0.05)
                                        )

        self.pauseText = OnscreenText("To Pause press P", pos=(-2.5, 0.95), scale=0.05, fg=(1, 1, 1, 1), align=TextNode.ACenter)
        self.accept('p', self.PauseMenu)
        
        self.HullBar = DirectWaitBar(text="Hull", value=self.PlayerHull, range=self.MaxHull, pos=(-.85, -15, -.7))
        self.HullBar['barColor'] = (0, 2, 0, 2)
        self.HullBar['text_scale'] = .05
        self.HullBar['frameSize'] = (-.35, .35, -.035, .02)
        self.HullBar['barRelief']= DGG.SUNKEN

        self.PowerBar = DirectWaitBar(text="Power", value=100, range=self.PowerCapacity, pos=(-.85, -1, -.8))
        self.PowerBar['barColor'] = (0, .5, 2, 2)
        self.PowerBar['text_scale'] = .05
        self.PowerBar['frameSize'] = (-.35, .35, -.035, .02)
        self.PowerBar['barRelief']= DGG.SUNKEN

        self.cm.setFrame(-.125, .125, -0.125, 0.125)
        self.thirdPersonCard = self.rover2PersonFrame.attachNewNode(self.cm.generate())
    def exportScene(self):
        file_name = input("Enter file name: ")
        ss = StringStream()
        self.render.ls(out=ss)
        with open(f"scene_graph-{file_name}.txt", "w", encoding="utf-8") as f:
            f.write(ss.get_data().decode("utf-8"))
    def Death(self):
        self.CameraOperator()
        def LoadMainMenu(self):
            # remove task, reset
            self.deathFrame.destroy()
            self.btnMainMenu.destroy()
            self.PlayerHull = 100  # Reset current hull
            self.MaxHull = 100     # Reset max hull to initial value
            self.clickSound.play()
            taskMgr.remove('Update')
            self.SaveProgress(reset=True)
            self.HealthBar.destroy()
            self.playButtonMethod = AsyncFuture()
            self.MainMenu()
            self.cam_controller = CameraControllerBehaviour(self.camera, velocity=3, mouse_sensitivity=self.mouse_sensitivity)
            self.cam_controller.setup(keys=self.keys)
            self.cam_controller.disable()
            self.currentwave = 0
            children_to_remove = [child for child in self.render.getChildren() if child != self.camera]
            for child in children_to_remove:
                if '__Actor_modelRoot' in child.getChildren():
                    child.cleanup()
                else:    
                    child.removeNode()
            taskMgr.add(self.loadScene())
        self.deathFrame = DirectFrame(frameColor=(0, 0, 0, 1), 
                                      frameSize=(-1.4, 1.4, -1, 1), 
                                      pos=(0, 0, 0), 
                                      scale=(1, 1, 1), 
                                      text="You died", 
                                      text_font=self.Font,
                                      text_scale=0.3, 
                                      text_pos=(0, .75), 
                                      text_fg=(1, 0, 0, 1), 
                                      text_align=TextNode.ACenter)
        self.btnMainMenu = DirectButton(
            parent=self.deathFrame,
            frameColor=(0.15, 0.15, 0.15, 1),
            frameSize=(-0.4, 0.4, -0.08, 0.16),
            pos=LPoint3f(0, 0, -0.15),
            hpr=LVecBase3f(0, 0, 0),
            relief=1,
            scale=LVecBase3f(1, 1, 1),
            text='Exit to Main Menu',
            text_align=TextNode.A_center,
            text_scale=(0.075, 0.075),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0.8, 0.8, 0.8, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            command=LoadMainMenu,
            extraArgs=[self],
        )
    def MouseIn(self):
        props = self.win.getProperties()
        # This is needed to for WebGL. If the window is not in focus, the mouse won't work, so we need to request focus
        if not self.inaMenu:
            if not props.getForeground() or not props.getCursorHidden() or props.getMouseMode() != WindowProperties.MRelative:
                self.win.requestProperties(WindowProperties(foreground=True, mouse_mode=WindowProperties.MRelative, cursor_hidden=True))
        
        # Create a CollisionRay for the mouse click
        ray_node = CollisionNode('click-ray')
        ray = CollisionRay()
        ray.setOrigin(0, 0, 0)  # Start at the camera
        ray.setDirection(0, 1, 0)  # Point forward
        ray_node.addSolid(ray)
        

        # Attach the CollisionRay to the camera and set it to the right bitmasks
        self.ray_path = self.camera.attachNewNode(ray_node)

        # Create a quene to store the collisions and add the CollisionRay to the CollisionTraverser
        self.collision_queue = CollisionHandlerQueue()
        self.cTrav.addCollider(self.ray_path, self.collision_queue)
        # Perform collision traversal
        self.cTrav.traverse(self.render)
        #print(self.ball.getPos())
        try:
            # Process collisions
            num_collisions = self.collision_queue.getNumEntries()
            if num_collisions > 1:
                self.collision_queue.sortEntries()
                entry = self.collision_queue.getEntry(1)  # Get the closest collision
                self.hit_name = (entry.getIntoNode()).getName()
                # Check if the hit node is the model that is supposed to be clicked using something like this:
                if hasattr(self, 'fishyController'):
                    for enemy in list(self.fishyController.EnemyDict['collision'].values()):
                        if self.hit_name == enemy.getName():
                            print(f"Hit enemy: {self.hit_name}")
                            self.fishyController.EnemyHit(enemy)
        except AssertionError as e:
            print("AssertionError occurred during collision processing.")
            print(e)
        except KeyError as e:
            print("KeyError occurred during collision processing.")
            pass
        if hasattr(self, 'ray_path'):
            self.cTrav.removeCollider(self.ray_path)  # Remove collider from traverser
            self.ray_path.removeNode()  # Safely remove the ray
            self.collision_queue.clearEntries()
        #self.ballDown = False
        #self.ballDown = True        
    def SaveProgress(self, reset=False):
        if reset:
            self.save_file = open("save.txt", "w")
            self.save_file.write('LPoint3f(0, 0, 114)\n')
            self.save_file.write(str(0))
            self.save_file.close()
        else:
            self.save_file = open("save.txt", "w")
            self.save_file.write(str(self.camera.getPos()) + '\n')
            self.save_file.close()
    def CameraOperator(self):
        # When this function is called, we check if we are in a menu, if we are then we watch our new keys
        # This is critical for one we don't setup the camera again, and two if the player decides to change controls
        # And then we switch our bool to false, as we are no longer in a menu, enabling clicking to focus the mouse
        if self.inaMenu:
            self.cam_controller.rewatch(self.keys, mouse_sensitivity=self.mouse_sensitivity)
            self.cam_controller._velocity = self.Speed
            self.inaMenu = False
        
        # If we are not in a menu, then we disable the camera controller
        # And set our bool to true, critical because our click function refocuses the window
        else:
            self.cam_controller.disable()  
            props = WindowProperties()
            props.setCursorHidden(False)
            self._showbase.win.requestProperties(props) 
            self.inaMenu = True
        # Using our boolean we pass an if statement to effectively switch when oue mouse focuses on clicks
    def TutorialMenu(self):
        self.clickSound.play()
        self.paused = True
        self.tutorialMainFrame = DirectFrame(frameColor=(0.6, 0.6, 0.6, 1),
                                        frameSize=(-1.25, 1.25, -0.9, 0.9),
                                        pos=(0, 0, 0)
        )
        self.tutorialLabel = DirectLabel(frameColor=(0.6, 0.6, 0.6, 1),
                                        frameSize=(-.3, .3, -0.1, 0.1),
                                        pos=(-.8, 0, .65),
                                        parent=self.tutorialMainFrame,
                                        relief=None,
                                        text="Tutorial",
                                        text_fg=(0, 0, 0, 1),
                                        text_pos=(0, 0),
                                        text_scale=0.2,
                                        text_font=self.Font,
                                        text_align=TextNode.ACenter
        )
        self.tutorialVideoControlFrame = DirectFrame(parent=self.tutorialMainFrame,
                                                    frameColor=(0.3, 0.3, 0.3, 1),
                                                    frameSize=(-1, 1, -0.1, 0.1),
                                                    pos=(0, 0, -.7)
        )
        self.tutorialVideo = self.loader.loadTexture(r"assets/audio/tutorial.mp4")
        self.cm = CardMaker("card")
        self.cm.setFrame(-.8, .8, -0.55, 0.55)
        self.cm.setUvRange(self.tutorialVideo)
        self.card = self.render2d.attachNewNode(self.cm.generate())
        self.card.setTexture(self.tutorialVideo)
        self.card.setPos(-0, 0, 0)
        self.card.reparentTo(self.tutorialMainFrame)
        self.tutorialVideo.set_muted(False)

        def PlayblackSliderMethod(self):
            self.tutorialVideo.stop()
            self.videoPauseButton['image'] = 'assets/images/pauseIcon.png'
            self.currentTime = self.videoPlaybackSlider['value']
            self.paused = True
        def PausePlayMethod(self):
            if self.paused == True:
                #When clicked from pause to play
                self.paused = False
                self.videoPauseButton['image'] = 'assets/images/playIcon.png'
            else:
                self.paused = True
                self.videoPauseButton['image'] = 'assets/images/pauseIcon.png'
            if self.tutorialVideo.is_playing:
                self.currentTime = self.tutorialVideo.get_time()
                self.tutorialVideo.stop()
            else:
                self.tutorialVideo.set_time(self.currentTime)
                self.tutorialVideo.play()
        
        self.videoPlaybackSlider = DirectSlider(range=(0, self.tutorialVideo.getVideoLength()),
                                  value=0, 
                                  command=PlayblackSliderMethod, 
                                  frameSize=(-.75, .75, -0.1, 0.1),
                                  frameColor=(0.8, 0.8, 0.8, 1),
                                  thumb_frameSize=(-.015, .015, -.015, .015),
                                  thumb_frameColor=(1, 0, 0, 1),
                                  pos=LPoint3f(0, 0, 0),
                                  orientation='horizontal', 
                                  parent=self.tutorialVideoControlFrame,
                                  thumb_relief=DGG.FLAT,
                                  extraArgs=[self]
                                  )
        self.videoPauseButton = DirectButton(parent=self.tutorialVideoControlFrame,
                                             frameColor=(0.8, 0.8, 0.8, 1),
                                             frameSize=(-.05, .05, -0.05, 0.05),
                                             pos=LPoint3f(-.9, 0, 0),
                                             relief=None,
                                             image = 'assets/images/pauseIcon.png',
                                             image_pos=(0, 0, 0),
                                             image_scale=(0.1, 0.1, 0.1),
                                             command=PausePlayMethod,
                                             extraArgs=[self]
                                             )
        self.videoPauseButton.setTransparency(TransparencyAttrib.MAlpha)
    def OptionMenu(self):
        self.clickSound.play()
        self.mouseSettingsOpen = False
        self.keyboardSettingsOpen = False
        self.audioSettingsOpen = False
        self.aboutSettingsOpen = False
        
        def clear_menu():
            if self.mouseSettingsOpen:
                self.sensitivityFrame.destroy()
                self.sensitivityLabel.destroy()
                self.sensitivitySlider.destroy()
                self.mouseSettingsOpen = False  
            if self.keyboardSettingsOpen:
                self.forwardFrame.destroy()
                self.backwardFrame.destroy()
                self.leftFrame.destroy()
                self.rightFrame.destroy()
                self.forwardLabel.destroy()
                self.backwardLabel.destroy()
                self.leftLabel.destroy()
                self.rightLabel.destroy()
                self.forwardEntry.destroy()
                self.backwardEntry.destroy()
                self.leftEntry.destroy()
                self.rightEntry.destroy()
                self.btnSave.destroy()
                self.disclamerLabel.destroy()
                self.keyboardSettingsOpen = False
            if self.audioSettingsOpen:
                self.audioMuteLabel.destroy()
                self.audioMuteButton.destroy()
                self.audioSettingsOpen = False
            if self.aboutSettingsOpen:
                self.aboutLabel.destroy()
                self.gameAboutLabel.destroy()
                self.aboutSettingsOpen = False
        self.optionMenuBg = OnscreenImage(image='assets/images/optionMenuBg.png', pos=(0, 0, 0), scale=(.75, .5, 1))
        self.optionMenuBg.setTransparency(TransparencyAttrib.MAlpha)

        self.scrolledFrame = DirectScrolledFrame(
            frameColor=(0.4, 0.4, 0.4, 1),
            frameSize=(-.2, .6, -.8, .7),
            pos=LPoint3f(-0.05, 0, 0),
            canvasSize=(-.4, .4, -1, 1),
            verticalScroll_relief=None,
            horizontalScroll_relief=None,
        )
        self.scrolledFrame.setManageScrollBars()
        self.scrolledFrame.verticalScroll['frameSize'] = (-.01, .01, -.01, .01)
        self.scrolledFrame.verticalScroll['frameColor'] = (0.4, 0.4, 0.4, 1)
        self.scrolledFrame.verticalScroll['thumb_relief'] = DGG.FLAT
        self.scrolledFrame.verticalScroll['decButton_relief'] = None
        self.scrolledFrame.verticalScroll['incButton_relief'] = None
        self.scrolledFrame.horizontalScroll['frameSize'] = None

        def MouseSettingMethod(self):
            self.sensitivityFrame = DirectFrame(frameColor=(0.6, 0.6, 0.6, 1),
                                                frameSize=(-.3, .3, -0.1, 0.1),
                                                pos=LPoint3f(-.05, 0, .85),
                                                parent=self.scrolledFrame.getCanvas(),
                                                relief=DGG.FLAT
                                                )
            self.sensitivityLabel = DirectLabel(frameColor=(0.6, 0.6, 0.6, 1),
                                                text="Mouse Sensitivity", 
                                                text_scale=0.05, 
                                                pos=LPoint3f(-.1, 0, .875), 
                                                parent=self.scrolledFrame.getCanvas(), 
                                                relief=DGG.FLAT
                                                )
            def changesensitivity():
                self.mouse_sensitivity = self.sensitivitySlider['value'] * .2   
            self.sensitivitySlider = DirectSlider(range=(0,2), 
                                  value=1, 
                                  command=changesensitivity, 
                                  frameSize=(-.25, .25, -0.05, 0.05),
                                  frameColor=(0.8, 0.8, 0.8, 1),
                                  thumb_frameSize=(-.01, .01, -.01, .01),
                                  thumb_frameColor=(0.4, 0.4, 0.4, 1),
                                  pos=LPoint3f(-.05, 0, .8),
                                  orientation='horizontal', 
                                  parent=self.scrolledFrame.getCanvas(),
                                  thumb_relief=DGG.FLAT
                                  )
            clear_menu()
            self.mouseSettingsOpen = True
        def KeyboardSettingMethod(self):
            def ForwardKeyMethod(key, self):
                self.forwardKey = key
            def BackwardKeyMethod(key, self):
                self.backwardKey = key
            def LeftKeyMethod(key, self):
                self.leftKey = key
            def RightKeyMethod(key, self):
                self.rightKey = key
            def SaveMethod(self):
                if not hasattr(self, 'forwardKey'):
                    self.forwardKey = 'w'
                if not hasattr(self, 'backwardKey'):
                    self.backwardKey = 's'
                if not hasattr(self, 'leftKey'):
                    self.leftKey = 'a'
                if not hasattr(self, 'rightKey'):
                    self.rightKey = 'd'
                self.keys = {
                    self.forwardKey: "forward",
                    self.backwardKey: "backward",
                    self.leftKey: "left",
                    self.rightKey: "right",
                    'space': "up",
                    'e': "down"
                }
            self.forwardLabel = DirectLabel(frameColor=(0.6, 0.6, 0.6, 1),
                                                text="Forward", 
                                                text_scale=0.05, 
                                                pos=LPoint3f(-.2, 0, .875), 
                                                parent=self.scrolledFrame.getCanvas(), 
                                                relief=DGG.FLAT,
                                                sortOrder=2
                                                )
            self.backwardLabel = DirectLabel(frameColor=(0.6, 0.6, 0.6, 1),
                                                text="Backward", 
                                                text_scale=0.05, 
                                                pos=LPoint3f(-.19, 0, .625), 
                                                parent=self.scrolledFrame.getCanvas(), 
                                                relief=DGG.FLAT,
                                                sortOrder=2
                                                )
            self.leftLabel = DirectLabel(frameColor=(0.6, 0.6, 0.6, 1),
                                                text="Left", 
                                                text_scale=0.05, 
                                                pos=LPoint3f(-.25, 0, .375), 
                                                parent=self.scrolledFrame.getCanvas(), 
                                                relief=DGG.FLAT,
                                                sortOrder=2
                                                )
            self.rightLabel = DirectLabel(frameColor=(0.6, 0.6, 0.6, 1),
                                                text="Right", 
                                                text_scale=0.05, 
                                                pos=LPoint3f(-.24, 0, .125), 
                                                parent=self.scrolledFrame.getCanvas(), 
                                                relief=DGG.FLAT,
                                                sortOrder=2
                                                )
            self.forwardEntry = DirectEntry(frameColor=(1, 1, 1, 1),
                                                frameSize=(-.15, 0, -0.03, 0.03),
                                                pos=LPoint3f(-.15, 0, .825),
                                                text_pos= (-0.1, -.015),
                                                parent=self.scrolledFrame.getCanvas(),
                                                relief=DGG.FLAT,
                                                text_scale=0.05,
                                                sortOrder=2,
                                                command=ForwardKeyMethod,
                                                extraArgs=[self],
                                                initialText='W'
                                                )
            self.backwardEntry = DirectEntry(frameColor=(1, 1, 1, 1),
                                                frameSize=(-.15, 0, -0.03, 0.03),
                                                pos=LPoint3f(-.15, 0, .575),
                                                text_pos= (-0.1, -.015),
                                                parent=self.scrolledFrame.getCanvas(),
                                                relief=DGG.FLAT,
                                                text_scale=0.05,
                                                sortOrder=2,
                                                command=BackwardKeyMethod,
                                                extraArgs=[self],
                                                initialText='S'
                                                )
            self.leftEntry = DirectEntry(frameColor=(1, 1, 1, 1),
                                                frameSize=(-.15, 0, -0.03, 0.03),
                                                pos=LPoint3f(-.15, 0, .325),
                                                text_pos= (-0.1, -.015),
                                                parent=self.scrolledFrame.getCanvas(),
                                                relief=DGG.FLAT,
                                                text_scale=0.05,
                                                sortOrder=2,
                                                command=LeftKeyMethod,
                                                extraArgs=[self],
                                                initialText='A'
                                                )
            self.rightEntry = DirectEntry(frameColor=(1, 1, 1, 1),
                                                frameSize=(-.15, 0, -0.03, 0.03),
                                                pos=LPoint3f(-.15, 0, .075),
                                                text_pos= (-0.1, -.015),    
                                                parent=self.scrolledFrame.getCanvas(),
                                                relief=DGG.FLAT,
                                                text_scale=0.05,
                                                sortOrder=2,
                                                command=RightKeyMethod,
                                                extraArgs=[self],
                                                initialText='D'
                                                )
            self.forwardFrame = DirectFrame(frameColor=(0.6, 0.6, 0.6, 1),
                                                frameSize=(-.3, .3, -0.1, 0.1),
                                                pos=LPoint3f(-.05, 0, .85),
                                                parent=self.scrolledFrame.getCanvas(),
                                                relief=DGG.FLAT
                                                )
            self.backwardFrame = DirectFrame(frameColor=(0.6, 0.6, 0.6, 1),
                                                frameSize=(-.3, .3, -0.1, 0.1),
                                                pos=LPoint3f(-.05, 0, .6),
                                                parent=self.scrolledFrame.getCanvas(),
                                                relief=DGG.FLAT
                                                )
            self.leftFrame = DirectFrame(frameColor=(0.6, 0.6, 0.6, 1),
                                                frameSize=(-.3, .3, -0.1, 0.1),
                                                pos=LPoint3f(-.05, 0, .35),
                                                parent=self.scrolledFrame.getCanvas(),
                                                relief=DGG.FLAT
                                                )
            self.rightFrame = DirectFrame(frameColor=(0.6, 0.6, 0.6, 1),
                                                frameSize=(-.3, .3, -0.1, 0.1),
                                                pos=LPoint3f(-.05, 0, .1),
                                                parent=self.scrolledFrame.getCanvas(),
                                                relief=DGG.FLAT
                                                )
            self.btnSave = DirectButton(
                frameColor=(0.2, 0.2, 0.2, 1),
                frameSize=(-0.09, 0.09, -0.025, 0.05),
                text='Save',
                text_scale=0.05,
                text_fg=(0.5, 0.5, 0.5, 1),
                pos=LPoint3f(-0.25, 0, -0.075),
                relief=1,
                parent=self.scrolledFrame.getCanvas(),
                command=SaveMethod,
                extraArgs=[self],
                sortOrder=2
            )
            self.disclamerLabel = DirectLabel(
                frameColor=(0.6, 0.6, 0.6, 1),
                text="*Press enter each key*",
                text_scale=0.05,
                pos=LPoint3f(0, 0, -0.2),
                parent=self.scrolledFrame.getCanvas(),
                relief=None
            )
            clear_menu()
            self.keyboardSettingsOpen = True
        
        def AudioSettingMethod(self):
            def muteClick(self):
                self.clickSound = self.loader.loadSfx('assets/audio/mute.ogg')
            self.audioMuteLabel = DirectLabel(frameColor=(0.6, 0.6, 0.6, 1),
                                        text="About",
                                        text_scale=0.1,
                                        pos=LPoint3f(-0.025, 0, 0.85),
                                        parent=self.scrolledFrame.getCanvas(),
                                        relief=None
                                        )
            
            self.audioMuteButton = DirectButton(
                frameColor=(0.4, 0.4, 0.4, 1),
                frameSize=(-0.09, 0.09, -0.07, 0.13),
                pos=LPoint3f(-0.37666, 0, 0.57666),
                hpr=LVecBase3f(0, 0, 0),
                relief=1,
                scale=LVecBase3f(1, 1, 1),
                image= 'assets/images/mouseIcon.png',
                image_scale = (.09, .09, .09),
                image_pos = (0, 0, 0.03),
                image_hpr = (0, 0, 0),
                command=muteClick,
                extraArgs=[self],
            )
            clear_menu()
            self.audioSettingsOpen = True
        def AboutSettingMethod(self):
            self.aboutLabel = DirectLabel(frameColor=(0.6, 0.6, 0.6, 1),
                                        text="About",
                                        text_scale=0.1,
                                        pos=LPoint3f(-0.025, 0, 0.85),
                                        parent=self.scrolledFrame.getCanvas(),
                                        relief=None
                                        )
            self.gameAboutLabel = DirectLabel(frameColor=(0.6, 0.6, 0.6, 1),
                                            text= "TSA Videogame Design 2025-2026 \n 'Doomed to Europa' is a game developed by \n  the team 1679-3 for the 2025-2026 \n  \
                                            Technology Student Association Competition for Video Game Design. \n this is a based on the theme of \n\
                                            We developed this game using \n the Panda3D game engine \n differing from Unity and Unreal as \n it is a purely text edited engine",
                                            text_scale=0.04,
                                            pos=LPoint3f(-0.04, 0, 0.3),
                                            parent=self.scrolledFrame.getCanvas(),
                                            relief=None
                                            )
            clear_menu()
            self.aboutSettingsOpen = True
        self.btnMouse = DirectButton(
            frameColor=(0.4, 0.4, 0.4, 1),
            frameSize=(-0.09, 0.09, -0.07, 0.13),
            pos=LPoint3f(-0.37666, 0, 0.57666),
            hpr=LVecBase3f(0, 0, 0),
            relief=1,
            scale=LVecBase3f(1, 1, 1),
            image= 'assets/images/mouseIcon.png',
            image_scale = (.09, .09, .09),
            image_pos = (0, 0, 0.03),
            image_hpr = (0, 0, 0),
            command=MouseSettingMethod,
            extraArgs=[self],
        )
        self.btnMouse.setTransparency(TransparencyAttrib.MAlpha)

        self.btnKeyboard = DirectButton(
            frameColor=(0.4, 0.4, 0.4, 1),
            frameSize=(-0.09, 0.09, -0.07, 0.14),
            pos=LPoint3f(-0.376666, 0, 0.33666),
            hpr=LVecBase3f(0, 0, 0),
            relief=1,
            scale=LVecBase3f(1, 1, 1),
            image= 'assets/images/keyboardIcon.png',
            image_scale = (.09, .09, .09),
            image_pos = (0, 0, .03),
            image_hpr = (0, 0, 0),
            command=KeyboardSettingMethod,
            extraArgs=[self],
        )
        self.btnKeyboard.setTransparency(TransparencyAttrib.MAlpha)

        self.btnAudioSet = DirectButton(
            frameColor=(0.4, 0.4, 0.4, 1),
            frameSize=(-0.09, 0.09, -0.07, 0.14),
            pos=LPoint3f(-0.37666, 0, 0.09666),
            hpr=LVecBase3f(0, 0, 0),
            relief=1,
            scale=LVecBase3f(1, 1, 1),
            image= 'assets/images/audioIcon.png',
            image_scale = (.07, .07, .07),
            image_pos = (0, 0, .03),
            image_hpr = (0, 0, 0),
            command=AudioSettingMethod,
            extraArgs=[self],
        )
        self.btnAudioSet.setTransparency(TransparencyAttrib.MAlpha)
        
        self.btnAbout = DirectButton(
            frameColor=(0.4, 0.4, 0.4, 1),
            frameSize=(-0.09, 0.09, -0.07, 0.14),
            pos=LPoint3f(-0.37666, 0, -0.13666),
            hpr=LVecBase3f(0, 0, 0),
            relief=1,
            scale=LVecBase3f(1, 1, 1),
            image= 'assets/images/aboutIcon.png',
            image_scale = (.07, .07, .07),
            image_pos = (0, 0, .03),
            image_hpr = (0, 0, 0),
            command=AboutSettingMethod,
            extraArgs=[self],
        )
        self.btnAbout.setTransparency(TransparencyAttrib.MAlpha)

        def close_menu():
            self.scrolledFrame.destroy()
            self.optionMenuBg.destroy()
            self.btnAbout.destroy()
            self.btnAudioSet.destroy()
            self.btnKeyboard.destroy()
            self.btnMouse.destroy()
            self.btnExit.destroy()
            clear_menu()

        self.btnExit = DirectButton(
            frameColor=(0.4, 0.4, 0.4, 1),
            frameSize=(-0.09, 0.09, -0.07, 0.14),
            pos=LPoint3f(-0.5, 0, 0.75),
            hpr=LVecBase3f(0, 0, 0),
            relief=None,
            scale=LVecBase3f(1, 1, 1),
            image= 'assets/images/exitIcon.png',
            image_scale = (.07, .07, .07),
            image_pos = (0, 0, .03),
            image_hpr = (0, 0, 0),
            command=close_menu,
        )
        self.btnExit.setTransparency(TransparencyAttrib.MAlpha)
    def clearHUD(self):
        if hasattr(self, 'HullBar'):
            self.HullBar.hide()
            setattr(self, 'stopHullBarUpdate', True)
        if hasattr(self, 'PowerBar'):
            self.PowerBar.hide()
            setattr(self, 'stopPowerBarUpdate', True)
        if hasattr(self, 'HUDMainFrame'):
            self.HUDMainFrame.hide()
            delattr(self, 'HUDMainFrame')
        if hasattr(self, 'rover2PersonFrame'):
            self.rover2PersonFrame.hide()
            setattr(self, 'stopRover2PersonUpdate', True)
        if hasattr(self, 'pauseText'):
            self.pauseText.hide()
            delattr(self, 'pauseText')
        if hasattr(self.Plot, 'transponderFrame'):
            self.transponderFrame.hide()
            setattr(self, 'transponderHidden', True)
        if hasattr(self.Plot, 'FundsBar'):
            self.Plot.FundsBar.destroy()
    def MainMenu(self):
        self.inaMenu = True
        self.mainMenuBackground = OnscreenImage(image='assets/images/mainMenuBackground.png', pos=(0, 0, 0), scale=(2.75,1,1))
        self.titleText = OnscreenText(text="Doomed to Europa", pos=(0, .4), scale=0.25, fg=(1, 1, 1, 1), align=TextNode.ACenter)
        self.titleText.setFont(self.Font)
        self.btnPlay = DirectButton(
            frameColor=(0.15, 0.15, 0.15, 1),
            frameSize=(-0.2, 0.2, -0.03, 0.06),
            pos=LPoint3f(0, 0, -0.1),
            hpr=LVecBase3f(0, 0, 0),
            relief=1,
            scale=LVecBase3f(1, 1, 1),
            text='Play',
            text_align=TextNode.A_center,
            text_scale=(0.05, 0.05),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0.8, 0.8, 0.8, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            command=self.playButtonMethod.set_result,
            extraArgs=[None],
        )

        self.btnOption= DirectButton(
            frameColor=(0.15, 0.15, 0.15, 1),
            frameSize=(-0.3, 0.3, -0.03, 0.06),
            pos=LPoint3f(-1.2, 0, -0.87),
            hpr=LVecBase3f(0, 0, 0),
            relief=None,
            scale=LVecBase3f(1, 1, 1),
            image= 'assets/images/optionIcon.png',
            image_scale = (.1, .1, .1),
            command=self.OptionMenu,
            extraArgs=[],
        )
        self.btnOption.setTransparency(TransparencyAttrib.MAlpha)

        self.btnTutorial= DirectButton(
            frameColor=(0.15, 0.15, 0.15, 1),
            frameSize=(-0.3, 0.3, -0.03, 0.06),
            pos=LPoint3f(1.2, 0, -0.87),
            hpr=LVecBase3f(0, 0, 0),
            relief=None,
            scale=LVecBase3f(1, 1, 1),
            image= 'assets/images/tutorialIcon.png',
            image_scale = (.1, .1, .1),
            command=self.TutorialMenu,
            extraArgs=[],
        )
        self.btnTutorial.setTransparency(TransparencyAttrib.MAlpha)
    def PauseMenu(self):
        self.clickSound.play()
        self.CameraOperator()
        def LoadMainMenu(self):
            #Keep AI here, dont remove .setup and reenter waves
            self.clickSound.play()
            taskMgr.remove('Update')
            self.SaveProgress()
            self.cam_controller = CameraControllerBehaviour(self.camera, velocity=3, mouse_sensitivity=self.mouse_sensitivity)
            self.cam_controller.setup(keys=self.keys)
            self.cam_controller.disable()
            self.HealthBar.destroy()
            self.playButtonMethod = AsyncFuture()
            self.MainMenu()
            children_to_remove = [child for child in self.render.getChildren() if child != self.camera]
            for child in children_to_remove:
                if '__Actor_modelRoot' in child.getName():
                    child.cleanup()
                else:    
                    child.removeNode()
            self.pauseFrame.destroy()
            self.btnMainMenu.destroy()
            self.btnResume.destroy()
            taskMgr.add(self.loadScene())
        def Resume(self):
            self.clickSound.play()
            self.pauseFrame.destroy()
            self.btnMainMenu.destroy()
            self.btnResume.destroy()
            self.CameraOperator()
        self.pauseFrame = DirectFrame(frameColor=(0.6, 0.6, 0.6, 1),
                                    frameSize=(-.5, .5, -0.3, 0.35),
                                    pos=LPoint3f(0, 0, 0),
                                    hpr=LVecBase3f(0, 0, 0),
                                    relief=DGG.FLAT,
                                    scale=LVecBase3f(1, 1, 1))
        self.btnMainMenu = DirectButton(
            parent=self.pauseFrame,
            frameColor=(0.15, 0.15, 0.15, 1),
            frameSize=(-0.4, 0.4, -0.08, 0.16),
            pos=LPoint3f(0, 0, -0.15),
            hpr=LVecBase3f(0, 0, 0),
            relief=1,
            scale=LVecBase3f(1, 1, 1),
            text='Save & Exit',
            text_align=TextNode.A_center,
            text_scale=(0.1, 0.1),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0.8, 0.8, 0.8, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            command=LoadMainMenu,
            extraArgs=[self],
        )
        self.btnResume = DirectButton(
            parent=self.pauseFrame,
            frameColor=(0.15, 0.15, 0.15, 1),
            frameSize=(-0.4, 0.4, -0.08, 0.16),
            pos=LPoint3f(0, 0, 0.15),
            hpr=LVecBase3f(0, 0, 0),
            relief=1,
            scale=LVecBase3f(1, 1, 1),
            text='Resume',
            text_align=TextNode.A_center,
            text_scale=(0.1, 0.1),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0.8, 0.8, 0.8, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            command=Resume,
            extraArgs=[self],
        )
#This function is called when the mouse is clicked, calling a function based on what is clicked in game    
    def shader(self, nodes = None, EnterNode = None):
        self.currentModels = []
        if not hasattr(self, 'Shader_setup'):
            self.Shader_setup = None
            if PandaSystem.getPlatform() == 'win_amd64' or PandaSystem.getPlatform() == 'osx_aarch64':
                shaders = [self.baseFolder + r"\assets\shaders\Shader.vert", self.baseFolder + r"\assets\shaders\Shader.frag"]
                patchedShaders = []
                for file in shaders:    
                    with open(file, 'r') as file:
                        code = file.read()
                        code = code.replace("#version 300 es", "#version 330")
                        code = "\n".join(
                            line for line in code.splitlines()
                            if not line.strip().startswith("precision")
                        )
                        patchedShaders.append(code)
                self.Shader = Shader.make(Shader.SL_GLSL, patchedShaders[0], patchedShaders[1])
            else:
                print("Using original shaders")
                self.Shader = Shader.load(Shader.SL_GLSL, "assets/shaders/Shader.vert", "assets/shaders/Shader.frag")
            shadow_buffer = self.win.make_texture_buffer("ShadowBuffer", 1024, 1024)
            shadow_buffer.set_sort(-100)
            shadow_buffer.set_clear_color((1, 1, 1, 1))
            self.shadow_map = shadow_buffer.get_texture()
            self.shadow_map.set_minfilter(SamplerState.FT_shadow)
            self.shadow_map.set_magfilter(SamplerState.FT_shadow)

            self.shadow_cam = self.make_camera(shadow_buffer, lens=OrthographicLens())
            self.shadow_cam.reparent_to(self.sunLightNP)

            shadow_scene = self.render.copy_to(NodePath("shadow_scene"))
            shadow_scene.set_shader(Shader.load(Shader.SL_GLSL, "assets/shaders/shadow_depth.vert", "assets/shaders/shadow_depth.frag"))
            self.shadow_cam.node().set_scene(shadow_scene)
        if EnterNode == None:
            for node in nodes:
                self.currentModels.append(node)
                node.setShader(self.Shader)
                node.setShaderInput("shadowMap", self.shadow_map)
                node.setShaderInput("shadowViewMatrix", self.shadow_cam.get_mat(self.render))
                node.setShaderInput("diffuseTex", node.find_texture("*"))
                node.setShaderInput("light0_direction", Vec3(.45, 1, 0))
                node.setShaderInput("light0_color", Vec3(.5, .75, 0.85))
                node.setShaderInput("material_diffuse", Vec4(0.2, 0.2, 0.2, 1.0))
                node.setShaderInput("material_specular", Vec4(0.2, 0.2, 0.2, 1))
                node.setShaderInput("material_shininess", 10.0)
                node.setShaderInput("ambient_color", Vec3(0.5, 0.5, 0.5))
                node.setShaderInput("cameraPos", self.camera.getPos(self.render))

        else:
            self.currentModels.append(EnterNode)
            EnterNode.setShader(self.Shader)
            EnterNode.setShaderInput("shadowMap", self.shadow_map)
            EnterNode.setShaderInput("shadowViewMatrix", self.shadow_cam.get_mat(self.render))
            EnterNode.setShaderInput("diffuseTex", EnterNode.find_texture("*"))
            EnterNode.setShaderInput("light0_direction", Vec3(.45, 1, 0))
            EnterNode.setShaderInput("light0_color", Vec3(.75, .75, 0.5))
            EnterNode.setShaderInput("material_diffuse", Vec4(0.2, 0.2, 0.2, 1.0))
            EnterNode.setShaderInput("material_specular", Vec4(0.2, 0.2, 0.2, 1))
            EnterNode.setShaderInput("material_shininess", 15.0)
            EnterNode.setShaderInput("ambient_color", Vec3(0.5, 0.5, 0.5))
            EnterNode.setShaderInput("cameraPos", self.camera.getPos(self.render))
    # This function loads the models in the background, reducing lag and improving performance
    async def readyScene(self):

        # in case of death, we need to reload the bool
        if hasattr(self, '_player_died'):
            delattr(self, '_player_died')  # Remove self._player_died
        
        if hasattr(self, '_player_won'):
            delattr(self, '_player_won')  # Remove self._player_won

        # Load the models in the background, each time suspending this
        # method until they are done
        self.worldCollisionModel = await self.loader.loadModel("assets/models/worldTriangles.bam", blocking=False)
        self.worldVisibleModel = await self.loader.loadModel("assets/models/worldVisible.bam", blocking=False)

        # Create a background for the world
        
        self.world_bg = await self.loader.loadModel("assets/models/skybox.bam",blocking=False)
        self.world_bg.set_scale(2500)

        world_bg_texture = self.loader.loadTexture("assets/images/world_bg.png")
        world_bg_texture.set_minfilter(SamplerState.FT_linear)
        world_bg_texture.set_magfilter(SamplerState.FT_linear)
        world_bg_texture.set_wrap_u(SamplerState.WM_repeat)
        world_bg_texture.set_wrap_v(SamplerState.WM_mirror)
        world_bg_texture.set_anisotropic_degree(400)
        self.world_bg.set_texture(world_bg_texture)
        if PandaSystem.getPlatform() == 'win_amd64' or PandaSystem.getPlatform() == 'osx_aarch64':
                shaders = [self.baseFolder + r"\assets\shaders\world_bg.vert.glsl", self.baseFolder + r"\assets\shaders\world_bg.frag.glsl"]
                patchedShaders = []
                for file in shaders:    
                    with open(file, 'r') as file:
                        code = file.read()
                        code = code.replace("#version 300 es", "#version 330")
                        code = "\n".join(
                            line for line in code.splitlines()
                            if not line.strip().startswith("precision")
                        )
                        patchedShaders.append(code)
                self.bgShader = Shader.make(Shader.SL_GLSL, patchedShaders[0], patchedShaders[1])
        else:
                print("Using original shaders")
                self.bgShader = Shader.load(Shader.SL_GLSL, "assets/shaders/world_bg.vert.glsl", "assets/shaders/world_bg.frag.glsl")
        self.world_bg.set_shader(self.bgShader) 
        
        # Create a collision node for the world
        self.world_collision_node = self.worldCollisionModel.find("**/+CollisionNode")
        self.worldCollisionModel.hide()
        self.cTrav.addCollider(self.world_collision_node, self.pusher)
        self.pusher.addCollider(self.world_collision_node, self.worldCollisionModel)

        # Set up Lighting SystemF
        self.sunLight = DirectionalLight('directionalLight')
        self.sunLight.setShadowCaster(True, 16384, 16384)
        self.sunLightNP = self.render.attachNewNode(self.sunLight)
        self.sunLightNP.setHpr(45, 45, 0)
        self.sunLight.setColor((1.5, 1.5, 1.5, 1))

        ambientLight = AmbientLight('ambientLight')
        ambientLight.setColor((0.1, 0.1, 0.1, 1))
        self.ambientLightNP = self.render.attachNewNode(ambientLight)
        
        # Set the shaders
        ''' Most of the time this is very custom. Though there is a pipeline that can be used
            Most of this stuff can be recycled
        '''
        self.shader(EnterNode=self.worldVisibleModel)

#        self.researchLocationEffect.start(parent=self.render, renderParent=self.render)
#        self.researchLocationEffect.setPos(0, 0, 250)

        #self.ball = self.loader.loadModel("assets/models/sun.bam")
        #self.ball.reparentTo(self.render)
        #self.ballDown = False

#        Loading_text.destroy() 

        # Request 8 RGB bits, no alpha bits, and a depth buffer.
        fb_prop = FrameBufferProperties()
        fb_prop.setRgbColor(True)
        fb_prop.setRgbaBits(8, 8, 8, 0)
        fb_prop.setDepthBits(16)

        # Create a WindowProperties object set to 512x512 size.
        win_prop = WindowProperties(size=(512, 512))

        # Don't open a window - force it to be an offscreen buffer.
        flags = GraphicsPipe.BF_refuse_window

        self.thirdPersonBuffer = self.graphicsEngine.make_output(self.pipe, "third person", -100, fb_prop, win_prop, flags, self.win.getGsg(), self.win)
        self.thirdPersonBuffer.setSort(-100)
        self.thirdPersonCam = self.makeCamera(self.thirdPersonBuffer)
        self.thirdPersonCam.reparentTo(self.render)
        self.thirdPersonTexture = Texture()
        self.thirdPersonBuffer.addRenderTexture(
            self.thirdPersonTexture,
            GraphicsOutput.RTMCopyRam,   # or RTMBindOrCopy
            GraphicsOutput.RTPColor
        )
        # Start the update cycle
        taskMgr.add(self.Update, "Update")        

    # The Update cycle, this function should be used to update positions and anything that needs to be updated
    def Update(self, task):
        if hasattr(self, 'thirdPersonCard') and hasattr(self, 'playerModel') and not hasattr(self, 'stopRover2PersonUpdate'):
            self.cm.setUvRange(self.thirdPersonTexture)
            self.thirdPersonCard.setTexture(self.thirdPersonTexture)
            self.thirdPersonCam.lookAt(self.playerModel)

        camera_forward = self.camera.getQuat(self.render).getForward()
        camera_up = self.camera.getQuat(self.render).getUp()
        camera_right = self.camera.getQuat(self.render).getRight()
        camera_position = self.camera.getPos(self.render)

        self.dayNightCycle()
        
        Player_Position = (
            camera_position+
            camera_forward * 0 -  # Forward by 1.0 units
            camera_up * 2.5 +       # Downward by 0.5 units
            camera_right * 0      # Rightward by 0.3 units
        )

        ThirdPersonCam_Position = (
            camera_position+
            camera_forward * 10 +  # Backward by 10.0 units
            camera_up * 5 +       # Upward by 5.0 units
            camera_right * 0      # Rightward by 0.0 units
        )
        
        Arrow_Position = (
            camera_position+
            camera_forward * 5 +  # Forward by 5.0 units
            camera_up * 0 +       # Upward by 0.0 units
            camera_right * -2      # Rightward by 0.0 units
        )

        if hasattr(self, 'playerModel'):
            self.playerModel.setPos(Player_Position)
            self.playerModel.setHpr(self.camera.getH()+90, 0, 0)
        
        self.thirdPersonCam.setPos(ThirdPersonCam_Position)

        if hasattr(self, "Plot") and hasattr(self.Plot, 'pointingArrow') and hasattr(self.Plot, 'mountainPeakPosition'):
            self.Plot.pointingArrow.setPos(Arrow_Position)
            self.Plot.pointingArrow.lookAt(self.render, self.Plot.mountainPeakPosition)
            direction = self.Plot.mountainPeakPosition - Arrow_Position
            direction.normalize()
            # Compute pitch only (vertical angle)
            pitch = -math.degrees(math.asin(direction.z))

            # Preserve existing H and R
            self.Plot.pointingArrow.setP(pitch-90)
            self.Plot.pointingArrow.setR(self.Plot.pointingArrow.getR() + 90)
            self.Plot.pointingArrow.setH(self.Plot.pointingArrow.getH() + 180)
        if self.worldCollisionModel.getParent() == self.render:
            self.worldCollisionModel.setPos(0, 0, 0)
        
        if not hasattr(self, 'stopHullBarUpdate') and hasattr(self, 'HullBar'):
            self.PlayerHull = min(self.PlayerHull, self.MaxHull)
            self.HullBar['value'] = self.PlayerHull

        if self.PlayerHull < 0 and not hasattr(self, '_player_died'):
            self._player_died = None
            self.Death()
        
        if hasattr(self, 'fishyController'):
            self.fishyController.MainUpdate()

        if not hasattr(self, "stopPowerBarUpdate") and hasattr(self, 'PowerBar'):
            self.PowerValue = min(self.PowerValue, self.PowerCapacity)
            self.PowerValue -= globalClock.getDt() * .75            
            self.PowerBar['value'] = self.PowerValue

        if not True:
            self._player_won = None
            self.CameraOperator()
            def LoadMainMenu(self):
                self.clickSound.play()
                taskMgr.remove('Update')
                self.SaveProgress(reset=True)
                self.HealthBar.destroy()
                self.playButtonMethod = AsyncFuture()
                self.MainMenu()
                self.cam_controller = CameraControllerBehaviour(self.camera, velocity=3, mouse_sensitivity=self.mouse_sensitivity)
                self.cam_controller.setup(keys=self.keys)
                self.cam_controller.disable()
                self.currentwave = 0
                children_to_remove = [child for child in self.render.getChildren() if child not in self.camera]
                for child in children_to_remove:
                    if '__Actor_modelRoot' in child.getChildren():
                        child.cleanup()
                    else:    
                        child.removeNode()
                self.winFrame.destroy()
                self.btnMainMenu.destroy()
                taskMgr.add(self.loadScene())
            self.winFrame = DirectFrame(frameColor=(0, 0, 0, 1), 
                                        frameSize=(-1.4, 1.4, -1., 1), 
                                        pos=(0, 0, 0), 
                                        scale=(1, 1, 1), 
                                        text="You Won!", 
                                        text_font=self.Font,
                                        text_scale=0.5, 
                                        text_pos=(0, .25), 
                                        text_fg=(0, 0, 1, 1), 
                                        text_align=TextNode.ACenter)
            self.btnMainMenu = DirectButton(
                parent=self.winFrame,
                frameColor=(0.15, 0.15, 0.15, 1),
                frameSize=(-0.4, 0.4, -0.08, 0.16),
                pos=LPoint3f(0, 0, -0.15),
                hpr=LVecBase3f(0, 0, 0),
                relief=1,
                scale=LVecBase3f(1, 1, 1),
                text='Exit to Main Menu',
                text_align=TextNode.A_center,
                text_scale=(0.075, 0.075),
                text_pos=(0, 0),
                text_fg=LVecBase4f(0.8, 0.8, 0.8, 1),
                text_bg=LVecBase4f(0, 0, 0, 0),
                command=LoadMainMenu,
                extraArgs=[self],
            )
        #if not self.ballDown:
        #    pos = self.camera.getPos(self.render)
        #    forward = self.camera.getQuat(self.render).getForward()
        #    self.ball.setPos(pos + forward * 50)

        return Task.cont
    def __init__(self, Plot: 'Plot'):
        super().__init__()
        
        lens = self.cam.node().getLens()
        lens.setFocalLength(0.25)

        self.currentwave = 0

        # Defining the Traverser, the task that checks for collisions, and the pusher, the task that pushes objects when it collides
        # The Traverser reports to the pusher, we also need to tell Panda3d which objects respond to collisions
        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()

        # Camera setup
        self.transitions = Transitions(self.loader)
        self.cam_controller = CameraControllerBehaviour(self.camera, velocity=self.Speed, gravity=-5
                                                        ,mouse_sensitivity=self.mouse_sensitivity
                                                        ,lockPitch=False)
        self.cam_controller.setup(keys=self.keys)
        self.cam_controller.disable()
        camera_collision_node = CollisionNode('camera')
        camera_collision_node.addSolid(CollisionBox(LPoint3f(0, 0, 0), 1, 1, 20))
        camera_collision_node_path = self.camera.attachNewNode(camera_collision_node)
        camera_collision_node_path.setCollideMask(BitMask32.bit(2))
  
        # Add the collision nodes to the traverser. This is how we tell Panda3d which objects respond to collisions  
        self.cTrav.addCollider(camera_collision_node_path, self.pusher) 
        self.pusher.addCollider(camera_collision_node_path, self.camera)

        #   We load the tasks in the background to reduce lag
        self.playButtonMethod = AsyncFuture()

        self.cm = CardMaker("card")

        taskMgr.add(self.readyScene())
        
        #  Tell Panda3d to listen for mouse clicks
        self.accept('mouse1', self.MouseIn)
        self.Font = self.loader.loadFont('assets/fonts/Metal-Lord.ttf')
        self.Font.setPixelsPerUnit(120)
        self.transmissionFont = self.loader.loadFont('assets/fonts/Hacked_CRT.ttf')

        self.clickSound = self.loader.loadSfx('assets/audio/click.ogg')

        self.enableParticles()

#        self.messenger.toggleVerbose()
        self.accept('x', self.exportScene)
        self.accept('k', self.printPos)
        self.accept('r', taskMgr.add('Repower', self.repower))

        self.Plot = Plot(self)

        # Open the main menu
        self.MainMenu()

class Plot():
    def manualPlotAdvance(self):
        self.eventAdvanceFunc['finish']()
        self.eventAdvanceFunc['reset']()
        self.eventDoneFunc['finish']()
        self.eventDoneFunc['reset']()
    def testingActivate(self):
        self.testing = True
        pass
    async def plotLine(self, task):
        if not self.testing:
            self.EuropaModel = await self.gameInstance.loader.loadModel("assets/models/europa.bam", blocking=False)
            self.EuropaModel.setScale(100)
            self.gameInstance.setBackgroundColor(0, 0, 0, 0)
        self.roverModel = self.gameInstance.loader.loadModel("assets/models/Rover.bam")
        self.roverModel.setScale(2)
        self.roverModel.setPos(850, 1950, 470)

        await self.gameInstance.playButtonMethod
        self.gameInstance.clickSound.play()

        # Remove the main menu
        self.gameInstance.titleText.destroy()
        self.gameInstance.btnPlay.destroy()
        self.gameInstance.mainMenuBackground.destroy()
        self.gameInstance.btnOption.destroy()
        self.gameInstance.btnTutorial.destroy()

        # Create a loading screen
        print("Loading Screen")
#        Loading_text = OnscreenText("Loading…", scale=2, parent=self.gameInstance.a2dTopCenter, pos=(0, 0), fg=(1, 1, 1, 1), align=TextNode.ACenter)
        
        self.zoomIn = True
        # Rover in space animation, flying towards Europa
        if not self.testing:
            def LookatRover(task):
                self.gameInstance.camera.lookAt(self.roverModel)
                if self.zoomIn:
                    self.gameInstance.cam.node().getLens().setFocalLength(self.gameInstance.cam.node().getLens().getFocalLength() + 0.01)
                return Task.cont
            self.gameInstance.transitions.fadeIn(3)
            self.EuropaModel.reparentTo(self.gameInstance.render)
            self.gameInstance.camera.setPos(760, 1860, 470)
            self.roverModel.reparentTo(self.gameInstance.render)
            taskMgr.add(LookatRover, "LookatRover")
            roverPosInterval = self.roverModel.posInterval(5, LPoint3f(0, 0, 0))
            roverHprInterval = self.roverModel.hprInterval(5, LVecBase3f(90, 1440, 170))
            roverHprInterval.start()
            roverPosInterval.start()
            await Task.pause(5)

        # Clean up after the animation
            taskMgr.remove("LookatRover")
            self.gameInstance.transitions.fadeOut(1)
            self.gameInstance.cam.node().getLens().setFocalLength(1.5)
            self.zoomIn = False
            self.EuropaModel.removeNode()
        
        # Crash land animation... work on this
            self.gameInstance.transitions.fadeIn(1)
            self.gameInstance.camera.setPos(0, 0, 220)
            self.gameInstance.worldVisibleModel.reparentTo(self.gameInstance.render)
            self.roverModel.setPos(600, 100, 1000)
            roverPosInterval = self.roverModel.posInterval(3, LPoint3f(100, 100, 300))
            roverPosInterval2 = self.roverModel.posInterval(.25, LPoint3f(-100, 100, 190))
        
            taskMgr.add(LookatRover, "LookatRover")
            roverPosInterval.start()
            await Task.pause(3)
            roverPosInterval2.start()
            await Task.pause(.24)

        # Cleanup after the animation
            taskMgr.remove("LookatRover")
            del self.zoomIn
            self.gameInstance.transitions.fadeOut(1)
            await Task.pause(1)
            self.blackScreen = DirectFrame(frameColor=(0, 0, 0, 1),
                                        frameSize=(-4, 4, -2, 2), 
                                        pos=(0, 0, 0), 
                                        scale=(1, 1, 1),
                                        sortOrder=-1)
            self.gameInstance.transitions.noFade()

            # Add HUD
            self.gameInstance.PlayerHUD()

            await Task.pause(2)
            self.gameInstance.textTypewriteAnimation(parent=self.gameInstance.transponderFrame, textPos=(-1.45, .1, .5), text="Warning: Crash landing detected! Rover systems...  functional.\nTransponder signal... weak.\nMission objective: Explore the planet of Europa; \nBudget Low; We need a breakthrough \nIt's all up to you, Good luck, operator.", scale=(0.04, 0.0275))
            await Task.pause(5)

        # Reparent the models to the render, making the world, and set the lights
            self.blackScreen.destroy()
            self.gameInstance.transitions.fadeIn(1)
        self.gameInstance.roverModel = self.roverModel
        self.gameInstance.playerModel = self.gameInstance.roverModel
        del self.roverModel
        self.gameInstance.world_bg.reparent_to(self.gameInstance.render)
        self.gameInstance.worldCollisionModel.reparentTo(self.gameInstance.render)
        self.gameInstance.render.setLight(self.gameInstance.sunLightNP)
        self.gameInstance.worldVisibleModel.reparentTo(self.gameInstance.render)
        self.gameInstance.render.setLight(self.gameInstance.ambientLightNP)

        # initialize the camera controller
        self.gameInstance.CameraOperator()

        with open(self.gameInstance.baseFolder + r"\save.txt", 'r') as f:
            line = f.readline()
            line = line.replace('LPoint3f(', '').replace(')', '')
            x, y, z = map(float, line.split(','))
        

        self.gameInstance.camera.setPos(x, y, z)

        # Load in our effect and a collision node for the research points. This is where the player will collect samples to advance the plot. 
        # We also set up the particle effect for when the player reaches these points, and we set up the text that will guide the player through the plot as they collect samples. 
        # This is a crucial part of the game, as it introduces the main gameplay loop and gets the player engaged with the story.
        if not self.testing:
            self.researchNode = self.gameInstance.loader.loadModel("assets/models/researchModel.bam")
            self.researchNode.setHpr(0,90,0)
            self.researchCollisionNode = self.researchNode.find("**/+CollisionNode")
            self.gameInstance.cTrav.addCollider(self.researchCollisionNode, self.gameInstance.pusher)
            self.gameInstance.pusher.addCollider(self.researchCollisionNode, self.researchNode)
            self.researchNode.reparentTo(self.gameInstance.render)
            self.researchNode.hide()
            self.researchLocationEffect = ParticleEffect()
            self.researchLocationEffect.loadConfig(Filename.fromOsSpecific(self.gameInstance.baseFolder + r"\assets\particles\researchParticles.ptf"))
            self.researchLocationEffect.clearShader()
            self.researchLocationEffect.start(self.researchNode, self.gameInstance.render)
            self.researchNode.setPos(self.pointLocations[0])
        
        # Wait for the first message
            await Task.pause(9)

        # We introduce the main gameplay loop here, where the player has to collect samples from different locations on Europa to advance the plot. 
        # Each time the player collects a sample, we update the text on the screen to guide them to the next location and provide information about their discoveries. 
        # This loop continues until they have collected all the necessary samples, at which point we can advance the plot to the next stage. 
        # This is where the player starts to feel like they are making progress in the game and uncovering the mysteries of Europa. 
        # It's important to keep the player engaged with interesting text and discoveries as they collect each sample.

        # First Sample
            self.gameInstance.textTypewriteAnimation(parent=self.gameInstance.transponderFrame, textPos=(-1.45, .1, .5), text="Operator! We need something to sustain our funding \nOur Satellite have pinged an interesting signature on the moon; \nWe've placed a small marker \nGo ahead and collect a sample by left clicking", scale=(0.04, 0.0275))
            
            # Small tutorial on how to collect samples and move
            self.tutorialFrame = DirectFrame(frameColor=(.2, .2, .2, 1),
                                        frameSize=(-1.1, 1.1, -.25, .25), 
                                        pos=(-1.45, 0, 0), 
                                        scale=(1, 1, 1), 
                                        relief=DGG.RIDGE,
                                        borderWidth=(0.05, 0.05)
                                        )
            self.tutorialText = OnscreenText(
                parent=self.tutorialFrame,
                pos=(-1, 0.15),
                scale=0.03,
                font=self.gameInstance.transmissionFont,
                align=TextNode.ALeft,
                fg=(1, 0, 1, 1),
                text="Click W to move forward\nClick A to move left\nClick S to move backward\nClick D to move right\nUse the mouse to look around\nLeft Click the satelite signals (the red particles) samples",
            )

            await Task.pause(15)
            self.tutorialFrame.destroy()

            await self.plotAsync
            self.gameInstance.hit_name = ''
            print("Sample 1 Collected")
        
        # Second Sample
            self.gameInstance.textTypewriteAnimation(parent=self.gameInstance.transponderFrame, textPos=(-1.45, .1, .5), text="Amazing! We have analyzed the sample and... Wow! \nWe are detecting high amounts of CH4 (Methane) \nBut it's not enough \nWe've pinged another signature, go ahead and collect a sample!", scale=(0.04, 0.0275))
            self.researchNode.setPos(self.pointLocations[1])
            self.eventAdvanceFunc['reset']()
            self.eventDoneFunc['finish']()
            await self.plotAsync
            self.gameInstance.hit_name = ''
            print("Sample 2 Collected")

        # Third Sample
            self.gameInstance.textTypewriteAnimation(parent=self.gameInstance.transponderFrame, textPos=(-1.45, .1, .5), text="This is astonishing! \nWe've detected high amounts of Complex Carbons! \nWe need one more sign though... Liquid water", scale=(0.04, 0.0275))
            self.researchNode.setPos(self.pointLocations[2])
            self.eventAdvanceFunc['reset']()
            self.eventDoneFunc['finish']()
            await self.plotAsync
            self.gameInstance.hit_name = ''
            print("Sample 3 Collected")

        # Instructions for the main gameplay loop for the first part of the game
            self.gameInstance.textTypewriteAnimation(parent=self.gameInstance.transponderFrame, textPos=(-1.45, .1, .5), text="Perfect! Liquid water detected! \nWe got a $500 million grant for our operations \nWe're gonna burn through it quick; We need to keep making discoveries \nNow that we see signs of life... WE NEED TO FIND LIFE", scale=(0.04, 0.0275))
            await Task.pause(12)
            self.gameInstance.textTypewriteAnimation(parent=self.gameInstance.transponderFrame, textPos=(-1.45, .1, .5), text="You have 35 samples to find life \nWith each new sample... 10 Million more to the budget \nOnce we find life, we can use the extra money for upgrades \nBased on your needs of course", scale=(0.04, 0.0275))
            
            self.FundsBar = DirectWaitBar(text="Funds:", value=100, pos=(.85, -15, -.7))
            self.FundsBar['barColor'] = (0, 0, 2, 2)
            self.FundsBar['text_scale'] = .05
            self.FundsBar['frameSize'] = (-.35, .35, -.035, .02)
            self.FundsBar['barRelief']= DGG.SUNKEN
            
            async def updateFundsBar(task):
                self.Funds -= 1_000_000
                self.FundsBar['value'] = min(100, (self.Funds / 5_000_000))
                self.FundsBar['text'] = f"Funds: ${self.Funds / 1_000_000:.1f}M"
                await Task.pause(1)
                if hasattr(self, "openedUpgradeMenu"):
                    return Task.done
                return task.cont        
            taskMgr.add(updateFundsBar, "updateFundsBar")

            self.researchNode.setPos(self.pointLocations[3])
            self.eventAdvanceFunc['reset']()
            self.eventDoneFunc['finish']()
            
            # Loop
            for i in range(3, 38):
                await self.plotAsync
                self.gameInstance.hit_name = ''
                print(f"Sample {i+1} Collected")
                self.Funds += 10_000_000
                self.gameInstance.textTypewriteAnimation(parent=self.gameInstance.transponderFrame, textPos=(-1.45, .1, .5), text=f"Sample {i+1} collected! Keep going operator!", scale=(0.04, 0.0275))
                self.researchNode.setPos(self.pointLocations[i])
                self.eventAdvanceFunc['reset']()
                self.eventDoneFunc['finish']()
            
            # Clean up and 
            self.plotChecks[0] = lambda: False  # Disable further checks for this event
            taskMgr.remove('updateFundsBar')  # Stop the task that checks for conditions to advance the plot
            self.gameInstance.textTypewriteAnimation(parent=self.gameInstance.transponderFrame, textPos=(-1.45, .1, .5), text=f"Incredible! All 35 samples collected! \nWe've detected life signatures in multiple samples \nAnd you have {self.Funds} left in your fund! \nWe need to go deeper... Time for Upgrades!", scale=(0.04, 0.0275))       
            await Task.pause(8)
        # This concludes the first part of the plot where the player collects samples to find signs of life. 
        # Next, we would transition into the upgrade phase 
        if not self.testing:
            self.gameInstance.CameraOperator()
            self.gameInstance.clearHUD()
            taskMgr.remove('updateFundsBar')
            self.UpgradeMenu()
            await self.plotAsync
            self.eventAdvanceFunc['reset']()
            self.eventDoneFunc['finish']()
            self.plotChecks[1] = lambda: False  # Disable further checks for this event

            #Transformation scene
            
            self.gameInstance.setBackgroundColor(.9, .85, .8, 1)
            self.gameInstance.cam.node().getLens().setFocalLength(1)
            self.gameInstance.world_bg.removeNode()
            self.gameInstance.roverModel.removeNode()
            self.gameInstance.worldVisibleModel.hide()
            self.gameInstance.worldCollisionModel.removeNode()
            self.gameInstance.transitions.fadeOut(.5)
            await Task.pause(1)
            self.roverSubBody = self.gameInstance.loader.loadModel("assets/models/roverSubBody.bam")
            self.roverSubBody.setScale(2)
            self.roverSubBody.setPos(0, 0, 0)
            self.roverSubBody.reparentTo(self.gameInstance.render)
            self.gameInstance.camera.setPos(20, -10, -15)
            self.gameInstance.camera.lookAt(self.roverSubBody)
            self.gameInstance.camera.setP(self.gameInstance.camera.getP() + 5)
            await Task.pause(1)
            self.gameInstance.transitions.fadeIn(1)
            await Task.pause(1)
            self.gameInstance.transitions.fadeOut(1)
            await Task.pause(1)
            self.rightJetModel = self.gameInstance.loader.loadModel("assets/models/rightJet.bam")
            self.rightJetModel.setScale(2)
            self.rightJetModel.setPos(0, -2.2, 1.8)
            self.rightJetModel.setHpr(180, 0, 0)
            self.rightJetModel.reparentTo(self.gameInstance.render)
            self.gameInstance.camera.setPos(-20, 20, 15)
            self.gameInstance.camera.lookAt(self.roverSubBody)
            await Task.pause(1)
            self.gameInstance.transitions.fadeIn(1)
            await Task.pause(1)
            self.gameInstance.transitions.fadeOut(1)
            await Task.pause(1)
            self.leftJetModel = self.gameInstance.loader.loadModel("assets/models/leftJet.bam")
            self.leftJetModel.setScale(2)
            self.leftJetModel.setPos(0, 2.2, 1.8)
            self.leftJetModel.setHpr(0, 0, 0)
            self.leftJetModel.reparentTo(self.gameInstance.render)
            self.gameInstance.camera.setPos(20, 20, 15)
            self.gameInstance.camera.lookAt(self.roverSubBody)
            await Task.pause(1)
            self.gameInstance.transitions.fadeIn(1)
            await Task.pause(1)
            self.gameInstance.transitions.fadeOut(1)
            await Task.pause(1)
            self.roverSubBody.removeNode()
            self.rightJetModel.removeNode()
            self.leftJetModel.removeNode()
            self.roverAquaticModel = self.gameInstance.loader.loadModel("assets/models/aquaticRover.bam")
            self.roverAquaticModel.setScale(2)
            self.roverAquaticModel.setPos(0, 0, -5)
            self.roverAquaticModel.reparentTo(self.gameInstance.render)
            await Task.pause(1)
            self.gameInstance.transitions.fadeIn(1)
            self.gameInstance.camera.setPos(5, 0, 0)
            self.gameInstance.cam.node().getLens().setFocalLength(0.15)
            self.gameInstance.camera.lookAt(LPoint3f(0, 0, 0))
            self.roverAquaticModel.hprInterval(3, LVecBase3f(3600, 0, 0)).start()
            self.roverAquaticModel.posInterval(1, LPoint3f(0, 0, 0)).start()
            transitionText = OnscreenText(text="Upgrades Complete! \nTime to explore the depths of Europa! \n 2 more leaps left", pos=(0, .75), scale=0.1, fg=(1, 0, 0, 1), font=self.gameInstance.loader.loadFont('assets/fonts/propaganda.ttf') ,align=TextNode.ACenter)
            await Task.pause(3)
            self.gameInstance.transitions.fadeOut(1)
            await Task.pause(1)
            transitionText.destroy()
            self.gameInstance.PlayerHUD()
            self.gameInstance.cam.node().getLens().setFocalLength(0.25)
            self.gameInstance.transitions.fadeIn(1)
            await Task.pause(1)
            self.gameInstance.CameraOperator()
            self.gameInstance.playerModel = self.roverAquaticModel
            self.gameInstance.setBackgroundColor(0, 0, .4, 1)
            self.gameInstance.textTypewriteAnimation(parent=self.gameInstance.transponderFrame, textPos=(-1.45, .1, .5), text=f"With the upgrades complete, we can now explore the depths of Europa! \nWe need to get to the core, is what the governemnt told us to keep the lights on \n Your goal is to get to the core ", scale=(0.04, 0.0275))
            await Task.pause(10)
            self.gameInstance.textTypewriteAnimation(parent=self.gameInstance.transponderFrame, textPos=(-1.45, .1, .5), text=f"We located a mantle peak \nFrom there, we'll start drilling \nGood luck operator, we're counting on you!", scale=(0.04, 0.0275))
            await Task.pause(10)
            self.gameInstance.textTypewriteAnimation(parent=self.gameInstance.transponderFrame, textPos=(-1.45, .1, .5), text=f"Use the arrow to guide you to the mantle peak \nWatch out for hostile pisces \nThey don't take kindly to intruders", scale=(0.04, 0.0275))
            
            self.tutorialFrame = DirectFrame(frameColor=(.2, .2, .2, 1),
                                        frameSize=(-1.1, 1.1, -.25, .25), 
                                        pos=(-1.45, 0, 0), 
                                        scale=(1, 1, 1), 
                                        relief=DGG.RIDGE,
                                        borderWidth=(0.05, 0.05)
                                        )
            self.tutorialText = OnscreenText(
                parent=self.tutorialFrame,
                pos=(-1, 0.15),
                scale=0.03,
                font=self.gameInstance.transmissionFont,
                align=TextNode.ALeft,
                fg=(1, 0, 1, 1),
                text="Click your left mouse button to stun the fish\nAvoid enemy fish to prevent damage\nReach the mantle peak indicated by the arrow \nCarefull, some fish take more stuns than others",
            )
            
            await Task.pause(7)
            self.tutorialFrame.destroy()

            self.pointingArrow = self.gameInstance.loader.loadModel("assets/models/arrow.bam")
            self.mountainPeakModel = self.gameInstance.loader.loadModel("assets/models/mountainPeak.bam")
            self.mountainPeakModel.setPos(165, -208, -1150)
            self.mountainPeakModel.setScale(10)
            self.mountainPeakModel.reparentTo(self.gameInstance.render)
            self.pointingArrow.reparentTo(self.gameInstance.render)
            def distanceCalculator(task):
                self.gameInstance.camera.getPos(self.gameInstance.render)
                self.mountainPeakPosition = LPoint3f(163, -149, -1000)
                scaleFactor = max(0.0, min(1.0, ((self.gameInstance.camera.getPos(self.gameInstance.render) - self.mountainPeakPosition).length() - 0) / (700 - 0)))
                self.pointingArrow.setScale(0.5 * scaleFactor)
                return Task.cont
            taskMgr.add(distanceCalculator, "distanceCalculator")
            self.gameInstance.enemies(1, 1, (-25, 0), 1)
            await self.plotAsync
            self.eventAdvanceFunc['reset']()
            self.eventDoneFunc['finish']()
            self.gameInstance.enemies(2, 2, (-30, 0), 2)
            await self.plotAsync
            self.eventAdvanceFunc['reset']()
            self.eventDoneFunc['finish']()
            self.gameInstance.enemies(3, 3, (-35, 0), 3)
            await self.plotAsync
            self.eventAdvanceFunc['reset']()
            self.eventDoneFunc['finish']()
            self.pointingArrow.removeNode()
            self.mountainPeakModel.removeNode()
        self.gameInstance.CameraOperator()
        self.LeviathonModel = Actor("assets/models/Leviathon.glb", {'attack': 'assets/models/Leviathon-attack.glb'})
        self.LeviathonModel.setScale(10)
        self.LeviathonModel.reparentTo(self.gameInstance.render)
        self.gameInstance.camera.lookAt(self.LeviathonModel)
        self.LeviathonModel.loop(self.LeviathonModel.getAnimNames()[0])

    def printPos(self):
        '''
        print('Main Frame Pos:' ,self.upgradeFrame.getPos())
        print('Main Frame Size:', self.upgradeFrame['frameSize'])
        print('Hull Frame Pos:', self.hullUpgradeFrame.getPos())
        print('Hull Frame Size:', self.hullUpgradeFrame['frameSize'])
        print('Battery Frame Pos:', self.batteryUpgradeFrame.getPos())
        print('Battery Frame Size:', self.batteryUpgradeFrame['frameSize'])
        print('Motor Frame Pos:', self.motorUpgradeFrame.getPos())
        print('Motor Frame Size:', self.motorUpgradeFrame['frameSize'])
        '''
        print(self.upgradeHullDescription.getPos())
        print(self.upgradeBatteryDescription.getPos())
        print(self.upgradeMotorDescription.getPos())
        print(self.hullUpgradeCountEnvelopingFrame.getPos())
        print(self.exitButton.getPos())
        '''
        print(self.upgradeHullButton['frameSize'])
        print(self.upgradeBatteryButton['frameSize'])
        print(self.upgradeMotorButton['frameSize'])
        '''
    def UpgradeMenu(self):
        delattr(self.gameInstance, "playerModel")
        self.openedUpgradeMenu = True
        self.hullUpgradeCount = 0
        self.batteryUpgradeCount = 0
        self.motorUpgradeCount = 0
        def upgradeHull():
            if self.gameInstance.MaxHull <= 150:  # Example cap at 150; adjust as needed
                if self.Funds > round(self.baseUpgradeCost * pow(self.growth, self.hullUpgradeCount)):
                    self.Funds -= round(self.baseUpgradeCost * pow(self.growth, self.hullUpgradeCount))
                    self.fundsText.setText(f"Funds: ${self.Funds / 1_000_000:.1f}M")
                    self.hullUpgradeCount += 1
                    setattr(self, f'upgradeHullCount{self.hullUpgradeCount}', DirectFrame(parent=self.hullUpgradeCountEnvelopingFrame, frameColor=(0, 1, .5, 1), frameSize=(-0.005, 0.005, -0.0075, 0.0075), pos=(-0.125 + self.hullUpgradeCount * 0.02, 0, 0)))
                    self.gameInstance.MaxHull += 5  # Increase max hull by 50 (adjust value as needed)
                    self.gameInstance.HullBar['range'] = self.gameInstance.MaxHull  # Update bar range dynamically
                    self.gameInstance.PlayerHull = min(self.gameInstance.PlayerHull, self.gameInstance.MaxHull)  # Clamp current hull if needed
            else:    
                self.upgradeHullButton['state'] = DGG.DISABLED  # Disable button if max hull is reached
                if not hasattr(self, 'hullMaxedText'):
                    self.hullMaxedText = OnscreenText(parent=self.hullUpgradeFrame, text="Max", pos=(.1, -0.0325), fg= (1, 0, 0, 1), scale=0.0175, align=TextNode.ALeft)
        def upgradeBattery():
            if self.gameInstance.PowerCapacity <= 150:  # Example cap at 150; adjust as needed
                if self.Funds > round(self.baseUpgradeCost * pow(self.growth, self.batteryUpgradeCount)):
                    self.Funds -= round(self.baseUpgradeCost * pow(self.growth, self.batteryUpgradeCount))
                    self.fundsText.setText(f"Funds: ${self.Funds / 1_000_000:.1f}M")
                    self.batteryUpgradeCount += 1
                    setattr(self, f'upgradeBatteryCount{self.batteryUpgradeCount}', DirectFrame(parent=self.batteryUpgradeCountEnvelopingFrame, frameColor=(0, 1, .5, 1), frameSize=(-0.005, 0.005, -0.0075, 0.0075), pos=(-0.125 + self.batteryUpgradeCount * 0.02, 0, 0)))
                    self.gameInstance.PowerCapacity += 5  # Increase power capacity by 50 (adjust value as needed)
                    self.gameInstance.PowerBar['range'] = self.gameInstance.PowerCapacity  # Update bar range dynamically
                    self.gameInstance.PowerValue = min(self.gameInstance.PowerValue, self.gameInstance.PowerCapacity)  # Clamp current power if needed
            else:
                self.upgradeBatteryButton['state'] = DGG.DISABLED  # Disable button if max power capacity is reached
                if not hasattr(self, 'batteryMaxedText'):
                    self.batteryMaxedText = OnscreenText(parent=self.batteryUpgradeFrame, text="Max", pos=(.1, -0.0325), fg= (1, 0, 0, 1), scale=0.0175, align=TextNode.ALeft)
        def upgradeMotor():
            if self.gameInstance.Speed <= 15:  # Example cap at 20; adjust as needed
                if self.Funds > round(self.baseUpgradeCost * pow(self.growth, self.motorUpgradeCount)):
                    self.Funds -= round(self.baseUpgradeCost * pow(self.growth, self.motorUpgradeCount))
                    self.fundsText.setText(f"Funds: ${self.Funds / 1_000_000:.1f}M")
                    self.motorUpgradeCount += 1
                    setattr(self, f'upgradeMotorCount{self.motorUpgradeCount}', DirectFrame(parent=self.motorUpgradeCountEnvelopingFrame, frameColor=(0, 1, .5, 1), frameSize=(-0.005, 0.005, -0.0075, 0.0075), pos=(-0.125 + self.motorUpgradeCount * 0.02, 0, 0)))
                    self.gameInstance.Speed += .5  # Increase speed by .5 (adjust value as needed)
            else:
                self.upgradeMotorButton['state'] = DGG.DISABLED  # Disable button if max speed is reached
                if not hasattr(self, 'motorMaxedText'):
                    self.motorMaxedText = OnscreenText(parent=self.motorUpgradeFrame, text="Max", pos=(.1, -0.0325), fg= (1, 0, 0, 1), scale=0.0175, align=TextNode.ALeft)
        def exitUpgradeMenu():
            self.upgradeFrame.destroy()
            self.fundsFrame.destroy()
            self.exitButton.destroy()
            self.closedUpgradeMenu = True
        self.fundsFrame = DirectFrame(frameColor=(.2, .2, .2, 1), frameSize=(-0.35, 0.35, -0.1, 0.1), pos=(1.5, 0, .5), scale=(1,1,1), relief=1)
        self.fundsText = OnscreenText(parent=self.fundsFrame, text=f"Funds: ${self.Funds / 1_000_000:.1f}M", pos=(0, 0.0), scale=0.075, align=TextNode.ACenter)
        self.upgradeFrame = DirectFrame(frameColor=(.2, .2, .2, 1),
                                        frameSize=(-.8, .8, -.8, .8), 
                                        pos=(0, 0, 0), 
                                        scale=(1.2, 1.2, 1.2), 
                                        relief=DGG.RIDGE,
                                        borderWidth=(0.05, 0.05)
                                        )
        self.hullUpgradeFrame = DirectFrame(parent=self.upgradeFrame, frameColor=(.1, .1, .1, 1), frameSize=(-.35, .35, -.1, .1), pos=(0, 0, .5), scale=(2,2,2), enableEdit=False)
        self.batteryUpgradeFrame = DirectFrame(parent=self.upgradeFrame, frameColor=(.1, .1, .1, 1), frameSize=(-.35, .35, -.1, .1), pos=(0, 0, 0), scale=(2,2,2), enableEdit=False)
        self.motorUpgradeFrame = DirectFrame(parent=self.upgradeFrame, frameColor=(.1, .1, .1, 1), frameSize=(-.35, .35, -.1, .1), pos=(0, 0, -0.5), scale=(2,2,2), enableEdit=False)
        self.upgradeHullButton = DirectButton(parent=self.hullUpgradeFrame, 
                                              frameColor=(0.5, 0.5, 0.5, 1), 
                                              frameSize=(-0.1, 0.1, -0.03, 0.06), 
                                              pos=LPoint3f(-.22, 0, -.015), 
                                              hpr=LVecBase3f(0, 0, 0), 
                                              text_font=self.gameInstance.transmissionFont,
                                              relief=1, 
                                              scale=LVecBase3f(1, 1, 1), 
                                              text_scale=(0.02, 0.02),
                                              text_pos=(0, 0.02),
                                              text='Upgrade\nHull', 
                                              text_align=TextNode.A_center,
                                              command=upgradeHull
        )
        self.upgradeBatteryButton = DirectButton(parent=self.batteryUpgradeFrame, 
                                                 frameColor=(0.5, 0.5, 0.5, 1), 
                                                 frameSize=(-0.1, 0.1, -0.03, 0.06), 
                                                 pos=LPoint3f(-.22, 0, -.015), 
                                                 hpr=LVecBase3f(0, 0, 0), 
                                                 text_font=self.gameInstance.transmissionFont,
                                                 relief=1, 
                                                 scale=LVecBase3f(1, 1, 1),
                                                 text_scale=(0.02, 0.02), 
                                                 text_pos=(0, 0.02),
                                                 text='Upgrade\nBattery', 
                                                 command=upgradeBattery
                                                 )
        self.upgradeMotorButton = DirectButton(parent=self.motorUpgradeFrame, 
                                               frameColor=(0.5, 0.5, 0.5, 1), 
                                               frameSize=(-0.1, 0.1, -0.03, 0.06), 
                                               pos=LPoint3f(-.22, 0, -.015), 
                                               hpr=LVecBase3f(0, 0, 0), 
                                               text_font=self.gameInstance.transmissionFont,
                                               relief=1,
                                               text_pos=(0, 0.02), 
                                               scale=LVecBase3f(1, 1, 1), 
                                               text_scale=(0.02, 0.02),
                                               text='Upgrade\nMotor', 
                                               command=upgradeMotor
                                               )
        self.upgradeHullDescription = OnscreenText(parent=self.hullUpgradeFrame, text="+5% Durability", pos=(-.1, .03), scale=0.02, align=TextNode.ALeft, bg=(.7, .7, .7, 1))
        self.upgradeBatteryDescription = OnscreenText(parent=self.batteryUpgradeFrame, text="+5% Power Capacity", pos=(-.1, .03), scale=0.02, align=TextNode.ALeft, bg=(.7, .7, .7, 1))
        self.upgradeMotorDescription = OnscreenText(parent=self.motorUpgradeFrame, text="+5% Speed", pos=(-.1, .03), scale=0.02, align=TextNode.ALeft, bg=(.7, .7, .7, 1))
        self.hullUpgradeIcon = DirectFrame(parent=self.hullUpgradeFrame, frameColor=(0, 0, 0, 0), frameSize=(-0.03, 0.03, -0.03, 0.03), pos=LPoint3f(.25, 0, 0), hpr=LVecBase3f(0, 0, 0), relief=1, image='assets/images/hullUpgradeIcon.png', image_scale=(0.08, 0.08, 0.08))
        self.batteryUpgradeIcon = DirectFrame(parent=self.batteryUpgradeFrame, frameColor=(0, 0, 0, 0), frameSize=(-0.03, 0.03, -0.03, 0.03), pos=LPoint3f(.25, 0, 0), hpr=LVecBase3f(0, 0, 0), relief=1, image='assets/images/batteryUpgradeIcon.png', image_scale=(0.08, 0.08, 0.08))
        self.motorUpgradeIcon = DirectFrame(parent=self.motorUpgradeFrame, frameColor=(0, 0, 0, 0), frameSize=(-0.03, 0.03, -0.03, 0.03), pos=LPoint3f(.25, 0, 0), hpr=LVecBase3f(0, 0, 0), relief=1, image='assets/images/motorUpgradeIcon.png', image_scale=(0.08, 0.08, 0.08))
        self.hullUpgradeIcon.setTransparency(TransparencyAttrib.MAlpha)
        self.batteryUpgradeIcon.setTransparency(TransparencyAttrib.MAlpha)
        self.motorUpgradeIcon.setTransparency(TransparencyAttrib.MAlpha)
        self.hullUpgradeCountEnvelopingFrame = DirectFrame(parent=self.hullUpgradeFrame, frameColor=(.4, .4, .4, 1), frameSize=(-0.12, 0.12, -0.015, 0.015), pos=LPoint3f(0.018, 0, -.0275), hpr=LVecBase3f(0, 0, 0), relief=1)
        self.batteryUpgradeCountEnvelopingFrame = DirectFrame(parent=self.batteryUpgradeFrame, frameColor=(.4, .4, .4, 1), frameSize=(-0.12, 0.12, -0.015, 0.015), pos=LPoint3f(0.018, 0, -.0275), hpr=LVecBase3f(0, 0, 0), relief=1)
        self.motorUpgradeCountEnvelopingFrame = DirectFrame(parent=self.motorUpgradeFrame, frameColor=(.4, .4, .4, 1), frameSize=(-0.12, 0.12, -0.015, 0.015), pos=LPoint3f(0.018, 0, -.0275), hpr=LVecBase3f(0, 0, 0), relief=1)
        self.exitButton = DirectButton(parent=self.upgradeFrame, frameColor=(0.5, 0.5, 0.5, 1), frameSize=(-0.2, 0.2, -0.09, 0.09), pos=LPoint3f(1.24, 0, -.15), hpr=LVecBase3f(0, 0, 0), text_font=self.gameInstance.transmissionFont, text_align=TextNode.ACenter ,relief=1, scale=LVecBase3f(1, 1, 1), text_pos=(0,-0.02), text_fg=(1,0,0,1), text_scale=(0.07, 0.07), text='Exit', command=exitUpgradeMenu)
    async def conditionBasedAdvancer(self, task):
        await Task.pause(0.5)  # Small delay to prevent tight looping

        for i in range(0, self.eventCounter):
            if self.plotChecks[i]():
                print(f"Plot Event {i} Triggered")
                self.eventAdvanceFunc['finish']()
                await self.advanceAsync
                self.eventDoneFunc['reset']()

        return Task.cont
    def __init__(self, gameInstance):
        self.gameInstance = gameInstance
        self.testing = False
        self.plotAsync = AsyncFuture()
        self.advanceAsync = AsyncFuture()
        self.eventAdvanceFunc = {'finish': lambda: self.plotAsync.set_result(None), 'reset': lambda: setattr(self, 'plotAsync', AsyncFuture())}
        self.eventDoneFunc = {'finish': lambda: self.advanceAsync.set_result(None), 'reset': lambda: setattr(self, 'advanceAsync', AsyncFuture())}
        # Use callables so conditions are evaluated fresh each loop.
        self.plotChecks = [
            # Check 0: research goal achieved — only true when gameInstance has hit_name and researchCollisionNode exists and names match
            lambda: hasattr(self.gameInstance, 'hit_name') and hasattr(self, 'researchCollisionNode') and (self.researchCollisionNode.getName() == self.gameInstance.hit_name),
            lambda: hasattr(self, 'closedUpgradeMenu'),  # Check 1: Closed Upgrade Menu — only true when the upgrade menu is closed
            lambda: hasattr(self.gameInstance, "levelDone")
        ]
        self.eventCounter = len(self.plotChecks)
        self.plotEvents = {"researchGoalAchieved": self.plotChecks[0]}

        # Event Storage, Variables, whatever you need to store for the plot
        self.pointLocations = [LPoint3f(118.48069, 35.507602, 173.39715),
                LPoint3f(-140.46547, -100.85309, 159.25064),
                LPoint3f(-262.78765, -85.375465, 173.93034),
                LPoint3f(-325.39071, -4.449741, 169.29825),
                LPoint3f(-382.43054, 101.4453, 137.1563),
                LPoint3f(-389.67944, 191.93561, 127.59272),
                LPoint3f(-347.23132, 277.0387, 92.15851),
                LPoint3f(-284.73852, 354.83175, 95.628746),
                LPoint3f(-236.08165, 371.5732, 122.47337),
                LPoint3f(-169.62724, 379.8985, 133.75111),
                LPoint3f(-95.8991, 352.017, 136.68565),
                LPoint3f(-19.416086, 331.0493, 122.97035),
                LPoint3f(46.853675, 264.72958, 124.27496),
                LPoint3f(90.75061, 224.11033, 126.57304),
                LPoint3f(167.22296, 225.10248, 121.35472),
                LPoint3f(244.48268, 272.04092, 109.59839),
                LPoint3f(291.50067, 323.3967, 116.53203),
                LPoint3f(357.60607, 369.92773, 98.937095),
                LPoint3f(411.15707, 392.13858, 87.553405),
                LPoint3f(476.01385, 341.33993, 89.037223),
                LPoint3f(486.28485, 286.83721, 100.47837),
                LPoint3f(487.89456, 221.99463, 98.18464),
                LPoint3f(459.68927, 134.7083, 97.3343),
                LPoint3f(438.48281, 84.56667, 109.779174),
                LPoint3f(383.7995, -27.694887, 112.04575),
                LPoint3f(313.93557, -27.287815, 125.492713),
                LPoint3f(234.44471, -11.153708, 130.0923),
                LPoint3f(153.96834, -58.076, 130.62211),
                LPoint3f(-51.07051, -333.6002, 86.012344),
                LPoint3f(-276.22778, -365.7992, 139.58493),
                LPoint3f(-306.20043, -271.9624, 145.96353),
                LPoint3f(-250.10818, -161.55514, 165.21084),
                LPoint3f(-149.96858, -26.882307, 172.18632),
                LPoint3f(-121.65235, 101.13438, 173.35678),
                LPoint3f(7.0617895, 175.9202, 142.39662),
                LPoint3f(70.71233, 142.88559, 159.0426),
                LPoint3f(148.71176, 112.771286, 155.41626),
                LPoint3f(238.17663, 38.95241, 129.26014)]
        self.Funds = 500_000_000  # Starting funds
        self.baseUpgradeCost = 4_500_000  # Base cost for upgrades
        self.growth = 1.33  # Growth factor for upgrade costs

        # Add the tasks to the task manager
        taskMgr.add(self.conditionBasedAdvancer, "ConditionBasedAdvancer") 
        taskMgr.add(self.plotLine, "PlotLine")

        # Debugging
        self.gameInstance.accept('u', self.UpgradeMenu)
        self.gameInstance.accept('h', self.printPos)
        self.gameInstance.accept('t', self.testingActivate)
        self.gameInstance.accept('y', self.manualPlotAdvance)

game = Game(Plot)
base.run()