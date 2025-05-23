import pygame

# import the scene class
from scene import Scene
from lightSource import LightSource
from blender import load_obj_file
from BaseModel import DrawModelFromMesh
from shaders import *
from ShadowMapping import *
from sphereModel import Sphere
from skyBox import *
from environmentMapping import *

class JungleScene(Scene):
    def __init__(self):
        Scene.__init__(self)

        self.light = LightSource(self, position=[3., 9., -5.])

        self.shaders='phong'

        # For shadow map rendering
        self.shadows = ShadowMap(light=self.light)

        #Initialise the cube map environment
        self.environment = EnvironmentMappingTexture(width=400, height=400)

        meshes = load_obj_file('models/scene.obj')
        self.add_models_list(
            [DrawModelFromMesh(scene=self, M=translationMatrix([0,-2,0]), mesh=mesh, shader=ShadowMappingShader(shadow_map=self.shadows), name='scene') for mesh in meshes]
    )

        heli = load_obj_file('models/helicrash.obj')
        self.heli = [DrawModelFromMesh(scene=self, M=np.matmul(rotationMatrixY(1.2),np.matmul(translationMatrix([6,-1,3]),scaleMatrix([0.5,0.5,0.5]))), mesh=mesh, shader=ShadowMappingShader(shadow_map=self.shadows), name='heli') for mesh in heli]

        water = load_obj_file('models/water.obj')
        self.water = [DrawModelFromMesh(scene=self, M=np.matmul(translationMatrix([0,-1.9,1]),scaleMatrix([0.8,1,1])), mesh=mesh, shader=FlatShader(), name='water') for mesh in water]

        spear = load_obj_file('models/arrow.obj')
        self.spear = [DrawModelFromMesh(scene=self, M=np.matmul(translationMatrix([8,-1.7,2]),scaleMatrix([0.03,0.03,0.03])), mesh=mesh, shader=ShadowMappingShader(shadow_map=self.shadows), name='spear') for mesh in spear]

        tree = load_obj_file('models/tree.obj')
        self.tree = [DrawModelFromMesh(scene=self, M=np.matmul(translationMatrix([-7,2,0]),scaleMatrix([0.1,0.1,0.1])), mesh=mesh, shader=ShadowMappingShader(shadow_map=self.shadows), name='tree') for mesh in tree]

        tree2 = load_obj_file('models/tree.obj')
        self.tree2 = [DrawModelFromMesh(scene=self, M=np.matmul(translationMatrix([4,2,5]),scaleMatrix([0.1,0.1,0.1])), mesh=mesh, shader=ShadowMappingShader(shadow_map=self.shadows), name='tree2') for mesh in tree2]

        self.flashlight_light = LightSource(self, position=[5, -1.7, -2])
        flashlight = load_obj_file('models/torch.obj')
        self.flashlight = DrawModelFromMesh(scene=self, M=np.matmul(translationMatrix(self.flashlight_light.position),scaleMatrix([0.05,0.05,0.05])), mesh=flashlight[0], shader=EnvironmentShader(map=self.environment))

        # draw a skybox for the horizon
        self.skybox = SkyBox(scene=self)

        self.show_light = DrawModelFromMesh(scene=self, M=poseMatrix(position=self.light.position, scale=0.5), mesh=Sphere(material=Material(Ka=[10,10,10])), shader=FlatShader())

        self.selected_object = self.show_light

    def draw_shadow_map(self):
        # first we need to clear the scene, we also clear the depth buffer to handle occlusions
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        for model in self.heli:
            model.draw()
                
        for model in self.spear:
            model.draw()

        for model in self.water:
            model.draw()

        for model in self.tree:
            model.draw()
        for model in self.tree2:
            model.draw()

    def draw_reflections(self):
        self.skybox.draw()

        for model in self.models:
            model.draw()

        for model in self.heli:
            model.draw()
                
        for model in self.spear:
            model.draw()

        for model in self.water:
            model.draw()

        for model in self.tree:
            model.draw()
        for model in self.tree2:
            model.draw()


    def draw(self, framebuffer=False):
        '''
        Draw all models in the scene
        :return: None
        '''
        # first we need to clear the scene, we also clear the depth buffer to handle occlusions
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # when using a framebuffer, we do not update the camera to allow for arbitrary viewpoint.
        if not framebuffer:
            self.camera.update()

        # first, we draw the skybox
        self.skybox.draw()

        # render the shadows
        self.shadows.render(self)

        # when rendering the framebuffer we ignore the reflective object
        if not framebuffer:

            self.environment.update(self)

            #self.sphere.draw()
            self.flashlight.draw()

        # then we loop over all models in the list and draw them
        for model in self.models:
            model.draw()

        for model in self.heli:
            model.draw()
        
        for model in self.spear:
            model.draw()

        for model in self.water:
            model.draw()

        for model in self.tree:
            model.draw()
        for model in self.tree2:
            model.draw()

        self.show_light.draw()

        # once we are done drawing, we display the scene
        # Note that here we use double buffering to avoid artefacts:
        # we draw on a different buffer than the one we display,
        # and flip the two buffers once we are done drawing.
        if not framebuffer:
            pygame.display.flip()

    def keyboard(self, event):
        '''
        Process additional keyboard events for this demo.
        '''
        Scene.keyboard(self, event)
        #Select a model for translation or rotation
        if event.key == pygame.K_0:
            self.selected_object = self.show_light
        if event.key == pygame.K_1:
            self.selected_object = self.spear
        elif event.key == pygame.K_2:
            self.selected_object = self.heli
        elif event.key == pygame.K_3:
            self.selected_object = self.water
        elif event.key == pygame.K_4:
            self.selected_object = self.tree
        elif event.key == pygame.K_5:
            self.selected_object = self.tree2
        elif event.key == pygame.K_6:
            self.selected_object = self.flashlight       
        elif event.key == pygame.K_7:
            print('--> no face culling')
            glDisable(GL_CULL_FACE)

        elif event.key == pygame.K_8:
            print('--> glCullFace(GL_FRONT)')
            glEnable(GL_CULL_FACE)
            glCullFace(GL_FRONT)

        elif event.key == pygame.K_9:
            print('--> glCullFace(GL_BACK)')
            glEnable(GL_CULL_FACE)
            glCullFace(GL_BACK)


if __name__ == '__main__':
    # Initialises the scene object
    scene = JungleScene()

    # Starts drawing the scene
    scene.run()
