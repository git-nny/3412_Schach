import numpy as np

class Piece:
    """
    Base class for pieces on the board. 
    
    A piece holds a reference to the board, its color and its currently located cell.
    In this class, you need to implement two methods, the "evaluate()" method and the "get_valid_cells()" method.
    """
    def __init__(self, board, white):
        """
        Constructor for a piece based on provided parameters

        :param board: Reference to the board this piece is placed on
        :type board: :ref:class:`board`
        """
        self.board = board
        self.white = white
        self.cell = None



    def is_white(self):
        """
        Returns whether this piece is white

        :return: True if the piece white, False otherwise
        """
        return self.white

    def can_enter_cell(self, cell):
        """
        Shortcut method to see if a cell on the board can be entered.
        Simply calls :py:meth:`piece_can_enter_cell <board.Board.piece_can_enter_cell>` from the current board class.

        :param cell: The cell to check for. Must be a unpackable (row, col) type.
        :return: True if the provided cell can enter, False otherwise
        """
        return self.board.piece_can_enter_cell(self, cell)

    def can_hit_on_cell(self, cell):
        """
        Shortcut method to see if this piece can hit another piece on a cell.
        Simply calls :py:meth:`piece_can_hit_on_cell <board.Board.piece_can_hit_on_cell>` from the current board class.

        :param cell: The cell to check for. Must be a unpackable (row, col) type.
        :return: True if the piece can hit on the provided cell, False otherwise
        """
        return self.board.piece_can_hit_on_cell(self, cell)

    def evaluate(self) -> int:
        """
        **TODO** Implement a meaningful numerical evaluation of this piece on the board.
        This evaluation happens independent of the color as later, values for white pieces will be added and values for black pieces will be substracted. 
        
        **HINT** Making this method *independent* of the pieces color is crucial to get a *symmetric* evaluation metric in the end.
         
        - The pure existance of this piece alone is worth some points. This will create an effect where the player with more pieces on the board will, in sum, get the most points assigned. 
        - Think of other criteria that would make this piece more valuable, e.g. movability or whether this piece can hit other pieces. Value them accordingly.
        
        :return: Return numerical score between -infinity and +infinity. Greater values indicate better evaluation result (more favorable).
        """
        # TODO: Implement
        # Michel
        # Turn on/off 'Thread points'
        # Modes: 'Threat' | None = Standard-Mode
        # mode = "Threat"
        mode = None

        def add_points(piece: Piece) -> int:
            """Add points to the score."""
            # Piece value dictionary
            piece_types_and_values = {Pawn: 100,
                                      Rook: 500,
                                      Knight: 300,
                                      Bishop: 400,
                                      Queen: 900,
                                      King: 100_000}

            # Return a value depending on Piece type
            for piece_type, piece_value in piece_types_and_values.items():
                if isinstance(piece, piece_type):
                    return piece_value

            return 0

        def add_threat_points() -> int:
            """Pieces gain even more points for 'threatening' opponent pieces after a move"""
            val = 0
            valid_cells = self.get_valid_cells()
            reachable_enemies = (self.board.get_cell(cell) for cell in valid_cells if self.board.get_cell(cell))

            # Add points on top of this piece's base score depending on what type of enemy and how many they can hit.
            for enemy in reachable_enemies:
                val += add_points(enemy) * (0.01 if not isinstance(enemy, King) else 0.001)

            return val

        score = add_points(self)

        # Check if 'Thread points' are active
        if mode == "Threat":
            score += add_threat_points()

        return score

    def get_valid_cells(self) -> list[tuple[int, int]]:
        """
        **TODO** Return a list of **valid** cells this piece can move into. 
        
        A cell is valid if 
          a) it is **reachable**. That is what the :py:meth:`get_reachable_cells` method is for and
          b) after a move into this cell the own king is not (or no longer) in check.

        **HINT**: Use the :py:meth:`get_reachable_cells` method of this piece to receive a list of reachable cells.
        Iterate through all of them and temporarily place the piece on this cell. Then check whether your own King (same color)
        is in check. Use the :py:meth:`is_king_check_cached` method to test for checks. If there is no check after this move, add
        this cell to the list of valid cells. After every move, restore the original board configuration. 
        
        To temporarily move a piece into a new cell, first store its old position (self.cell) in a local variable. 
        The target cell might have another piece already placed on it. 
        Use :py:meth:`get_cell <board.BoardBase.get_cell>` to retrieve that piece (or None if there was none) and store it as well. 
        Then call :py:meth:`set_cell <board.BoardBase.set_cell>` to place this piece on the target cell and test for any checks given. 
        After this, restore the original configuration by placing this piece back into its old position (call :py:meth:`set_cell <board.BoardBase.set_cell>` again)
        and place the previous piece also back into its cell. 
        
        :return: Return True 
        """
        # TODO: Implement
        # Michel
        # Create an empty list and save current position and all reachable cells
        valid_cells = []
        reachable_cells = self.get_reachable_cells()
        old_pos = self.cell

        # Iterate over every reachable cell and store the piece on it (or None)
        for temp_pos in reachable_cells:
            piece = self.board.get_cell(temp_pos)

            # Change the board configuration to the new position and check if own king is 'check'
            self.board.set_cell(temp_pos, self)

            if not self.board.is_king_check_cached(self.is_white()):
                valid_cells.append(temp_pos)

            # Return the board to its original state
            self.board.set_cell(old_pos, self)

            if piece:
                self.board.set_cell(temp_pos, piece)
        
        return valid_cells

