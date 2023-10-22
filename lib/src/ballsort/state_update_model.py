from dataclasses import dataclass
from typing import ClassVar

MIN_X = 0
MIN_Y = 0

@dataclass
class StatePosition:
    x: int
    y: int

    def __str__(self) -> str:
        return f"x={self.x} y={self.y}"


@dataclass
class StateBall:
    __id_cnt: ClassVar[int] = 0
    pos: StatePosition
    color: str
    value: int | None = None
    label: str = ""    
    value_visible: bool = True
    id: str = "" # always overwritten in __post_init__

    @classmethod
    def __create_unique_id(cls) -> str:
        cls.__id_cnt = cls.__id_cnt + 1
        return f"{cls.__id_cnt}"

    def __post_init__(self):
        if self.id == "":
            self.id = self.__create_unique_id()

    def __str__(self) -> str:
        return f"{self.color} {self.label}"

@dataclass
class Claw:
    pos: StatePosition
    open: bool    
    min_x: int
    max_x: int
    moving_horizontally: bool
    moving_vertically: bool
    operating_claw: bool
    ball: StateBall | None

@dataclass
class Spotlight:
    on: bool
    pos: StatePosition

@dataclass
class Highlight:
    xMin: int
    xMax: int
    yMin: int
    yMax: int
    color: str

@dataclass
class StateModel:
    max_x: int
    max_y: int
    balls: list[StateBall]
    claws: list[Claw]
    goal_accomplished: bool
    spotlight: Spotlight | None
    highlights: list[Highlight] | None
    elapsed: float

@dataclass
class StateUpdateModel:
    userId: str
    state: StateModel
    delay_multiplier: float


def get_default_state() -> StateModel:
    return StateModel(
        max_x=3,
        max_y=4,
        balls=[],
        claws=[Claw(pos=StatePosition(x=0, y=0), open=True, min_x=0, max_x=100, moving_horizontally=False, moving_vertically=False, operating_claw=False, ball=None)],
        goal_accomplished=False,
        spotlight=None,
        highlights=None,
        elapsed=0.0
    )
