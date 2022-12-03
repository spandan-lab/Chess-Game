# main driver file
# handle the inputs
# display the current state

import pygame as p
import ChessEngine, SmartMoveFinder
import random

WIDTH = HEIGHT = 512
DIMENSION = 8  # 8X8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # for animations
IMAGES = {}

col = random.randint(0,7)
ro = random.randint(2,5)
wall = (5,5)

# Initialize a global dictionary of images
# called exact once in main

def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(piece + '.png'), (SQ_SIZE, SQ_SIZE))


# Main Driver
# Handle User Input
# Display current state

def main():
    print("Select the control strategy for players. \n 1. Human \n 2. Baseline AI (Randome AI) \n 3. Tree-based AI \n")
    val1 = input("Enter the preference for the 1st player: ")
    val2 = input("Enter the preference for the 2nd player: ")
    
    playerOne = val1
    playerTwo = val2
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color('white'))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False

    loadImages()  # only once
    sqSelected = ()  # keep track of the last click of the user (row,col)
    playerClicks = []  # keep track of player clicks

    gameOver = False
    running = True

    

    while running:
        humanTurn = (gs.whiteToMove and (playerOne == "1") ) or (not gs.whiteToMove and (playerTwo == "1"))
        randomTurn = (gs.whiteToMove and (playerOne == "2") ) or (not gs.whiteToMove and (playerTwo == "2"))
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # add drag piece functionality
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()  # (x,y) coordinates for the mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col):
                        sqSelected = ()  # undo select
                        playerClicks = []  # clear player clicks
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2:  # 2 clicks recorded, make the move
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        if move in validMoves:
                            gs.makeMove(move)
                            moveMade = True
                            sqSelected = ()
                            playerClicks = []
                        else:
                            playerClicks = [sqSelected]
            # key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when 'z' is pressed
                    gs.undoMove()
                    moveMade = True
                    gameOver = False
                if e.key == p.K_r:  # reset the game
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    gameOver = False


        #AI Move maker
        if not gameOver and not humanTurn and not randomTurn:
            AImove = SmartMoveFinder.findBestMove(gs, validMoves)
            if AImove is None:
                AImove = SmartMoveFinder.findRandomMove(validMoves)
            print(AImove.getChessNotation())
            gs.makeMove(AImove)
            moveMade = True

        #Radom move maker
        if not gameOver and not humanTurn:

            #ai_move = return_queue.get()
            AImove = SmartMoveFinder.findRandomMove(validMoves)
            print(AImove.getChessNotation())
            gs.makeMove(AImove)
            moveMade = True

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs, validMoves, sqSelected, wall)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, "Black Wins")
            else:
                drawText(screen, "White Wins")
        elif gs.staleMate:
            gameOver = True
            drawText(screen, "Stalemate")
        clock.tick(MAX_FPS)
        p.display.flip()

        

# Highlight saquare and moves

def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

            # moves
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


# Responsible for graphics within a current game state

def drawGameState(screen, gs, validMoves, sqSelected, wall):
    drawBoard(screen)  # draw squares
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board, wall)  # draw pieces


def drawBoard(screen):
    colors = [p.Color('white'), p.Color('gray')]
    # top left square is always white
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


# draw pieces from GameState.board
def drawPieces(screen, board, wall):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            # Check if not empty
            if (r,c) == wall:
                p.draw.rect(screen, 'red', p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            if piece != '--' and piece != '00':
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawText(screen, text):
    font = p.font.SysFont("Helvitica", 32, True, False)
    textObject = font.render(text, 0, p.Color('Black'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2,
                                                    HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)


if __name__ == '__main__':
    main()
