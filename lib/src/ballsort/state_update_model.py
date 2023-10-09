from dataclasses import dataclass

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
    pos: StatePosition
    color: str
    value: int = 0
    label: str = ""

    def __str__(self) -> str:
        return f"{self.color} {self.label}"

@dataclass
class Claw:
    pos: StatePosition
    open: bool
    ball_color: str
    ball_value: int
    ball_label: str

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
    claw: Claw
    isInGoalState: bool
    moving_horizontally: bool
    moving_vertically: bool
    operating_claw: bool
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
        balls=[StateBall(pos=StatePosition(x=2, y=4), color="blue")],
        claw=Claw(pos=StatePosition(x=0, y=0), open=True, ball_color="", ball_value=0, ball_label=""),
        isInGoalState=False,
        moving_horizontally=False,
        moving_vertically=False,
        operating_claw=False,
        spotlight=None,
        highlights=None,
        elapsed=0.0
    )