class Pawn(Piece):  # Bauer
    def __init__(self, board, white):
        super().__init__(board, white)

    def get_reachable_cells(self) -> list[tuple[int, int]]:
        """
        **TODO** Implement the movability mechanik for `pawns <https://de.wikipedia.org/wiki/Bauer_(Schach)>`_. 

        **NOTE**: Here you do not yet need to consider whether your own King would become checked after a move. This will be taken care of by
        the :py:meth:`is_king_check <board.Board.is_king_check>` and :py:meth:`get_valid_cells <pieces.Piece.get_valid_cells>` methods.

        **HINT**: Pawns can move only forward (towards the opposing army). Depening of whether this piece is black of white, this means pawn
        can move only to higher or lower rows. Normally a pawn can only move one cell forward as long as the target cell is not occupied by any other piece. 
        If the pawn is still on its starting row, it can also dash forward and move two pieces at once (as long as the path to that cell is not blocked).
        Pawns can only hit diagonally, meaning they can hit other pieces only the are one cell forward left or one cell forward right from them. 

        You can call :py:meth:`cell_is_valid_and_empty <board.Board.cell_is_valid_and_empty>`, 
        :py:meth:`can_hit_on_cell <pieces.Piece.can_hit_on_cell>` and :py:meth:`can_enter_cell <pieces.Piece.can_enter_cell>` 
        to check for necessary conditions to implement the pawn movability mechanics. 

        **NOTE**: For all you deep chess experts: Hitting `en passant <https://de.wikipedia.org/wiki/En_passant>`_ does not need to be implemented.
        
        :return: A list of reachable cells this pawn could move into.
        """
        # TODO: Implement a method that returns all cells this piece can enter in its next move
        # Michel
        # Create an empty list and set the Pawns direction and home row depending on their colour
        reachable_cells = []
        dir_y = 1 if self.is_white() else -1
        home_row = 1 if self.is_white() else 6

        # Unpack position and set Pawn's move range depending on it's position
        curr_y, curr_x = self.cell
        move_range = 3 if curr_y == home_row else 2  # 3 and 2 since range() stop parameter is exclusive

        # Iterate over vertical cells (range 1-2), add to list if empty and break if front is blocked
        for val in range(1, move_range):
            move_pos = ((dir_y * val + curr_y), curr_x)

            if not self.board.cell_is_valid_and_empty(move_pos):
                break

            reachable_cells.append(move_pos)

        # Iterate over diagonal cells (range 1), add to list if enemy is on cell
        for val in (1, -1):
            hit_pos = ((curr_y + dir_y), (curr_x + val))

            if self.can_hit_on_cell(hit_pos):
                reachable_cells.append(hit_pos)

        return reachable_cells

