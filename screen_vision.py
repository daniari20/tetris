import mss
import numpy as np
import cv2
import time
import pyautogui

# ==============================
# CONFIGURACIÓN
# ==============================

GAME_REGION = {
    "top": 250,
    "left": 600,
    "width": 800,
    "height": 700
}

ROWS = 20
COLS = 10

# Colores en BGR (OpenCV)
PIECE_COLORS = {
    "Cuadradito":       (51,155,181),
    "Ele moradita":     (165,63,80),
    "Ele naranjita":    (41,113,227),
    "Palito":           (132,179,50),
    "Pistolita":        (191,57,205),
    "Rojita":           (58,51,179),
    "Verde clarita":    (53,182,134)
}

COLOR_TOLERANCE = 100


def capture_game():
    with mss.mss() as sct:
        screenshot = sct.grab(GAME_REGION)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

def split_regions(img):
    h, w, _ = img.shape
    
    board = img[:, int(w*0.25):int(w*0.65)]
    next_region = img[:, int(w*0.65):w]

    return board, next_region

template = cv2.imread("hold_image.png", 0)
template2 = cv2.imread("next_image.png", 0)
w, h = template.shape[::-1]

def detect_game_region(imagen):

    with mss.mss() as sct:

        monitor = sct.monitors[1]


        screenshot = sct.grab(monitor)
        img = np.array(screenshot)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)

        threshold = 0.8
        locations = np.where(result >= threshold)

        #for pt in zip(*locations[::-1]):

            # cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0,255,0), 2)

            #print("Tablero encontrado en:", pt)

        #cv2.imshow("Detection", img)

        #time.sleep(0.2)

        # if cv2.waitKey(1) == 27:
        #     break

    #cv2.destroyAllWindows()

class Vision:

    def __init__(self):
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]
        self.board_bbox = None

    # -------------------------
    # SCREEN CAPTURE
    # -------------------------

    def capture_screen(self):
        screenshot = np.array(self.sct.grab(self.monitor))
        frame = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
        return frame

    # -------------------------
    # LOCATE BOARD
    # -------------------------

    def locate_board(self, frame):

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        edges = cv2.Canny(gray, 50, 150)

        contours, _ = cv2.findContours(
            edges,
            cv2.RETR_TREE,
            cv2.CHAIN_APPROX_SIMPLE
        )

        best = None
        best_area = 0

        for c in contours:

            x, y, w, h = cv2.boundingRect(c)

            ratio = h / float(w)

            area = w * h

            # tablero Tetris ~ 2:1
            if 1.8 < ratio < 2.4 and area > best_area:

                if w > 200:
                    best = (x, y, w, h)
                    best_area = area

        self.board_bbox = best
        print("best", best)
        return best

    # -------------------------
    # READ GRID
    # -------------------------

    def read_board(self, frame):

        if self.board_bbox is None:
            return None

        x, y, w, h = self.board_bbox

        cell_w = w / 10
        cell_h = h / 20

        board = [[0 for _ in range(10)] for _ in range(20)]

        for row in range(20):
            for col in range(10):

                cx = int(x + col * cell_w + cell_w / 2)
                cy = int(y + row * cell_h + cell_h / 2)

                pixel = frame[cy, cx]

                if np.mean(pixel) < 40:
                    board[row][col] = 0
                else:
                    board[row][col] = 1

        return board

    # -------------------------
    # READ CURRENT PIECE (placeholder)
    # -------------------------

    def detect_current_piece(self, frame):
        """
        Placeholder.
        Requiere calibración de color.
        """
        return None

    # -------------------------
    # READ NEXT QUEUE (placeholder)
    # -------------------------

    def detect_next_queue(self, frame, best):


        if best:
            next_region = frame[
                int(best[1] + 0.02*best[3]): int(best[1] + 0.8*best[3]),
                int(best[0] + best[2] + 0.03*best[2]): int(best[0] + best[2] + 0.6*best[2])
            ]
            cv2.imshow("next", next_region)
            return next_region


    # -------------------------
    # READ HOLD 
    # -------------------------

    def detect_hold_region(self, frame, best):


        if best:

            hold_region = frame[
            int(best[1] + 0.02*best[3]): int(best[1] + 0.25*best[3]),
            int(best[0] - 0.5*best[2]): int(best[0] - 0.05*best[2])
            ]
            cv2.imshow("hold", hold_region)
            return hold_region



    # -------------------------
    # GET GAME STATE
    # -------------------------

    def get_state(self):

        frame = self.capture_screen()

        if self.board_bbox is None:
            self.locate_board(frame)

        board = self.read_board(frame)

        current_piece = self.detect_current_piece(frame)

        next_queue = self.detect_next_queue(frame)

        return {
            "board": board,
            "current_piece": current_piece,
            "next_queue": next_queue
        }

    # -------------------------
    # DEBUG VISUALIZATION
    # -------------------------

    def debug_show(self, frame):

        if self.board_bbox:

            x, y, w, h = self.board_bbox

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

        cv2.imshow("vision", frame)


        cv2.waitKey(1)



