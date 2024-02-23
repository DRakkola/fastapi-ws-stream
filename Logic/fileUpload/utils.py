import os
import time
import numpy as np
import cv2
import pytesseract
import re
import datetime as dt
import logging
import easyocr

# Configure logging
logging.basicConfig( format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)

tesseract = r'E:\Tesseract-ocr\\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd=tesseract
# text_reader = easyocr.Reader(['en'],model_storage_directory='/Model')
def clean(img):
    try:
        black_pixels = np.where(
            (img[:, :, 0] == 0) & (img[:, :, 1] == 0) & (img[:, :, 2] == 0)
        )
        img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
        img[black_pixels] = [255, 255, 255]
        not_white = np.where(
            (img[:, :, 0] != 255) & (img[:, :, 1] != 255) & (img[:, :, 2] != 255)
        )
        img[not_white] = [0, 0, 0]
        ret, bw_img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
        return bw_img
    except Exception as e:
        logging.error(f"Error in clean function: {e}")

def im_green(path):
    try:
        print(path)
        logging.info("Processing green image...")
        img = cv2.imread(path)

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)

        mask = cv2.inRange(hsv, (50, 130, 150), (70, 255, 255))
        dst1 = cv2.bitwise_and(img, img, mask=mask)
        bw_img = clean(dst1)
        return bw_img
    except Exception as e:
        logging.error(f"Error in im_green function: {e}")

def im_blue(path):
    try:
        logging.info("Processing blue image...")
        img = cv2.imread(path)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)

        mask = cv2.inRange(hsv, (82, 130, 150), (95, 255, 255))
        dst1 = cv2.bitwise_and(img, img, mask=mask)
        bw_img = clean(dst1)
        return bw_img
    except Exception as e:
        logging.error(f"Error in im_blue function: {e}")

def dms_to_dd(d, m, s):
    try:
        if d[0] == "-":
            dd = float(d) - float(m) / 60 - float(s) / 3600
        else:
            dd = float(d) + float(m) / 60 + float(s) / 3600
        return dd
    except Exception as e:
        logging.error(f"Error in dms_to_dd function: {e}")

def parse_data(img):
    try:
        custom_config = r" --oem 3 --psm 6"
        text = pytesseract.image_to_string(img, config=custom_config)
        # text = ''
        # results = text_reader.readtext(img,width_ths=0.7 )
        # for (bbox, item, prob) in results:
        #     text = text +' '+item
        logging.info("Extracting text...")
        
        text = re.sub(" : ", ":", text)
        x1 = text.split()
        test = x1
        x1 = "".join(x1)
        
        x = re.findall(r"([0-9]+:[0-9]+:[0-9]+N*E*)", x1)
        x = " ".join(x)
        logging.info(text)
        logging.info(x1)
        logging.info(x)
        N = re.findall(r"[0-9]*[0-9]:[0-9]*[0-9]:[0-9]*N{1}", x)
        E = re.findall(r"[0-9]*[0-9]:[0-9]*[0-9]:[0-9]*E{1}", x)
        if len(E) != 2:
            E.append(test[len(test) - 1])
        TGT = []
        if len(N) == 2 & len(E) == 2:
            TGT.extend([N[1], E[1]])
        TGT_cov = []
        for item in TGT:
            if re.search("N", item):
                x = re.sub("O", "0", item)
                x = re.sub("N", "", x).split(":")
            else:
                x = re.sub("O", "0", item)
                x = re.sub("E", "", x).split(":")
            TGT_cov.append(dms_to_dd(x[0], x[1], x[2]))

        ACFT = []
        if len(N) == 2 & len(E) == 2:
            ACFT.extend([N[0], E[0]])
        ACFT_cov = []
        for item in ACFT:
            if re.search("N", item):
                x = re.sub("N", "", item).split(":")
            else:
                x = re.sub("E", "", item).split(":")
            ACFT_cov.append(dms_to_dd(x[0], x[1], x[2]))

        return TGT, TGT_cov, ACFT, ACFT_cov
    except Exception as e:
        logging.error(f"Error in parse_data function: {e}")

def save_valuable(image):
    try:
        try:
            img = im_green(rf"{image}")
            TGT, TGT_cov, ACFT, ACFT_cov = parse_data(img)
        except:
            img = im_blue(rf"{image}")
            TGT, TGT_cov, ACFT, ACFT_cov = parse_data(img)

        logging.info("TGT:\n%s", TGT)
        logging.info("TGT_conv %s", TGT_cov)
        logging.info("ACFT:\n%s", ACFT)
        logging.info("ACFT_conv %s", ACFT_cov)

        if (
            len(TGT) == 2
            and len(ACFT) == 2
            and 29 <= TGT_cov[0] <= 37  # lat
            and 7 <= TGT_cov[1] <= 11  # lon
            and 29 <= ACFT_cov[0] <= 37
            and 7 <= ACFT_cov[1] <= 11
        ):

            datetm = dt.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
            snap = "".join(datetm)
            x = re.sub(":", "-", snap)
            names = f"{ACFT_cov[0]}_{ACFT_cov[1]}@{TGT_cov[0]}_{TGT_cov[1]}@{x}.png"
            return ACFT_cov, TGT_cov, names
    except Exception as e:
        logging.error(f"Error in save_valuable function: {e}")