class Rook(Piece):  # Turm
    def __init__(self, board, white):
        super().__init__(board, white)

    def get_reachable_cells(self) -> list[tuple[int, int]]:
        """
        **TODO** Implement the movability mechanic for `rooks <https://de.wikipedia.org/wiki/Turm_(Schach)>`_. 

        **NOTE**: Here you do not yet need to consider whether your own King would become checked after a move. This will be taken care of by
        the :py:meth:`is_king_check <board.Board.is_king_check>` and :py:meth:`get_valid_cells <pieces.Piece.get_valid_cells>` methods.

        **HINT**: Rooks can move only horizontally or vertically. They can move an arbitrary amount of cells until blocked by an own piece
        or an opposing piece (which they could hit and then being stopped).

        You can call :py:meth:`cell_is_valid_and_empty <board.Board.cell_is_valid_and_empty>`, 
        :py:meth:`can_hit_on_cell <pieces.Piece.can_hit_on_cell>` and :py:meth:`can_enter_cell <pieces.Piece.can_enter_cell>` 
        to check for necessary conditions to implement the rook movability mechanics. 

        :return: A list of reachable cells this rook could move into.
        """
        # TODO: Implement a method that returns all cells this piece can enter in its next move
        # Michel
        # Create an empty list, a direction patterns tuple and unpack current position
        reachable_cells = []
        dir_patterns = ((1, 0),
                        (-1, 0),
                        (0, 1),
                        (0, -1))
        curr_y, curr_x = self.cell
        
        # Iterate over every possible direction (horizontally and vertically)
        for dir_y, dir_x in dir_patterns:
            dir_clear = True
            count = 0

            # Check if a cell is reachable, one cell at a time
            # Increase/Decrease the x and y values depending on direction pattern until direction is no longer clear
            # Append if cell is clear
            while dir_clear:
                count += 1
                new_pos = ((count * dir_y + curr_y), (count * dir_x + curr_x))
                
                # Break if direction is blocked by ally or cell is invalid
                if not self.can_enter_cell(new_pos):
                    break
                
                # Change direction if there is an enemy, but append cell to list
                elif self.can_hit_on_cell(new_pos):
                    dir_clear = False
                
                reachable_cells.append(new_pos)
        
        return reachable_cells

class Knight(Piece):  # Springer
    def __init__(self, board, white):
        super().__init__(board, white)

    def get_reachable_cells(self):
        """
        **TODO** Implement the movability mechanic for `knights <https://de.wikipedia.org/wiki/Springer_(Schach)>`_. 

        **NOTE**: Here you do not yet need to consider whether your own King would become checked after a move. This will be taken care of by
        the :py:meth:`is_king_check <board.Board.is_king_check>` and :py:meth:`get_valid_cells <pieces.Piece.get_valid_cells>` methods.

        **HINT**: Knights can move in a special pattern. They can move two rows up or down and then one column left or right. Alternatively, they can
        move one row up or down and then two columns left or right. They are not blocked by pieces in between. 

        You can call :py:meth:`cell_is_valid_and_empty <board.Board.cell_is_valid_and_empty>`, 
        :py:meth:`can_hit_on_cell <pieces.Piece.can_hit_on_cell>` and :py:meth:`can_enter_cell <pieces.Piece.can_enter_cell>` 
        to check for necessary conditions to implement the rook movability mechanics. 

        :return: A list of reachable cells this knight could move into.
        """
        # TODO: Implement a method that returns all cells this piece can enter in its next move
        # Alesatir

        reachable_cells = []
        y, x= self.cell
        pos_cells = [(y-2,x-1),(y-1,x-2),(y+1,x-2),(y+2,x-1),(y+2,x+1),(y+1,x+2),(y-1,x+2),(y-2,x+1)]   # Alle theorerisch möglichen Zellen
        
        for cell in pos_cells:                                      # Über alle theoretisch möglichen Zellen itterieren
            if self.board.cell_is_valid_and_empty(cell):            # Wenn Zelle leer, appenden
                reachable_cells.append(cell)
            elif self.can_enter_cell(cell):                         # Wenn nicht leer, geg. Figur?
                if self.can_hit_on_cell(cell):
                    reachable_cells.append(cell)
        return reachable_cells

