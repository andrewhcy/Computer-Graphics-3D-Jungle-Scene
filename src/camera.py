# import a bunch of useful matrix functions (for translation, scaling etc)
from matutils import *

class Camera:
    '''
    Base class for handling the camera.
    '''

    def __init__(self):
        self.V = np.identity(4)
        self.phi = 0.               # azimuth angle
        self.psi = 0.               # zenith angle
        self.distance = 5.         # distance of the camera to the centre point
        self.center = [0., 0., 0.]  # position of the centre
        self.update()               # calculate the view matrix

    def update(self):
        '''
        Function to update the camera view matrix from parameters.
        first, we set the point we want to look at as centre of the coordinate system,
        then, we rotate the coordinate system according to phi and psi angles
        finally, we move the camera to the set distance from the point.
        '''
        # Calculate the translation matrix for the view center
        T0 = translationMatrix(self.center)

        # Calculate the rotation matrix from the angles phi (azimuth) and psi (zenith) angles.
        R = np.matmul(rotationMatrixX(self.psi), rotationMatrixY(self.phi))

        # Calculate translation for the camera distance to the center point
        T = translationMatrix([0., 0., -self.distance])

        # Calculate the view matrix by combining the three matrices
        self.V = np.matmul(np.matmul(T, R), T0)