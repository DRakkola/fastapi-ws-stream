import cv2
import numpy as np
import pytesseract

def clean(img):
    black_pixels = np.where(
        (img[:, :, 0] == 0) &
        (img[:, :, 1] == 0) &
        (img[:, :, 2] == 0)
    )
    img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
    img[black_pixels] = [255, 255, 255]
    not_white = np.where(
        (img[:, :, 0] != 255) &
        (img[:, :, 1] != 255) &
        (img[:, :, 2] != 255)
    )
    img[not_white] = [0, 0, 0]
    ret, bw_img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    return bw_img


def im_green(path):
    print("green")
    img = cv2.imread(path)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    mask = cv2.inRange(hsv, (50, 130, 150), (70, 255, 255))
    dst1 = cv2.bitwise_and(img, img, mask=mask)
    #cv2.imwrite(path.split('/')[2],dst1)
    bw_img = clean(dst1)
    return bw_img


def im_blue(path):
    print("blue")
    img = cv2.imread(path)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    mask = cv2.inRange(hsv, (82, 130, 150), (95, 255, 255))
    dst1 = cv2.bitwise_and(img, img, mask=mask)
    bw_img = clean(dst1)
    return bw_img


def parse_data(img):
    custom_config = r' --oem 3 --psm 6'
    text = pytesseract.image_to_string(img, config=custom_config)
    x1 = text.split()
    test = x1
    x1 = ''.join(x1)
    # print(x1)
    x = re.findall(r"([0-9]+:[0-9]+:[0-9]+N*E*)", x1)
    # print(x)
    x = ' '.join(x)
    N = re.findall(r"[0-9]*[0-9]:[0-9]*[0-9]:[0-9]*N{1}", x)

    E = re.findall(r"[0-9]*[0-9]:[0-9]*[0-9]:[0-9]*E{1}", x)
    # print(type(E))
    if len(E) != 2:
        E.append(test[len(test)-1])
    TGT = []
    if len(N) == 2 & len(E) == 2:
        TGT.extend([N[1], E[1]])
    # print("TGT=",TGT)
    TGT_cov = []
    for item in TGT:
        if re.search("N", item):
            x = re.sub("O", "0", item)
            x = re.sub("N", "", x).split(':')
            # print(x)
        else:
            x = re.sub("O", "0", item)
            x = re.sub("E", "", x).split(':')
            # print(x)
        # print ('!!!!',x)
        TGT_cov.append(dms_to_dd(x[0], x[1], x[2]))

    ACFT = []
    if len(N) == 2 & len(E) == 2:
        ACFT.extend([N[0], E[0]])
    ACFT_cov = []
    for item in ACFT:
        if re.search("N", item):
            x = re.sub("N", "", item).split(':')
        else:
            x = re.sub("E", "", item).split(':')
        ACFT_cov.append(dms_to_dd(x[0], x[1], x[2]))

    return TGT, TGT_cov, ACFT, ACFT_cov
