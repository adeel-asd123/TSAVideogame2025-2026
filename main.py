# /// script
# dependencies = [
#    "panda3d",
# ]
# ///

'''
Game made by: Adeel Siddiqi and
This is
A game made for TSA Videogame design 2025-2026 
'''
__author__ = 'Adeel Siddiqi'

import os
import random
from direct.actor.Actor import Actor
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.showbase.DirectObject import DirectObject
from direct.controls.InputState import InputState
from direct.particles.ParticleEffect import ParticleEffect
import direct.gui.DirectGuiGlobals as DGG
from panda3d.ai import AIWorld, AICharacter
from panda3d.core import (
    PandaSystem,
    FrameBufferProperties, 
    WindowProperties, 
    GraphicsOutput,
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
    CollisionSphere, 
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

        props = WindowProperties()
        props.setMouseMode(WindowProperties.MConfined)
        props.setCursorHidden(True)

        self._showbase.win.requestProperties(props)
        
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
    def __init__(self, showbase=None):
        self.showbase = base if showbase is None else showbase
        self.EnemyModelDict = {}
        self.EnemyAIDotDict = {}
        self.EnemyCollisionDict = {}
        self.EnemyAICharDict = {}
        self.EnemyAIBehaviourDict = {}
        self.EnemyHealthDict = {}
        self.EnemyAnimControlDict = {}
        self.EnemyDict = {'model':self.EnemyModelDict,
                          'ai_dot':self.EnemyAIDotDict,
                          'collision':self.EnemyCollisionDict,
                          'ai_char':self.EnemyAICharDict,
                          'ai_behaviour':self.EnemyAIBehaviourDict,
                          'health':self.EnemyHealthDict,
                          }
        self.EnemyAIWorld = AIWorld(self.showbase.render)
        self.EnemyCollisionHandler = CollisionHandlerEvent()
        self.EnemyCollisionHandler.addInPattern('into-camera')
        self.showbase.accept("into-camera",self.DamagePlayer)

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
                self.EnemyModelDict['enemy' + str(j)].setPos(random.randint(-100, 100), random.randint(-100, 100), height)
                
                # Set up shaders, pretty custom
                game.shader(EnterNode=self.EnemyModelDict['enemy' + str(j)])

                # We need to use a place holder model because the model will point at the user, so we just set position of the actual model
                self.EnemyAIDotDict['enemy' + str(j)] = self.showbase.loader.loadModel("assets/models/aidotupdater.bam")
                self.EnemyAIDotDict['enemy' + str(j)].reparentTo(self.showbase.render)
                self.EnemyAIDotDict['enemy' + str(j)].setPos(random.randint(-100, 100), random.randint(-100, 100), height)
                
                # Collision
                self.EnemyCollisionDict['enemy' + str(j)] = CollisionNode('enemy' + str(j))
                self.EnemyCollisionDict['enemy' + str(j)].addSolid(CollisionBox(LPoint3f(2, 0, 9), 4,3,12))
                self.EnemyColliderPath = self.EnemyModelDict['enemy' + str(j)].attachNewNode(self.EnemyCollisionDict['enemy' + str(j)])

                # AI
                self.EnemyAICharDict['enemy' + str(j)] = AICharacter('enemy' + str(j), self.EnemyAIDotDict['enemy' + str(j)], 100, .05, 5)
                self.EnemyAIWorld.addAiChar(self.EnemyAICharDict['enemy' + str(j)])
                self.EnemyAIBehaviourDict['enemy' + str(j)] = self.EnemyAICharDict['enemy' + str(j)].getAiBehaviors()
                self.EnemyAIBehaviourDict['enemy' + str(j)].pursue(self.showbase.camera)
                self.EnemyAIBehaviourDict['enemy' + str(j)].arrival(1)
                self.EnemyHealthDict['enemy' + str(j)] = health

                # Add collisions
                self.showbase.cTrav.addCollider(self.EnemyColliderPath, self.EnemyCollisionHandler)
                game.pusher.addCollider(self.EnemyColliderPath, self.EnemyModelDict['enemy' + str(j)])

                print("Enemy " + str(j) + " spawned")
            if self.waveCount > i:
                continue
            else:
                await self.waveMethod
                print("Wave " + str(i+2) + " done")
                self.waveMethod = AsyncFuture()
                self.WaveCounttext.setText("Wave: " + str(i+2))
                self.waveCount += 1
                self.Messagesent = False
                self.num += changePerWave
    def DamagePlayer(self, collision='nothing'):
        for i in range(len(self.EnemyDict['model'])+1):
            if 'enemy' + str(i) in str(collision) and 'camera' in str(collision):
                Game.PlayerHealth -= 1
    def EnemyHit(self, enemy):
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
                del self.EnemyDict['model'][key]
                del self.EnemyDict['ai_dot'][key]
                del self.EnemyDict['collision'][key]
                del self.EnemyDict['ai_char'][key]
                del self.EnemyDict['ai_behaviour'][key]
                del self.EnemyDict['health'][key]
                self.EnemyCount += 1
        
        if self.EnemyDict['model'] == {} and not self.Messagesent:
            self.Messagesent = True
            self.waveMethod.set_result(None)
        
        for enemy in list(self.EnemyDict['model'].values()):
            key = list(self.EnemyDict['model'].keys())[list(self.EnemyDict['model'].values()).index(enemy)]
            if not enemy.getAnimControl('hit').isPlaying() and self.EnemyDict['ai_behaviour'][key].behaviorStatus('pursue') == 'paused':
                self.EnemyDict['ai_behaviour'][key].resumeAi('all')
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
    inaMenu = True
    mouse_sensitivity = 0.5
    PlayerHealth = 100
    sunDirection = -.2
    cycleOscillation = {'dawnOrDusk' : 'down', 'notQiyamah': .45}
    keys = {'w':"forward",
            's':"backward",
            'a':"left",
            'd':"right",
#            'space':"up",
#            'e':"down"
            }
    def textTypewriteAnimation(self, textPos, text, interval=0.05):
        textSplit = list(text)
        textNode = OnscreenText(text='', pos=textPos, scale=0.07, fg=(1,0,0,1), align=TextNode.ALeft, font=self.loader.loadFont('assets/fonts/Micro5-Regular.ttf'))
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
        self.HUDMainFrame = DirectFrame(frameColor=(0.6, 0.6, 0.6, 1),
                                        frameSize=(-1.25, 1.25, -0.15, 0.15),
                                        pos=(0, 0, -.75))
        self.rover2PersonFrame = DirectFrame(frameColor=(0.2, 0.2, 0.2, 1),
                                             frameSize=(-.125, .125, -0.125, 0.125),
                                             pos=(0, 0, -.75))
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
            self.PlayerHealth = 100
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
            if not props.getForeground() or not props.getCursorHidden() or props.getMouseMode() != WindowProperties.MConfined:
                self.win.requestProperties(WindowProperties(foreground=True, mouse_mode=WindowProperties.MConfined, cursor_hidden=True))
        
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
        taskMgr.add(self.click, "clickTask")

        #self.ballDown = True
    def MouseUp(self):
        taskMgr.remove("clickTask")
        print(self.collision_queue)
        if hasattr(self, 'hit_name'):
            delattr(self, 'hit_name')
        if hasattr(self, 'ray_path'):
            self.cTrav.removeCollider(self.ray_path)  # Remove collider from traverser
            self.ray_path.removeNode()  # Safely remove the ray
            self.collision_queue.clearEntries()
        #self.ballDown = False
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
            self.inaMenu = False
        
        # If we are not in a menu, then we disable the camera controller
        # And set our bool to true, critical because our click function refocuses the window
        else:
            self.cam_controller.disable()   
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
        self.tutorialAudio = self.loader.loadSfx(r"assets/audio/tutorial.mp4")
        self.tutorialVideo.synchronizeTo(self.tutorialAudio)

        def PlayblackSliderMethod(self):
            self.tutorialAudio.stop()
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
            if self.tutorialAudio.status() == self.tutorialAudio.PLAYING:
                self.currentTime = self.tutorialAudio.getTime()
                self.tutorialAudio.stop()
            else:
                self.tutorialAudio.setTime(self.currentTime)
                self.tutorialAudio.play()
        
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
#            if self.audioSettingsOpen:

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
        def AboutSettingMethod(self):
            self.aboutLabel = DirectLabel(frameColor=(0.6, 0.6, 0.6, 1),
                                        text="About",
                                        text_scale=0.1,
                                        pos=LPoint3f(-0.025, 0, 0.85),
                                        parent=self.scrolledFrame.getCanvas(),
                                        relief=None
                                        )
            self.gameAboutLabel = DirectLabel(frameColor=(0.6, 0.6, 0.6, 1),
                                            text= "TSA Videogame Design 2025-2026 \n '' is a  game developed by \n  the team 1034-1 for the 2025-2026 \n  \
                                            Technology Student Association Competition for Video Game Design. \n this is a  based on the theme of \n\
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
            command=self.playButtonMethod.set_result,
            extraArgs=[None],
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
    def MainMenu(self):
        self.inaMenu = True
        self.mainMenuBackground = OnscreenImage(image='assets/images/mainMenuBackground.png', pos=(0, 0, 0), scale=(1.5, 1.5, 1.5))
        self.titleText = OnscreenText(text="TSA Video Game", pos=(0, .4), scale=0.25, fg=(1, 1, 1, 1), align=TextNode.ACenter)
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
    # This function is called when the mouse is clicked, calling a function based on what is clicked in game
    async def click(self, task):
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
#                for enemy in list(self.enemy.EnemyDict['collision'].values()):
#                    if hit_node.getName() == enemy.getName():
#                        self.enemyController.EnemyHit(enemy)
#                        await Task.pause(.2)
        except AssertionError as e:
            print("AssertionError occurred during collision processing.")
            print(e)
        except KeyError as e:
            print("KeyError occurred during collision processing.")
            pass
        return Task.cont
    def shader(self, nodes = None, EnterNode = None):
        self.currentModels = []
        if not hasattr(self, 'Shader_setup'):
            self.Shader_setup = None
            if PandaSystem.getPlatform() == 'win_amd64' or PandaSystem.getPlatform() == 'osx_aarch64':
                shaders = [f"{os.path.dirname(__file__)}/assets/shaders/Shader.vert", f"{os.path.dirname(__file__)}/assets/shaders/Shader.frag"]
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
    # This function loads the models in the background, reducing lag and improving performance
    async def loadScene(self):

        # in case of death, we need to reload the bool
        if hasattr(self, '_player_died'):
            delattr(self, '_player_died')  # Remove self._player_died
        
        if hasattr(self, '_player_won'):
            delattr(self, '_player_won')  # Remove self._player_won
            
        with open(f'{os.path.dirname(__file__)}/save.txt', 'r') as f:
            line = f.readline()
            line = line.replace('LPoint3f(', '').replace(')', '')
            x, y, z = map(float, line.split(','))
        

        self.camera.setPos(x, y, z)

        # Load the models in the background, each time suspending this
        # method until they are done
        self.worldCollisionModel = await self.loader.loadModel("assets/models/worldTriangles.bam", blocking=False)
        self.worldVisibleModel = await self.loader.loadModel("assets/models/worldVisible.bam", blocking=False)

        # Create a background for the world
        
        self.world_bg = await self.loader.loadModel("assets/models/skybox.bam",blocking=False)
        self.world_bg.reparent_to(self.render)
        self.world_bg.set_scale(2500)

        world_bg_texture = self.loader.loadTexture("assets/images/world_bg.png")
        world_bg_texture.set_minfilter(SamplerState.FT_linear)
        world_bg_texture.set_magfilter(SamplerState.FT_linear)
        world_bg_texture.set_wrap_u(SamplerState.WM_repeat)
        world_bg_texture.set_wrap_v(SamplerState.WM_mirror)
        world_bg_texture.set_anisotropic_degree(200)
        self.world_bg.set_texture(world_bg_texture)
        world_bg_shader = Shader.load(Shader.SL_GLSL, "assets/shaders/world_bg.vert.glsl", "assets/shaders/world_bg.frag.glsl")
        self.world_bg.set_shader(world_bg_shader) 
        
        # Create a collision node for the world
        self.world_collision_node = self.worldCollisionModel.find("**/+CollisionNode")
        self.worldCollisionModel.hide()
        self.cTrav.addCollider(self.world_collision_node, self.pusher)
        self.pusher.addCollider(self.world_collision_node, self.worldCollisionModel)

        # Set up Lighting System
        self.sunLight = DirectionalLight('directionalLight')
        self.sunLight.setShadowCaster(True, 16384, 16384)
        self.sunLightNP = self.render.attachNewNode(self.sunLight)
        self.sunLightNP.setHpr(45, 45, 0)
        self.sunLight.setColor((1.5, 1.5, 1.5, 1))
        
        self.sunModel = await self.loader.loadModel("assets/models/sun.bam", blocking=False)
        self.sunModel.setPos(150, -150, 200)

        ambientLight = AmbientLight('ambientLight')
        ambientLight.setColor((0.1, 0.1, 0.1, 1))
        ambientLightNP = self.render.attachNewNode(ambientLight)
        
        # Set the shaders
        ''' Most of the time this is very custom. Though there is a pipeline that can be used
            Most of this stuff can be recycled
        '''
        self.shader([self.sunModel, self.worldVisibleModel])
        
        # Wait for the player to start the game
        await self.playButtonMethod
        self.clickSound.play()

        # Remove the main menu
        self.titleText.destroy()
        self.btnPlay.destroy()
        self.mainMenuBackground.destroy()
        self.btnOption.destroy()
        self.btnTutorial.destroy()

        # Create a loading screen
        print("Loading Screen")
        Loading_text = OnscreenText("Loading…", scale=2, parent=self.a2dTopCenter, pos=(0, 0), fg=(1, 1, 1, 1), align=TextNode.ACenter)

        self.HealthBar = DirectWaitBar(text="Hull", value=100, pos=(-.85, -15, -.7))
        self.HealthBar['barColor'] = (0, 2, 0, 2)
        self.HealthBar['text_scale'] = .05
        self.HealthBar['frameSize'] = (-.35, .35, -.035, .02)
        self.HealthBar['barRelief']= DGG.SUNKEN

        self.HullBar = DirectWaitBar(text="Fuel", value=100, pos=(-.85, -1, -.8))
        self.HullBar['barColor'] = (2, .5, 0, 2)
        self.HullBar['text_scale'] = .05
        self.HullBar['frameSize'] = (-.35, .35, -.035, .02)
        self.HullBar['barRelief']= DGG.SUNKEN

        # Reparent the models to the render, making the world, and set the lights
        self.worldCollisionModel.reparentTo(self.render)
        self.worldVisibleModel.reparentTo(self.render)
        self.render.setLight(self.sunLightNP)
        self.render.setLight(ambientLightNP)
        self.sunModel.reparentTo(self.render)
        
        # Add HUD
        self.PlayerHUD()
        
        # Add a Pause Menu
        pausetext = OnscreenText("To Pause press P", pos=(-1.14, 0.95), scale=0.05, fg=(0, 0, 0, 1), align=TextNode.ACenter)
        self.accept('p', self.PauseMenu)

        # initialize the camera controller
        self.CameraOperator()
        
        
        
#        self.researchLocationEffect.start(parent=self.render, renderParent=self.render)
#        self.researchLocationEffect.setPos(0, 0, 250)

        #self.ball = self.loader.loadModel("assets/models/sun.bam")
        #self.ball.reparentTo(self.render)
        #self.ballDown = False
        # Start the update cycle
        taskMgr.add(self.Update, "Update")        
        self.accept('mouse1-up', self.MouseUp)
        Loading_text.destroy() 

    # The Update cycle, this function should be used to update positions and anything that needs to be updated
    def Update(self, task):
        camera_forward = self.camera.getQuat(self.render).getForward()
        camera_up = self.camera.getQuat(self.render).getUp()
        camera_right = self.camera.getQuat(self.render).getRight()
        camera_position = self.camera.getPos(self.render)

        self.dayNightCycle()
#            ak47_position = (
#                camera_position +
#                camera_forward * 2.67 -  # Forward by 1.0 units
#                camera_up * 1 +       # Downward by 0.5 units
#                camera_right * 0.8      # Rightward by 0.3 units
#            )
#            self.ak47.setPos(ak47_position)
#            self.ak47.setHpr(self.camera.getH(), 0, 90)
        
        self.worldCollisionModel.setPos(0, 0, 0)
        
        self.HealthBar['value'] = self.PlayerHealth

        if self.PlayerHealth < 0 and not hasattr(self, '_player_died'):
            self._player_died = None
            self.Death()
        
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
        
        self.currentwave = 0

        # Defining the Traverser, the task that checks for collisions, and the pusher, the task that pushes objects when it collides
        # The Traverser reports to the pusher, we also need to tell Panda3d which objects respond to collisions
        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()

        # Camera setup
        self.cam_controller = CameraControllerBehaviour(self.camera, velocity=10, gravity=-5
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
        taskMgr.add(self.loadScene())
        
        #  Tell Panda3d to listen for mouse clicks
        self.accept('mouse1', self.MouseIn)
        self.Font = self.loader.loadFont('assets/fonts/propaganda.ttf')
        self.Font.setPixelsPerUnit(120)

        self.clickSound = self.loader.loadSfx('assets/audio/click.ogg')

        self.enableParticles()

#        self.messenger.toggleVerbose()
        self.accept('x', self.exportScene)

        self.Plot = Plot(self)

        # Open the main menu
        self.MainMenu()

class Plot():
    async def plotLine(self, task):
        self.researchNode = self.gameInstance.loader.loadModel("assets/models/researchModel.bam")
        self.researchNode.setPosHpr(0, 0, 250, 0, 90, 0)
        self.researchCollisionNode = self.researchNode.find("**/+CollisionNode")
        self.gameInstance.cTrav.addCollider(self.researchCollisionNode, self.gameInstance.pusher)
        self.gameInstance.pusher.addCollider(self.researchCollisionNode, self.researchNode)
        self.researchNode.reparentTo(self.gameInstance.render)
        self.researchNode.hide()
        self.researchLocationEffect = ParticleEffect()
        os.chdir(os.path.abspath(os.path.dirname(__file__)))
        self.researchLocationEffect.loadConfig(f"{Filename.fromOsSpecific(os.path.dirname(__file__))}/assets/particles/researchParticles.ptf")
        self.researchLocationEffect.clearShader()
        self.researchLocationEffect.start(self.researchNode, self.gameInstance.render)
        await self.plotAsync
        print('very cool')
    async def conditionBasedAdvancer(self, task):
        # Evaluate dynamic check functions each iteration instead of using a stale boolean list
        for i in range(0, self.eventCounter):
            try:
                if self.plotChecks[i]():
                    self.eventAdvanceFunc['finish']()
                    await self.advanceAsync
            except Exception as e:
                # Don't crash the loop if a check can't run yet (e.g. researchCollisionNode missing)
                print("Plot check error:", e)
        return Task.cont
    def __init__(self, gameInstance):
        self.gameInstance = gameInstance
        self.plotAsync = AsyncFuture()
        self.advanceAsync = AsyncFuture()
        self.eventAdvanceFunc = {'finish': lambda: self.plotAsync.set_result(None), 'reset': lambda: self.plotAsync == AsyncFuture()}
        self.eventDoneFunc = {'finish': lambda: self.advanceAsync.set_result(None), 'reset': lambda: self.advanceAsync == AsyncFuture()}
        # Use callables so conditions are evaluated fresh each loop.
        self.plotChecks = [
            # Check 0: research goal achieved — only true when gameInstance has hit_name and researchCollisionNode exists and names match
            lambda: hasattr(self.gameInstance, 'hit_name') and hasattr(self, 'researchCollisionNode') and (self.researchCollisionNode.getName() == self.gameInstance.hit_name),
            lambda: False
        ]
        self.eventCounter = len(self.plotChecks)
        self.plotEvents = {"researchGoalAchieved": self.plotChecks[0]}
        taskMgr.add(self.conditionBasedAdvancer, "ConditionBasedAdvancer") 
        taskMgr.add(self.plotLine, "PlotLine")

game = Game(Plot)
base.run()