def extract_grid(board_img):
    h, w, _ = board_img.shape
    cell_h = h // ROWS
    cell_w = w // COLS
    
    grid = []
    
    for r in range(ROWS):
        row = []
        for c in range(COLS):
            y1 = r * cell_h
            y2 = (r+1) * cell_h
            x1 = c * cell_w
            x2 = (c+1) * cell_w
            
            cell = board_img[y1:y2, x1:x2]
            row.append(cell)
        grid.append(row)

    return grid


def get_dominant_color(cell):
    avg_color = np.mean(cell.reshape(-1, 3), axis=0)
    return tuple(avg_color.astype(int))


def classify_cell(cell):
    avg = get_dominant_color(cell)
    
    for name, color in PIECE_COLORS.items():
        if all(abs(avg[i] - color[i]) < COLOR_TOLERANCE for i in range(3)):
            return name
            
    return None


def build_board_state(board_img):
    grid = extract_grid(board_img)
    state = []
    
    for row in grid:
        state_row = []
        for cell in row:
            piece = classify_cell(cell)
            state_row.append(piece)
        state.append(state_row)
    
    return np.array(state)


# ==============================
# COMPONENTES CONEXAS
# ==============================

def find_connected_components(state):
    visited = set()
    components = []
    
    for r in range(ROWS):
        for c in range(COLS):
            if state[r][c] is not None and (r,c) not in visited:
                stack = [(r,c)]
                comp = []
                
                while stack:
                    rr, cc = stack.pop()
                    if (rr,cc) in visited:
                        continue
                    visited.add((rr,cc))
                    comp.append((rr,cc))
                    
                    for dr,dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                        nr, nc = rr+dr, cc+dc
                        if 0<=nr<ROWS and 0<=nc<COLS:
                            if state[nr][nc] is not None:
                                stack.append((nr,nc))
                                
                components.append(comp)
                
    return components


def separate_falling_and_stack(state):
    components = find_connected_components(state)
    
    if not components:
        return None, []
    
    components.sort(key=lambda comp: np.mean([r for r,c in comp]))
    
    falling_piece = components[0]
    stack_pieces = components[1:]
    
    return falling_piece, stack_pieces


# ==============================
# NEXT PIECES
# ==============================

def detect_next(next_img):
    detected = []
    
    for name, color in PIECE_COLORS.items():
        lower = np.array([max(0,color[0]-30),
                          max(0,color[1]-30),
                          max(0,color[2]-30)])
        upper = np.array([min(255,color[0]+30),
                          min(255,color[1]+30),
                          min(255,color[2]+30)])
                          
        mask = cv2.inRange(next_img, lower, upper)
        
        if cv2.countNonZero(mask) > 800:
            detected.append(name)
            
    return detected


# ==============================
# LOOP PRINCIPAL
# ==============================

vision = Vision()

while True:
    detect_game_region(template)
    detect_game_region(template2)
    frame = vision.capture_screen()
    best=vision.locate_board(frame)
    next_image=vision.read_board(frame)
    next_region = vision.detect_next_queue(frame, best)
    hold_region= vision.detect_hold_region(frame,best)
    vision.debug_show(frame)
    img = capture_game()
    board_img, next_img = split_regions(img)
    # x, y = pyautogui.position()
    # print(f"Mouse position: {x}, {y}")  



    board = vision.read_board(frame)
    
    state = build_board_state(board_img)
    
    falling_piece, stack_pieces = separate_falling_and_stack(state)
    
    next_pieces = detect_next(next_img)
    


    print("Board", board)
    print("Falling:", falling_piece)
    print("Stack groups:", len(stack_pieces))
    print("Next:", next_pieces)
    print("-"*40)
    
    # cv2.imshow("Board", board_img)
    # cv2.imshow("Next", next_img)
    
    if cv2.waitKey(1) == 27:
        break
    
    #time.sleep(0.2)

cv2.destroyAllWindows()