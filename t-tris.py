import os
import signal
import time
import random
import msvcrt

HEIGHT = 20
WIDTH = 10

score = {"value": 0}

clear = lambda: os.system('cls' if os.name == 'nt' else 'clear')
status = "piece_spawn"

piecesTypes = ["o", "i", "j", "l", "t", "s", "z"]
EmptyLine = [False, False, False, False, False, False, False, False, False, False]

rotation = {
    "o": [
        [['░', "░"],
         ["░", "░"]]
    ],
    "i": [
        [
            ["░"],
            ["░"],
            ["░"],
            ["░"],
        ],
        [["░", "░", "░", "░"]]
    ],
    "j": [
        [
            ["░", "", ""],
            ["░", "░", "░"]
        ],

        [
            ["░", "░"],
            ["░", ""],
            ["░", ""]
        ],

        [
            ["░", "░", "░"],
            ["", "", "░"]
        ],

        [
            ["", "░"],
            ["", "░"],
            ["░", "░"]
        ]
    ],
    "l": [

        [
            ["", "", "░"],
            ["░", "░", "░"]
        ],

        [
            ["░", ""],
            ["░", ""],
            ["░", "░"]
        ],
        [
            ["░", "░", "░"],
            ["░", "", ""]
        ],
        [
            ["░", "░"],
            ["", "░"],
            ["", "░"]
        ],

    ],
    "t": [
        [
            ["", "░", ""],
            ["░", "░", "░"]
        ],
        [
            ["░", ""],
            ["░", "░"],
            ["░", ""]
        ],
        [
            ["░", "░", "░"],
            ["", "░", ""]
        ],
        [
            ["", "░"],
            ["░", "░"],
            ["", "░"]
        ]
    ],
    "s":
        [
            [
                ["", "░", "░"],
                ["░", "░", ""],
            ],

            [
                ["░", ""],
                ["░", "░"],
                ["", "░"]
            ]

        ]
    ,
    "z":
        [
            [
                ["░", "░", ""],
                ["", "░", "░"],
            ],
            [
                ["", "░"],
                ["░", "░"],
                ["░", ""]
            ]

        ]

}


class objectview(object):
    def __init__(self, d):
        self.__dict__ = d


def getPiece():
    selectedPieceType = random.choice(piecesTypes)
    selectedPiece = rotation[selectedPieceType][0]
    return objectview({"piece": selectedPiece,
                       "type": selectedPieceType,
                       "position": (-len(selectedPiece) + 1, int(WIDTH / 2) - 1),
                       "rotateIndex": 0})


currentPiece = getPiece()


def rotatePiece(piece):
    piece.rotateIndex = piece.rotateIndex + 1
    if piece.rotateIndex > len(rotation[piece.type]) - 1:
        piece.rotateIndex = 0

    piece.piece = rotation[piece.type][piece.rotateIndex]


def undoRotatePiece(piece):
    piece.rotateIndex = piece.rotateIndex - 1
    if piece.rotateIndex < 0:
        piece.rotateIndex = len(rotation[piece.type]) - 1

    piece.piece = rotation[piece.type][piece.rotateIndex]


def initEmptyGrid():
    """Initialize a new empty grid"""
    grid = []
    for i in range(HEIGHT):
        grid.append([])
        for j in range(WIDTH):
            grid[i].append(False)
    return grid


def printGrid(grid):
    for i in range(HEIGHT):
        print("▓|", end="")
        for j in range(WIDTH):
            currentCell = grid[i][j]
            if currentCell:
                print("░░", end="")
            elif isPiecePartAtGridPos(i, j, currentPiece):
                print("▓▓", end="")
            else:
                print("  ", end="")
        print("|▓")

    for j in range(WIDTH + 2):
        print("▓▓", end="")

    print()
    print("T-TRIS !")
    print("(q TO QUIT)")
    print("(r TO RESTART)")
    printScore()
    print()

    time.sleep(0.2)
    clear()


def spawnPiece():
    return getPiece()


def isPiecePartAtGridPos(y, x, piece):
    yy = y - piece.position[0]
    xx = x - piece.position[1]

    if yy < 0 or xx < 0:
        return False
    if yy >= len(piece.piece) or xx >= len(piece.piece[yy]):
        return False

    return piece.piece[yy][xx] != ""


