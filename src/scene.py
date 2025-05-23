# pygame is just used to create a window with the operating system on which to draw.
import pygame

# imports all openGL functions
from OpenGL.GL import *

# import the shader class
from shaders import *

# import the camera class
from camera import Camera

# and we import a bunch of helper functions
from matutils import *

from lightSource import LightSource

class Scene:
    '''
    This is the main class for adrawing an OpenGL scene using the PyGame library
    '''
    def __init__(self, width=1500 , height=750, shaders=None):
        '''
        Initialises the scene
        '''

        self.window_size = (width, height)

        # by default, wireframe mode is off
        self.wireframe = False

        # the first two lines initialise the pygame window. You could use another library for this,
        # for example GLut or Qt
        pygame.init()
        screen = pygame.display.set_mode(self.window_size, pygame.OPENGL | pygame.DOUBLEBUF, 24)

        # Here we start initialising the window from the OpenGL side
        glViewport(0, 0, self.window_size[0], self.window_size[1])

        # this selects the background color
        glClearColor(0.7, 0.7, 1.0, 1.0)

        # enable back face culling (see lecture on clipping and visibility
        glEnable(GL_CULL_FACE)
        # depending on your model, or your projection matrix, the winding order may be inverted,
        # Typically, you see the far side of the model instead of the front one
        # uncommenting the following line should provide an easy fix.
        #glCullFace(GL_FRONT)

        # enable the vertex array capability
        glEnableClientState(GL_VERTEX_ARRAY)

        # enable depth test for clean output (see lecture on clipping & visibility for an explanation
        glEnable(GL_DEPTH_TEST)

        # set the default shader program (can be set on a per-mesh basis)
        self.shaders = 'flat'

        # initialise the projective transform
        near = 1.0
        far = 20.0
        left = -1.0
        right = 1.0
        top = -1.0
        bottom = 1.0

        # cycle through models
        self.show_model = -1

        # to start with, we use an orthographic projection; change this.
        self.P = frustumMatrix(left, right, top, bottom, near, far)

        # initialises the camera object
        self.camera = Camera()

        # initialise the light source
        self.light = LightSource(self, position=[5., 5., 5.])

        # rendering mode for the shaders
        self.mode = 1  # initialise to full interpolated shading

        # This class will maintain a list of models to draw in the scene,
        self.models = []

    def add_model(self, model):
        '''
        This method just adds a model to the scene.
        :param model: The model object to add to the scene
        :return: None
        '''

        # bind the default shader to the mesh
        #model.bind_shader(self.shaders)

        # and add to the list
        self.models.append(model)

    def add_models_list(self, models_list):
        '''
        This method just adds a model to the scene.
        :param model: The model object to add to the scene
        :return: None
        '''
        for model in models_list:
            self.add_model(model)

    def draw(self, framebuffer=False):
        '''
        Draw all models in the scene
        :return: None
        '''

        # first we need to clear the scene, we also clear the depth buffer to handle occlusions
        if not framebuffer:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # ensure that the camera view matrix is up to date
            self.camera.update()

        # then we loop over all models in the list and draw them
        for model in self.models:
            model.draw()

        # once we are done drawing, we display the scene
        # Note that here we use double buffering to avoid artefacts:
        # we draw on a different buffer than the one we display,
        # and flip the two buffers once we are done drawing.
        if not framebuffer:
            pygame.display.flip()

    def keyboard(self, event):
        '''
        Method to process keyboard events. Check Pygame documentation for a list of key events
        :param event: the event object that was raised
        '''
        if event.key == pygame.K_q:
            self.running = False

        # flag to switch wireframe rendering
        elif event.key == pygame.K_0:
            if self.wireframe:
                print('--> Rendering using colour fill')
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
                self.wireframe = False
            else:
                print('--> Rendering using colour wireframe')
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
                self.wireframe = True

    def pygameEvents(self):
        '''
        Method to handle PyGame events for user interaction.
        '''
        # check whether the window has been closed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # keyboard events
            elif event.type == pygame.KEYDOWN:
                self.keyboard(event)
            elif event.type == pygame.MOUSEMOTION:
                #for model in self.models:
                mods = pygame.key.get_mods()
                if pygame.mouse.get_pressed()[0]:
                    if mods & pygame.KMOD_SHIFT: #Shift and hold left click to move objects
                        if self.mouse_mvt is not None:
                            self.mouse_mvt = pygame.mouse.get_rel()
                            #Calculate importance of axis when translating according to camera position
                            x_translation = np.cos(self.camera.phi)
                            z_translation = np.sin(self.camera.phi)
                            #Translates objects
                            try:
                                for model in self.selected_object:
                                    model.M = np.matmul(translationMatrix([5*self.mouse_mvt[0]*x_translation/ self.window_size[0],-5*self.mouse_mvt[1]/ self.window_size[1],5*self.mouse_mvt[0]*z_translation/ self.window_size[1]]), model.M)
                            except:
                                self.selected_object.M = np.matmul(translationMatrix([5*self.mouse_mvt[0]*x_translation/ self.window_size[0],-5*self.mouse_mvt[1]/ self.window_size[1],5*self.mouse_mvt[0]*z_translation/ self.window_size[1]]), self.selected_object.M)
                                #Local illumination is followed by show light sphere object
                                if self.selected_object == self.show_light:
                                    self.light.position = [self.show_light.M[0][3],self.show_light.M[1][3],self.show_light.M[2][3]]
                        else:
                            self.mouse_mvt = pygame.mouse.get_rel()
                elif pygame.mouse.get_pressed()[2]:
                    if mods & pygame.KMOD_SHIFT: #Shift and hold right click to rotate objects
                        if self.mouse_mvt is not None:  
                            self.mouse_mvt = pygame.mouse.get_rel()
                            #Calculate importance of axis when rotating according to camera position
                            z_rotation = np.cos(self.camera.phi)
                            x_rotation = np.sin(self.camera.phi)
                            try:
                                for model in self.selected_object:
                                    inverse = np.linalg.inv(model.M) #Find the inverse
                                    savedMatrix = model.M #Save the position of the object to be rotated
                                    model.M = np.matmul(model.M, inverse) #Reset the object to the identity matrix with the inverse, to the origin to be rotated
                                    #print(model.M)
                                    #Rotate the axes accordingly
                                    model.M = np.matmul(rotationMatrixX((self.mouse_mvt[1]*x_rotation)/31.4),model.M)
                                    model.M = np.matmul(rotationMatrixZ((self.mouse_mvt[1]*z_rotation)/31.4),model.M)
                                    model.M = np.matmul(rotationMatrixY(self.mouse_mvt[0]/31.4),model.M)
                                    model.M = np.matmul(savedMatrix, model.M)
                            except:
                                inverse = np.linalg.inv(self.selected_object.M) #Find the inverse
                                savedMatrix = self.selected_object.M #Save the position of the object to be rotated
                                self.selected_object.M = np.matmul(self.selected_object.M, inverse) #Reset the object to the identity matrix with the inverse, to the origin to be rotated
                                #print(self.selected_object.M)
                                #Rotate the axes accordingly
                                self.selected_object.M = np.matmul(rotationMatrixX((self.mouse_mvt[1]*x_rotation)/31.4),self.selected_object.M)
                                self.selected_object.M = np.matmul(rotationMatrixZ((self.mouse_mvt[1]*z_rotation)/31.4),self.selected_object.M)
                                self.selected_object.M = np.matmul(rotationMatrixY(self.mouse_mvt[0]/31.4),self.selected_object.M)
                                self.selected_object.M = np.matmul(savedMatrix, self.selected_object.M)
                        else:
                            self.mouse_mvt = pygame.mouse.get_rel()
                if pygame.mouse.get_pressed()[0]:
                    if self.mouse_mvt is not None:
                        #Move the camera up, down, left or right, moving it's center along with it
                        self.mouse_mvt = pygame.mouse.get_rel()
                        self.camera.center[0] -= (float(self.mouse_mvt[0]) / self.window_size[0])
                        self.camera.center[1] -= (float(self.mouse_mvt[1]) / self.window_size[1])
                    else:
                        self.mouse_mvt = pygame.mouse.get_rel()

                elif pygame.mouse.get_pressed()[2]:
                    if self.mouse_mvt is not None:
                        #Rotate the camera around the centre
                        self.mouse_mvt = pygame.mouse.get_rel()
                        self.camera.phi -= (float(self.mouse_mvt[0]) / self.window_size[0])
                        self.camera.psi -= (float(self.mouse_mvt[1]) / self.window_size[1])
                    else:
                        self.mouse_mvt = pygame.mouse.get_rel()
                else:
                    self.mouse_mvt = None

    def run(self):
        '''
        Draws the scene in a loop until exit.
        '''

        # We have a classic program loop
        self.running = True
        while self.running:

            self.pygameEvents()

            # otherwise, continue drawing
            self.draw()