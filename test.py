import cv2, numpy as np

# img = np.zeros((101, 4096, 4))
img = cv2.imread('files/pics/db_font00_US_win.bmp.png', cv2.IMREAD_UNCHANGED)

with open('positions.txt', 'r') as f:
    for i, line in enumerate(f.readlines()):
        try:
            x, y, w, h, a, b, c = list(map(int, line.strip().split(' ')))
            print(f'{x:04} {y:02}, {w:02} {h:02}, {a} {b} {c}')
            color = (255,0,0,255) if i % 2 else (0, 255, 0, 255)

            cv2.rectangle(img, (x, y), (x + w, y + h), color=color, thickness=1)
        except: pass

test = cv2.imwrite('test.png', img)