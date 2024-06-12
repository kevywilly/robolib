import unittest

from robolib.interfaces.vector import Vector3
from robolib.motion.quadruped_kinematics import QuadrupedKinematics


class TestHandler(unittest.TestCase):
    coxa=50
    femur=100
    tibia=120

    kinematics = QuadrupedKinematics(coxa=50, femur=100, tibia=120)

    def test_quadruped_forward(self):
        fk = Vector3.from_numpy(self.kinematics.fk_degrees(Vector3(0,0,0).numpy()))
        assert fk == Vector3(220, 0, 0)

        fk = Vector3.from_numpy(self.kinematics.fk_degrees(Vector3(0, 0, 90).numpy()))
        assert fk == Vector3(100., 0., 120.)

        fk = Vector3.from_numpy(self.kinematics.fk_degrees(Vector3(0, 0, 45).numpy()))
        assert fk.z < 120

    def test_quadruped_inverse(self):

        position = Vector3(220,0,0).numpy()
        ik = self.kinematics.ik_degrees(position)
        assert Vector3.from_numpy(ik) == Vector3(0,0,0)

        position = Vector3(100, 0, 120).numpy()
        ik = self.kinematics.ik_degrees(position)
        assert Vector3.from_numpy(ik) == Vector3(0, 0, 90)

        position = Vector3(90, 0, 100).numpy()
        ik = self.kinematics.ik_degrees(position)
        angles = Vector3.from_numpy(ik)
        assert angles.y < 0
        assert angles.z > 90





