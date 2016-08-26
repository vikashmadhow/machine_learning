
class Board:

    BLANK, X, O = 0, 1, 2
    WON, LOST = 100, -100

    def __init__(self, size=3):
        self.size = 3;
        self._positions = [[Board.BLANK for _ in range(size)] for _ in range(size)]

    def __setitem__(self, key, value):
        if Board.BLANK <= value <= Board.O:
            row, col = key
            if 0 <= row < self.size and 0 <= col < self.size:
                self._positions[row][col] = value
            else:
                raise IndexError("Only row and column positions must be between 0 and " + str(self.size - 1) + " are valid")
        else:
            raise ValueError("Only Blank(0), X(1) and O(2) are valid values")

    def __getitem__(self, key):
        row, col = key
        if 0 <= row <= 2 and 0 <= col <= 2:
            return self._positions[row][col]
        else:
            raise IndexError("Only row and column positions must be between 0 and " + str(self.size - 1) + " are valid")

    @staticmethod
    def other_player(player):
        return Board.O if player == Board.X else Board.O

    def value(self, player):
        # check horizontals
        for row in range(self.size):
            if all([self[row, col] == player for col in range(self.size)]):
                return Board.WON

        # check verticals
        for col in range(self.size):
            if all([self[row, col] == player for row in range(self.size)]):
                return Board.WON

        # check forward diagonal
        if all([self[pos, pos] == player for pos in range(self.size)]):
            return Board.WON

        # check backward diagonal
        if all([self[pos, self.size - pos - 1] == player for pos in range(self.size)]):
            return Board.WON

        if self.value(self, Board.other_player(player)) == Board.WON:
            return Board.LOST

