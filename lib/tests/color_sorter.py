from dataclasses import dataclass, field
import random
import sys
import pathlib

abspath = pathlib.Path(__file__).parent.joinpath("../src/ballsort").resolve()
sys.path.append(f"{abspath}")


@dataclass
class ColorSortResult:
    successful: bool
    post_move_hashes: list[int] # only relevant for successful searches
    max_moves: int # only relevant for unsuccessful searches

@dataclass
class ColorSorter:
    """Finds a sequence of moves to solve color sorting challenge"""

    max_x: int
    max_y: int
    nof_rows: int = 0 # overwritten in __post_init__ 
    nof_columns: int = 0 # overwritten in __post_init__
    nof_colors: int = 0 # overwritten in __post_init__ 
    empty_color: int = 0 # overwritten in __post_init__ 
    total_positions: int = 0
    repeat_positions: int = 0
    cache_hits: int = 0
    zobrist_dict: dict[int, int] = field(default_factory=dict) # populated in __post_init__ 
    column_zobrist_dict: dict[int, int] = field(default_factory=dict) # populated in __post_init__ 
    result_cache: dict[int, ColorSortResult] = field(default_factory=dict)

    def __get_column_zobrist_index(self, column: list[int]) -> int:
        ix = 0
        for row in range(self.nof_rows):
            ix = ix * (self.nof_colors+1) + column[row]
            #ix = ix + pow(self.nof_colors+1, row) * column[row]
        return ix
    
    #def __get_column_hash(x: int)
    
    def __calc_total_hash(self, balls: list[int]) -> int:
        hash = 0
        for column in self.__get_columns(balls=balls):
            hash = hash ^ self.column_zobrist_dict[self.__get_column_zobrist_index(column=column)]
        return hash

    def __post_init__(self):
        self.nof_rows = self.max_y + 1
        self.nof_columns = self.max_x + 1        
        self.nof_colors = self.nof_columns - 2 # assume two empty columns
        self.empty_color = self.nof_colors
        for x in range(self.nof_columns):
            for y in range(self.nof_rows):
                for color in range(self.nof_colors + 1): # +1 for the no color (no ball) case
                    self.zobrist_dict[
                        self.__get_zobrist_index(
                            ball_index=self.get_ball_index(x=x, y=y), color=color
                        )
                    ] = random.randint(0, 0xFFFFFFFFFFFFFFFF)

        c = 0
        for index in range(pow(self.nof_colors + 1, self.nof_rows)):
            c = c +1
            self.column_zobrist_dict[index] = random.randint(0, 0xFFFFFFFFFFFFFFFF)
        
        a = len(self.column_zobrist_dict)
        b = self.__get_column_zobrist_index([self.empty_color, self.empty_color, self.empty_color, self.empty_color]) + 1
        print(a, b, c)
        assert a == b
        assert 0 == self.__get_column_zobrist_index([0,0,0,0])

    def __get_zobrist_index(self, ball_index: int, color: int) -> int:
        return ball_index * (self.nof_colors) + color

    def get_ball_index(self, x: int, y: int) -> int:
        assert(x >= 0)
        assert(x <= self.max_x)
        assert(y >= 0)
        assert(y <= self.max_y)
        return x * self.nof_rows + y

    def __get_color(self, balls: list[int], x: int, y: int) -> int:
        return balls[self.get_ball_index(x=x, y=y)]
    
    def __get_column(self, balls: list[int], x: int) -> list[int]:
        return balls[x * (self.nof_rows) : (x + 1) * (self.nof_rows)]

    def __get_columns(self, balls: list[int]) -> list[list[int]]:
        return [
            self.__get_column(balls=balls, x=x)
            for x in range(self.nof_columns)
        ]

    def __is_in_goal_state(self, balls: list[int]) -> bool:
        columns = self.__get_columns(balls=balls)
        return next((False for column in columns if len(set(column)) != 1), True)

    def __get_top_index(self, balls: list[int], x: int) -> int:
        ret = self.nof_rows
        for y in range(self.nof_rows):
            if self.__get_color(balls=balls, x=x, y=y) != self.nof_colors:
                ret = y
                break
        return ret
    
    def __column_is_single_color(self, balls: list[int], x: int) -> bool:
        column = [c for c in self.__get_column(balls=balls, x=x) if c != self.empty_color]
        return len(set(column)) == 1

    def __is_move_meaningful(self, balls: list[int], move: tuple[int, int]) -> bool:
        src_x, dest_x = move
        src_y = self.__get_top_index(balls=balls, x=src_x)
        if src_y > self.max_y:
            return False  # source column is empty. Not legal.

        dest_col_top_y = self.__get_top_index(balls=balls, x=dest_x)
        if dest_col_top_y > self.max_y:
            # destination column is empty
            if self.__column_is_single_color(balls=balls, x=src_x):
                return False # source column is single color. Legal but useless.
            return True

        if dest_col_top_y == 0:
            return False  # destination column is full. Not Legal.

        return self.__get_color(balls=balls, x=src_x, y=src_y) == self.__get_color(
            balls=balls, x=dest_x, y=dest_col_top_y
        )

    def __get_meaningful_moves(self, balls: list[int]) -> list[tuple[int, int]]:
        all_moves = [
            (src_col, dest_col)
            for src_col in range(self.nof_columns)
            for dest_col in range(self.nof_columns)
            if src_col != dest_col
        ]
        return [
            move for move in all_moves if self.__is_move_meaningful(balls=balls, move=move)
        ]

    def __calc_hash(self, balls: list[int]) -> int:
        return self.__calc_total_hash(balls=balls)
        hash = 0
        for x in range(self.nof_columns):
            for y in range(self.nof_rows):
                ball_index = self.get_ball_index(x=x, y=y)
                hash = (
                    hash
                    ^ self.zobrist_dict[
                        self.__get_zobrist_index(
                            ball_index=ball_index, color=balls[ball_index]
                        )
                    ]
                )
        return hash
    
    def __make_move(self, balls: list[int], src_x: int, dest_x: int) -> list[int]:
        src_y = self.__get_top_index(balls=balls, x=src_x)
        dest_y = self.__get_top_index(balls=balls, x=dest_x) - 1
        src_index = self.get_ball_index(x=src_x, y=src_y)
        dest_index = self.get_ball_index(x=dest_x, y=dest_y)
        post_move_state = balls.copy()
        post_move_state[dest_index] = balls[src_index]
        post_move_state[src_index] = self.nof_colors
        return post_move_state

    def __find_winning_sequence_recursive(self, 
        balls: list[int], previous_positions: set[int], position_hash: int, max_moves: int
    ) -> ColorSortResult:

        if position_hash in self.result_cache:
            cached_result = self.result_cache[position_hash]
            if cached_result.successful or cached_result.max_moves >= max_moves:
                #print("cache hit")
                self.cache_hits = self.cache_hits + 1
                return cached_result
        
        if self.__is_in_goal_state(balls=balls):
            ret = ColorSortResult(successful=True, post_move_hashes=[], max_moves=max_moves)
            self.result_cache[position_hash] = ret
            return ret

        best_move_result = ColorSortResult(successful=False, post_move_hashes=[], max_moves=max_moves)
        max_submoves = max_moves-1
        fewest_moves = 10000
        if max_submoves > 0:
            for move in self.__get_meaningful_moves(balls=balls):
                src_x, dest_x = move

                post_move_state = self.__make_move(balls=balls, src_x=src_x, dest_x=dest_x)
                self.total_positions = self.total_positions + 1

                # new_position_hash = __calc_hash_incrementally(start_hash=position_hash, move=move)
                new_position_hash = self.__calc_hash(balls=post_move_state)

                if new_position_hash not in previous_positions:
                    all_positions = previous_positions.union({new_position_hash})

                    move_result = self.__find_winning_sequence_recursive(
                        balls=post_move_state,
                        previous_positions=all_positions,
                        position_hash=new_position_hash,
                        max_moves=max_submoves
                    )
                    
                    nof_submoves = len(move_result.post_move_hashes)
                    if move_result.successful and nof_submoves < fewest_moves:
                        fewest_moves = nof_submoves
                        best_move_result = ColorSortResult(successful=True, post_move_hashes=[new_position_hash]+move_result.post_move_hashes, max_moves=max_moves)
                        max_submoves = nof_submoves
                        #print(f"new best: {max_submoves}\n{best_move_result.moves}")
                        #return ColorSortResult(successful=True, moves=[move] + move_result.moves)
                        #return best_move_result
                else:
                    self.repeat_positions = self.repeat_positions + 1

        self.result_cache[position_hash] = best_move_result
        return best_move_result
    
    def __get_move_sequence(self, balls: list[int], sort_result: ColorSortResult) -> list[tuple[int, int]]:
        moves: list[tuple[int, int]] = []
        confirmed_state = balls
        for hash in sort_result.post_move_hashes:
            for move in self.__get_meaningful_moves(balls=confirmed_state):
                src_x, dest_x = move
                post_move_state = self.__make_move(balls=confirmed_state, src_x=src_x, dest_x=dest_x)
                new_position_hash = self.__calc_hash(balls=post_move_state)
                if new_position_hash == hash:
                    moves.append(move)
                    confirmed_state = post_move_state
                    break
        return moves

    def find_winning_sequence(self, balls: list[int]) -> list[tuple[int, int]]:
        hash = self.__calc_hash(balls=balls)
        search_result = self.__find_winning_sequence_recursive(
            balls=balls, previous_positions=set(), position_hash=hash, max_moves=200
        )
        if not search_result.successful:
            raise ValueError("Unwinnable starting position")
        move_sequence = self.__get_move_sequence(balls=balls, sort_result=search_result)
        return move_sequence
    
