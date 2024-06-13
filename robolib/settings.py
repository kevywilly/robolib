from typing import Dict, Optional, Tuple, Any

import numpy as np
import yaml
from pydantic import BaseModel, computed_field, ValidationError
from pydantic.functional_validators import BeforeValidator
from pydantic_settings import BaseSettings
from typing_extensions import Annotated

from robolib.vision.sensors import CameraSensor


def convert_numpy(value: Any) -> np.ndarray:
    if isinstance(value, Dict):
        return NumpyArray.model_validate(value).numpy
    elif isinstance(value, np.ndarray):
        return value
    else:
        raise ValidationError(f"Invalid type {type(value)} for conversion to np.ndarray via NPArray")


def numpy_int(value: np.ndarray) -> np.ndarray:
    return convert_numpy(value).astype(int)


def numpy_float(value: np.ndarray) -> np.ndarray:
    return convert_numpy(value).astype(float)


NumpyInt = Annotated[np.ndarray, BeforeValidator(numpy_int)]
NumpyFloat = Annotated[np.ndarray, BeforeValidator(numpy_float)]


def load_config(config_file) -> Dict:
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)


class NumpyArray(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    rows: int
    cols: int
    data: list

    @computed_field
    def numpy(self) -> np.ndarray:
        return np.array(self.data).reshape(self.rows, self.cols)

    @classmethod
    def zeros(cls, rows: int, cols: int):
        return NumpyArray(
            rows=rows,
            cols=cols,
            data=list(np.zeros((rows, cols)).flatten())
        )

    @classmethod
    def fill(cls, rows: int, cols: int, value: any):
        return NumpyArray(
            rows=rows,
            cols=cols,
            data=list(np.zeros((rows, cols)).flatten() + value)
        )


class ImuOffsets(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    magnetic: Optional[Tuple[int, int, int]] = (0, 0, 0)
    gyro: Optional[Tuple[int, int, int]] = (0, 0, 0)
    accel: Optional[Tuple[int, int, int]] = (0, 0, 0)


class ImuSettings(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    offsets: Optional[ImuOffsets] = ImuOffsets()
    bn0_axis_remap: Optional[Tuple] = (0, 1, 2, 1, 0, 1)


class QDimensions(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    width: Optional[float] = 0.0
    length: Optional[float] = 0.0
    coxa: Optional[float] = 0.0
    femur: Optional[float] = 0.0
    tibia: Optional[float] = 0.0


class Quadruped(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    dims: QDimensions = QDimensions()
    servo_ids: Optional[NumpyInt] = np.zeros((1, 12))
    actuator_angle_zero: Optional[NumpyInt] = np.zeros((4, 3))
    actuator_angle_flip: Optional[NumpyInt] = np.zeros((4, 3)) + 1
    ready_position_height_pct: Optional[float] = 0.5
    ready_position_offsets: Optional[NumpyInt] = np.zeros((4, 3))
    home_position_offsets: Optional[NumpyInt] = np.zeros((4, 3))

    @computed_field
    def servos(self) -> np.ndarray:
        return np.array(self.servo_ids).reshape(4, 3)

    @property
    def max_height(self) -> float:
        return self.dims.femur + self.dims.tibia

    @property
    def lengths(self) -> np.ndarray:
        return np.array([self.coxa, self.femur, self.tibia])

    @computed_field
    def position_home(self) -> np.ndarray:
        return np.zeros((4, 3)).astype(np.float16) + [0, 0, self.max_height] + self.home_position_offsets

    @computed_field
    def position_ready(self) -> np.ndarray:
        return (self.ready_position_height_pct * self.position_home) + self.ready_position_offsets

    @computed_field
    def position_crouch(self) -> np.ndarray:
        return self.position_ready * 0.4


class CameraCalibration(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    image_width: Optional[int] = 1640
    image_height: Optional[int] = 1232
    camera_matrix: Optional[NumpyFloat] = np.zeros((3, 3))
    distortion_model: Optional[str] = "plumb_bob"
    distortion_coefficients: Optional[NumpyFloat] = np.zeros((1, 5))
    rectification_matrix: Optional[NumpyFloat] = np.zeros((3, 3))
    projection_matrix: Optional[NumpyFloat] = np.zeros((3, 4))


class CameraSettings(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    sensor_mode: Optional[int] = CameraSensor.MODE1640x1232X29
    calibration: Optional[CameraCalibration] = None


class AppSettings(BaseSettings):
    config_file: str = '/users/kevywilly/Projects/robolib/config.yaml'

    @computed_field
    def serial_port(self) -> str:
        return self.config.get("serial_port", "/dev/serial0")

    @computed_field
    def config(self) -> Dict:
        return load_config(config_file=self.config_file)

    @computed_field
    def quadruped(self) -> Optional[Quadruped]:
        return Quadruped.model_validate(self.config.get('quadruped', {}))

    @computed_field
    def imu(self) -> Optional[ImuSettings]:
        return ImuSettings.model_validate(self.config.get('imu', {}))

    @computed_field
    def camera(self) -> CameraSettings:
        return CameraSettings.model_validate(self.config.get("camera", {}))


settings = AppSettings()