def pieceCollides(grid, currentPiece):
    for yy in range(0, len(currentPiece.piece)):
        for xx in range(0, len(currentPiece.piece[yy])):
            if currentPiece.piece[yy][xx] == "": continue
            if currentPiece.position[0] + yy < 0 or currentPiece.position[1] + xx < 0: continue
            if currentPiece.position[0] + yy > HEIGHT - 1 or currentPiece.position[1] + xx > WIDTH - 1:
                return True
            if grid[currentPiece.position[0] + yy][currentPiece.position[1] + xx]:
                return True
    return False


def pieceFall(grid, piece):
    piece.position = (piece.position[0] + 1, piece.position[1])

    def lock():
        # lock piece in grid
        for i in range(HEIGHT):
            for j in range(WIDTH):
                if isPiecePartAtGridPos(i, j, piece):
                    grid[i][j] = True

    if pieceCollides(grid, piece):
        piece.position = (piece.position[0] - 1, piece.position[1])
        lock()
        return "piece_spawn"

    elif piece.position[0] > HEIGHT - len(piece.piece):
        lock()
        return "piece_spawn"
    # draw piece

    return "piece_falling"


def movePieceLeft(grid, piece):
    if piece.position[1] > 0:
        piece.position = (piece.position[0], piece.position[1] - 1)
        if pieceCollides(grid, piece):
            piece.position = (piece.position[0], piece.position[1] + 1)


def movePieceRight(grid, piece):
    if piece.position[1] < WIDTH - len(piece.piece[0]) and not pieceCollides(grid, piece):
        piece.position = (piece.position[0], piece.position[1] + 1)
        if pieceCollides(grid, piece):
            piece.position = (piece.position[0], piece.position[1] - 1)


def checklineFull(grid):
    toDelete = []

    for i in range(HEIGHT):
        for j in range(WIDTH):
            currentCell = grid[i][j]
            if currentCell == False:
                break
            if j == WIDTH - 1:
                toDelete.append(i)

    if len(toDelete) > 0:
        printGrid(grid)

    l = len(toDelete)
    if l == 1:
        score["value"] = score["value"] + 40
    elif l == 2:
        score["value"] = score["value"] + 100
    elif l == 3:
        score["value"] = score["value"] + 300
    elif l == 4:
        score["value"] = score["value"] + 1200

    for line in toDelete:
        grid[line] = []
        for j in range(WIDTH):
            grid[line].append(False)
        printGrid(grid)
        grid.pop(line)
        grid.insert(0, [])
        for j in range(WIDTH):
            grid[0].append(False)
        time.sleep(0.05)
        printGrid(grid)


def movePieceDownInstantly(grid, currentPiece):
    while pieceFall(grid, currentPiece) == "piece_falling":
        pass
    return "piece_spawn"


def undoRotate(piece):
    undoRotatePiece(piece)


def rotate(piece):
    rotatePiece(piece)
    if pieceCollides(grid, piece):
        undoRotate(piece)


def printScore():
    print("Score : " + str(score["value"]))


def checkGameOver(grid, currentPiece):
    return pieceCollides(grid, currentPiece)


if __name__ == "__main__":

    os.system('mode con: cols=25 lines=22')

    grid = initEmptyGrid()
    clear()
    while True:
        if status == "piece_spawn":
            currentPiece = spawnPiece()
            status = "piece_falling"
            printGrid(grid)

            if checkGameOver(grid, currentPiece):
                printScore()
                input("Press Enter to continue...")
                grid = initEmptyGrid()
                score["value"] = 0
                status = "piece_spawn"
                continue

        elif status == "piece_falling":

            if msvcrt.kbhit():
                msvcrt.getch()
                x = msvcrt.getch()

                if x == b'K':
                    movePieceLeft(grid, currentPiece)
                elif x == b'M':
                    movePieceRight(grid, currentPiece)
                elif x == b'P':
                    status = movePieceDownInstantly(grid, currentPiece)
                    checklineFull(grid)
                elif x == b'H':
                    rotate(currentPiece)
                elif x == b'q':
                    print("quit")
                    printScore()
                    break
                elif x == b'r':
                    printScore()
                    input("Press Enter to continue...")
                    grid = initEmptyGrid()
                    score["value"] = 0
                    status = "piece_spawn"
                    continue

            else:
                status = pieceFall(grid, currentPiece)
                checklineFull(grid)

            printGrid(grid)
    os.kill(os.getppid(), signal.SIGTERM)
