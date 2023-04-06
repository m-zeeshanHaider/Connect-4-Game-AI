import pygame
import sys
import numpy as np
import math
import random

Red = (220,20,60)
Yellow = (240,255,20)
Blue = (30,144,255)
Black = (0,0,0)
rowCount = 6
columnCount = 7
squareSize = 120
Width = columnCount * squareSize
Height = (rowCount+1) * squareSize
Radius = int(squareSize/2 - 5)
Size = (Width, Height)
Screen = pygame.display.set_mode(Size)

playerTurn = 0
AiTurn = 1
playerPiece = 1
aiPiece = 2
emptyPiece = 0
windowLength = 4

def create_board():
	board = np.zeros((rowCount,columnCount))
	return board

def draw_board(board):
	for c in range(columnCount):
		for r in range(rowCount):
			pygame.draw.rect(Screen, Blue, (c*squareSize, r*squareSize+squareSize, squareSize, squareSize))
			pygame.draw.circle(Screen, Black, (int(c*squareSize+squareSize/2), int(r*squareSize+squareSize+squareSize/2)), Radius)
	
	for c in range(columnCount):
		for r in range(rowCount):		
			if board[r][c] == playerPiece:
				pygame.draw.circle(Screen, Red, (int(c*squareSize+squareSize/2), Height-int(r*squareSize+squareSize/2)), Radius)
			elif board[r][c] == aiPiece: 
				pygame.draw.circle(Screen, Yellow, (int(c*squareSize+squareSize/2), Height-int(r*squareSize+squareSize/2)), Radius)
	pygame.display.update()

def print_board(board):
	print(np.flip(board, 0))

def is_valid_slot(board, col):
	return board[rowCount-1][col] == 0

def drop_piece(board, row, col, piece):
	board[row][col] = piece

def get_next_open_row(board, col):
	for r in range(rowCount):
		if board[r][col] == 0:
			return r

def winning_move(board, piece):

	# Check horizontal locations for win
	for c in range(columnCount-3):
		for r in range(rowCount):
			if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
				return True

	# Check vertical locations for win
	for c in range(columnCount):
		for r in range(rowCount-3):
			if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
				return True

	# Check positively sloped diaganols for win
	for c in range(columnCount-3):
		for r in range(rowCount-3):
			if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
				return True

	# Check negatively sloped diaganols for win
	for c in range(columnCount-3):
		for r in range(3, rowCount):
			if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
				return True

