import unittest

from robolib.settings import settings
from robolib.log import logger
import numpy as np

class TestHandler(unittest.TestCase):

    def test_app_settings_config(self):
        s = settings
        assert settings.config is not None
        assert settings.quadruped.dims.femur > 0
        assert settings.quadruped.servo_ids[0][0] == settings.quadruped.servos[0][0]
        assert settings.camera.calibration.image_width == 1640
        assert settings.camera.calibration.distortion_coefficients[0][0] == -0.29685
        assert settings.imu.offsets.magnetic == (419, -250, -597)
        assert settings.quadruped.position_home is not None
        assert np.sum(settings.quadruped.actuator_angle_zero - np.radians(np.array([[0, 90, 30], [0, 90, 30], [0, 90, 30], [0, 90, 30]]))) == 0
        logger.info("""================ settings ==================""")
        for (k,v) in settings.dict().items():
            logger.info(f"{k}: {v}\n")

