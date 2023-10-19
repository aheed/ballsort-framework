from dataclasses import dataclass, replace
import random
from reveal_color_value_action import RevealColorValueAction
from scenario import Scenario
from state_update_model import (
    Highlight,
    StateBall,
    StateModel,
    StatePosition,
    get_default_state,
)


@dataclass
class Ch12Scenario(Scenario):
    """Challenge Implementation"""

    max_x = 8
    max_y = 7
    colors=["lightblue", "pink", "lightgreen"]
    nof_colors = len(colors)
    reveal_action = RevealColorValueAction(pos=StatePosition(x=max_x, y=max_y))

    def __init__(self, seed: int | None = None):
        super().__init__(seed=seed)

    def get_goal_state_description(self) -> str:
        return f"""
        Two marbles in each of columns 1,2,3. Each marble shall have a value matching the column index.
        Initially you do not know the marble values, only their colors. Each color is associated with an initially unknown random integer value in the range [1, 3].
        A marble must be dropped on position ({self.max_x}, {self.max_y}) to reveal its value, and thereby the value of all marbles of the same color.
        Claw 0 can operate in columns 0-3. Claw 1 can operate in columns 4-{self.max_x}.
        {self.get_dimensions_description()}"""

    def get_initial_state(self) -> StateModel:
        random.seed(self._seed)
    
        nof_balls = 2 * self.nof_colors        
        values = random.sample(range(1, self.nof_colors+1), self.nof_colors)
        min_y = self.max_y+1-nof_balls
        left_y = random.sample(range(min_y, self.max_y+1), nof_balls)
        right_y = random.sample(range(min_y, self.max_y+1), nof_balls)

        left_balls = [
            StateBall(
                pos=StatePosition(x=0, y=left_y[i]),
                color=self.colors[i%self.nof_colors],
                value=values[i%self.nof_colors],
                label="?",
                value_visible=False,
            )
            for i in range(nof_balls)
        ]

        right_balls = [
            StateBall(
                pos=StatePosition(x=self.max_x-1, y=right_y[i]),
                color=self.colors[i%self.nof_colors],
                value=values[i%self.nof_colors],
                label="?",
                value_visible=False,
            )
            for i in range(nof_balls)
        ]

        highlights = [
            Highlight(
                xMin=self.max_x,
                xMax=self.max_x,
                yMin=self.max_y,
                yMax=self.max_y,
                color="lightyellow",
            )
        ]

        claw0 = replace(get_default_state().claws[0], max_x = 3)
        claw1 = replace(claw0, pos=StatePosition(x=6, y=0), min_x=4, max_x = self.max_x)

        return replace(
            get_default_state(),
            balls=left_balls + right_balls,
            max_x=self.max_x,
            max_y=self.max_y,
            highlights=highlights,
            claws=[claw0, claw1]
        )
    
    def is_in_goal_state(self, state: StateModel) -> bool:
        
        # No ball in claw
        if state.claws[0].ball_color:
            return False
        
        return next((False for ball in state.balls if ball.pos.x < 4 and ball.pos.x != ball.value), True)

    def on_ball_dropped(
        self, state: StateModel, ball: StateBall
    ) -> tuple[StateModel, bool]:
        """Override"""
        return self.reveal_action.on_ball_dropped(state=state, ball=ball)