def score_heuristic(board, piece):

	score = 0

	# Score center column
	center_column_array = [int(i) for i in list(board[:, columnCount//2])]
	center_pieces_count = center_column_array.count(piece)
	score += center_pieces_count * 3

	# Score Horizontally 
	for r in range(rowCount):
		row_array = [int(i) for i in list(board[r,:])]
		for c in range(columnCount-3):
			window = row_array[c:c+windowLength]
			if window.count(piece) == 3 and window.count(emptyPiece) == 1:
				score += 5
			elif window.count(piece) == 2 and window.count(emptyPiece) == 2:
				score += 2

	# Score Vertically
	for c in range(columnCount):
		col_array = [int(i) for i in list(board[:,c])]
		for r in range(rowCount-3):
			window = col_array[r:r+windowLength]
			if window.count(piece) == 3 and window.count(emptyPiece) == 1:
				score += 5
			elif window.count(piece) == 2 and window.count(emptyPiece) == 2:
				score += 2

	# Score positive sloped diagonal
	for r in range(rowCount-3):
		for c in range(columnCount-3):
			window = [board[r+i][c+i] for i in range(windowLength)]
			if window.count(piece) == 3 and window.count(emptyPiece) == 1:
				score += 5
			elif window.count(piece) == 2 and window.count(emptyPiece) == 2:
				score += 2

	# Score negative sloped diagonal
	for r in range(rowCount-3):
		for c in range(columnCount-3):
			window = [board[r+3-i][c+i] for i in range(windowLength)]
			if window.count(piece) == 3 and window.count(emptyPiece) == 1:
				score += 5
			elif window.count(piece) == 2 and window.count(emptyPiece) == 2:
				score += 2

	return score

# Get all valid slots in which piece can be droped
def get_valid_slots(board):
	valid_slots = []
	for col in range(columnCount):
		if is_valid_slot(board, col):
			valid_slots.append(col)
	return valid_slots

# Checks wether a terminal node is reached or not i.e
# 1) Player won the game 
# 2) AI won the game 
# 3) No more valid slots to drop the piece 
def is_terminal_node(board):
	return winning_move(board, playerPiece) or winning_move(board, aiPiece) or len(get_valid_slots(board)) == 0

# Minimax algorithm with Alpha-Beta pruning
def minimaxAlgo(board, depth, alpha, beta, maximizingPlayer):

	valid_slots = get_valid_slots(board)
	terminal_node = is_terminal_node(board)

	if depth == 0 or terminal_node:

		if terminal_node:

			# If AI wins i.e AI gets 4 in a row
			if winning_move(board, aiPiece):
				return (None, 100000000000000)

			# If Player wins i.e Player gets 4 a row	
			elif winning_move(board, playerPiece):
				return (None, -10000000000000)

			else: # Game is over, no more valid moves
				return (None, 0)

		else: # Depth is zero
			return (None, score_heuristic(board, aiPiece))

	if maximizingPlayer:
		value = -math.inf
		column = random.choice(valid_slots)
		
		for col in valid_slots:

			row = get_next_open_row(board, col)
			board_copy = board.copy()
			drop_piece(board_copy, row, col, aiPiece)
			new_score = minimaxAlgo(board_copy, depth-1, alpha, beta, False)[1]

			if new_score > value:
				value = new_score
				column = col
			alpha = max(alpha, value)

			if alpha >= beta:
				break

		return column, value

	else: # Minimizing player
		value = math.inf
		column = random.choice(valid_slots)

		for col in valid_slots:
			row = get_next_open_row(board, col)
			board_copy = board.copy()
			drop_piece(board_copy, row, col, playerPiece)
			new_score = minimaxAlgo(board_copy, depth-1, alpha, beta, True)[1]

			if new_score < value:
				value = new_score
				column = col
			beta = min(beta, value)

			if alpha >= beta:
				break

		return column, value

def run_game():

	board = create_board()
	print_board(board)
	game_over = False
	pygame.init()
	draw_board(board)
	pygame.display.update()
	myfont = pygame.font.SysFont("monospace", 75)

	turn = random.randint(playerTurn, AiTurn)

	while not game_over:

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()

			if event.type == pygame.MOUSEMOTION:
				pygame.draw.rect(Screen, Black, (0,0, Width, squareSize))
				posx = event.pos[0]
				if turn == playerTurn:
					pygame.draw.circle(Screen, Red, (posx, int(squareSize/2)), Radius)

			pygame.display.update()

			if event.type == pygame.MOUSEBUTTONDOWN:
				pygame.draw.rect(Screen, Black, (0,0, Width, squareSize))

				# Ask for Player Input
				if turn == playerTurn:
					posx = event.pos[0]
					column = int(math.floor(posx/squareSize))

					if is_valid_slot(board, column):
						row = get_next_open_row(board, column)
						drop_piece(board, row, column, playerPiece)

						if winning_move(board, playerPiece):
							label = myfont.render("Player Wins!", 1, Red)
							Screen.blit(label, (40,10))
							game_over = True

						# Switching to AI turn
						turn = 1

						print_board(board)
						draw_board(board)


		# AI Input
		if turn == AiTurn and not game_over:

			depth = 5
			alpha = -math.inf
			beta = math.inf
			maximizingPlayer = True

			column, minimax_score = minimaxAlgo(board, depth, alpha, beta, maximizingPlayer)

			if is_valid_slot(board, column):
				row = get_next_open_row(board, column)
				drop_piece(board, row, column, aiPiece)

				if winning_move(board, aiPiece):
					label = myfont.render("AI Wins!", 1, Yellow)
					Screen.blit(label, (40,10))
					game_over = True

				# Switching to Player turn
				turn = 0

				print_board(board)
				draw_board(board)

		if game_over:
			pygame.time.wait(3000)
		

run_game()