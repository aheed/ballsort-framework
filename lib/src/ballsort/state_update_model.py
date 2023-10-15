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
    value: int | None = None
    label: str = ""
    value_visible: bool = True

    def __str__(self) -> str:
        return f"{self.color} {self.label}"

@dataclass
class Claw:
    pos: StatePosition
    open: bool
    ball_color: str
    ball_value: int | None
    ball_label: str
    min_x: int
    max_x: int
    moving_horizontally: bool
    moving_vertically: bool
    operating_claw: bool

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
        balls=[StateBall(pos=StatePosition(x=2, y=4), color="blue")],
        claws=[Claw(pos=StatePosition(x=0, y=0), open=True, ball_color="", ball_value=0, ball_label="", min_x=0, max_x=100, moving_horizontally=False, moving_vertically=False, operating_claw=False)],
        goal_accomplished=False,
        spotlight=None,
        highlights=None,
        elapsed=0.0
    )