class Bishop(Piece):  # Läufer
    def __init__(self, board, white):
        super().__init__(board, white)

    def get_reachable_cells(self):
        """
        **TODO** Implement the movability mechanic for `bishop <https://de.wikipedia.org/wiki/L%C3%A4ufer_(Schach)>`_. 

        **NOTE**: Here you do not yet need to consider whether your own King would become checked after a move. This will be taken care of by
        the :py:meth:`is_king_check <board.Board.is_king_check>` and :py:meth:`get_valid_cells <pieces.Piece.get_valid_cells>` methods.

        **HINT**: Bishops can move diagonally an arbitrary amount of cells until blocked.

        You can call :py:meth:`cell_is_valid_and_empty <board.Board.cell_is_valid_and_empty>`, 
        :py:meth:`can_hit_on_cell <pieces.Piece.can_hit_on_cell>` and :py:meth:`can_enter_cell <pieces.Piece.can_enter_cell>` 
        to check for necessary conditions to implement the rook movability mechanics. 

        :return: A list of reachable cells this bishop could move into.
        """
        # TODO: Implement a method that returns all cells this piece can enter in its next move  - ricarda

        
        directions = [ (-1, -1), (-1, 1), (1, -1), (1, 1)] # movement pattern for directions
        positions = [] 

        def get_available_cells_in_direction(position_tuple, count=1):

            cell_y, cell_x =  position_tuple # starting position
            new_pos = (cell_y + direction[0] * count, cell_x + direction[1] * count)

            # end condition: if cell is invalid or occupied, end run 
            if not self.board.cell_is_valid_and_empty(new_pos):
                if self.can_hit_on_cell(new_pos): # adds latest cell if the cell contains opposing piece
                    positions.append(new_pos)
                    
            else:
                positions.append(new_pos)
                count += 1
                get_available_cells_in_direction( position_tuple, count ) # check next cell in row until end condition is hit

        # run function for every direction in movement patterns
        for direction in directions:
            get_available_cells_in_direction(self.cell)

        return positions


class Queen(Piece):  # Königin
    def __init__(self, board, white):
        super().__init__(board, white)

    def get_reachable_cells(self):
        """
        **TODO** Implement the movability mechanic for the `queen <https://de.wikipedia.org/wiki/Dame_(Schach)>`_. 

        **NOTE**: Here you do not yet need to consider whether your own King would become checked after a move. This will be taken care of by
        the :py:meth:`is_king_check <board.Board.is_king_check>` and :py:meth:`get_valid_cells <pieces.Piece.get_valid_cells>` methods.

        **HINT**: Queens can move horizontally, vertically and diagonally an arbitrary amount of cells until blocked. They combine the movability
        of rooks and bishops. 

        You can call :py:meth:`cell_is_valid_and_empty <board.Board.cell_is_valid_and_empty>`, 
        :py:meth:`can_hit_on_cell <pieces.Piece.can_hit_on_cell>` and :py:meth:`can_enter_cell <pieces.Piece.can_enter_cell>` 
        to check for necessary conditions to implement the rook movability mechanics. 

        :return: A list of reachable cells this queen could move into.
        """
        # TODO: Implement a method that returns all cells this piece can enter in its next move
        # Alestair

        reachable_cells = []
        direction = [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,-1), (1,1)] # y:1 x:2     # Alle möglichen Richtungen

        for move in direction:
            for i in range(1, 9):                                                   # Loop für jeden Step
                start_y, start_x = self.cell                                        # Anfangsposition entpacken
                move_y, move_x =move                                                # Richtung entpacken
                new_pos = ((start_y + move_y * i), (start_x + move_x * i))          # Richtung * Step + Anfangsposition

                if self.board.cell_is_valid_and_empty(new_pos):                     # Wenn neue Pos. leer, append
                    reachable_cells.append(new_pos)
                elif self.can_enter_cell(new_pos):                                  # Wenn neue Pos. nicht leer, geg. Figur?                
                    if self.can_hit_on_cell(new_pos):
                        reachable_cells.append(new_pos)                             # Wenn geg. Figur, Zelle möglich aber danach stopp
                        break
                else:                                                               # Wenn keine validen Zelle mehr, beenden
                    break
        return reachable_cells
        

class King(Piece):  # König
    def __init__(self, board, white):
        super().__init__(board, white)

    def get_reachable_cells(self):
        """
        **TODO** Implement the movability mechanic for the `king <https://de.wikipedia.org/wiki/K%C3%B6nig_(Schach)>`_. 

        **NOTE**: Here you do not yet need to consider whether your own King would become checked after a move. This will be taken care of by
        the :py:meth:`is_king_check <board.Board.is_king_check>` and :py:meth:`get_valid_cells <pieces.Piece.get_valid_cells>` methods.

        **HINT**: Kings can move horizontally, vertically and diagonally but only one piece at a time.

        You can call :py:meth:`cell_is_valid_and_empty <board.Board.cell_is_valid_and_empty>`, 
        :py:meth:`can_hit_on_cell <pieces.Piece.can_hit_on_cell>` and :py:meth:`can_enter_cell <pieces.Piece.can_enter_cell>` 
        to check for necessary conditions to implement the rook movability mechanics. 

        :return: A list of reachable cells this king could move into.
        """
        # TODO: Implement a method that returns all cells this piece can enter in its next move - Ricarda
        
        # get current cell and neighboring cells on current row
        y, x = self.cell
        pos_modifier = [ -1, 0, 1 ]
        positions_x = [ ( y, x + modifier) for modifier in pos_modifier ] 
        new_position = []

        # get all cells from row and add top and bottom cells to the array
        for position_y, position_x in positions_x:
            for modifier in pos_modifier: 
                new_position.append((position_y + modifier, position_x )) 

        # checks if cell is valid, and can be entered via attack or just being empty
        available_positions = [position for position in new_position if self.can_enter_cell(position)] 

        return available_positions

# ⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⣿⣧⣤⡴⠞⠛⠛⠛⠛⠛⠛⠛⠛⠳⢦⣤⣴⣿⣿⣿⣦⡄⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⡿⢋⡽⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢯⡙⢻⣿⣿⡄⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⣷⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣾⣿⣿⠃⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠘⢿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⠃⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⢠⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⡆⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⣼⠃⠀⠀⠀⠀⠀⠀⣠⣤⣄⠀⠀⠀⢀⣤⣄⡀⠀⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⢀⣴⣾⣿⣿⣿⠀⠀⠀⢾⣾⣿⣿⣦⣄⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠸⣧⠀⠀⠀⠘⠿⣿⣿⣿⠋⠰⣶⡶⠈⢻⣿⣿⡿⠟⠀⠀⠀⠀⣸⠇⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⣘⣷⢤⣀⣀⠠⣤⠠⠘⠢⠠⡜⣄⣠⣚⠽⠄⠤⠼⠁⣀⡴⠞⠛⢦⡀⠀⠀⠀⠀⠀⠀
# ⠀⠀⢀⡴⠊⣉⡉⠵⣟⠛⡏⢁⣀⡠⣤⠕⠶⠂⡉⢉⣁⣀⣀⣠⠤⠴⠖⠚⠉⠉⠀⠀⠀⠀⠙⣦⡀⠀⠀⠀⠀
# ⠀⡠⠞⠊⢹⣀⣀⠀⡼⠒⠉⠁⡇⢆⠆⠀⠀⢀⣠⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂⠀⠀⠀⠀⠈⢷⡄⠀⠀⠀
# ⠈⠦⢴⡶⣈⣁⠠⠞⠁⠀⠀⠠⠗⠁⠀⠀⠸⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠀⠀⠀⠀⠀⠀⢿⡄⠀⠀
# ⠀⠀⠘⣧⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠈⣷⠀⠀
# ⠀⠀⠀⠈⠻⠶⢤⣤⠤⢤⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡼⠀⠀⠀⠀⠀⠀⠀⣿⠀⠀
# ⠀⠀⠀⠀⠀⠀⢰⡏⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡼⠁⠀⠀⠀⠀⠀⠀⢀⣿⡄⠀
# ⠀⠀⠀⠀⠀⢀⡿⠀⠀⠸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡾⠁⠀⠀⠀⠀⠀⠀⢀⡼⠃⢿⡀
# ⠀⠀⠀⣀⡤⠼⢇⡀⠀⠀⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢧⡀⠀⠀⠀⣀⣤⠴⠋⠀⠀⠈⣷
# ⠀⠀⡼⡥⢔⢑⢎⢩⢢⡀⠘⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣩⡛⢛⠛⠢⡀⠀⠀⠀⠀⠀⣿
# ⠀⠀⡇⡪⢱⠉⢐⠀⠀⢡⠀⠐⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠎⠀⢘⢃⢠⠒⡴⡀⠀⠀⠀⠀⣿
# ⠀⠀⣧⠐⠂⠀⠀⠀⢠⠘⡄⠀⠘⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡜⠀⠀⠃⠀⠐⠒⠀⡇⠀⠀⠀⣼⠃
# ⠀⠀⠘⡄⢀⠀⠀⠀⠸⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠈⠀⠀⠀⠈⠈⢰⠁⠀⢀⣴⠏⠀
# ⠀⠀⠀⠙⢦⡁⠂⠐⠁⡸⠀⠀⠀⠀⣀⣀⣀⣀⣀⣠⣀⣀⣀⣀⠀⠀⠀⡇⠠⡀⠀⢀⠄⢠⢃⣠⡶⠋⠁⠀⠀
# ⠀⠀⠀⠀⠀⠉⠓⠒⠊⠉⠛⠛⠛⠋⠉⠉⠉⠉⠁⠀⠀⠈⠉⠉⠙⠛⠳⢾⣦⡀⣁⣠⡴⠟⠋⠁⠀⠀⠀⠀⠀

