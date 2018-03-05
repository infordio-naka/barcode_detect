import os
import random
import barcode
from   barcode.writer import ImageWriter
from   barcode.errors import BarcodeError
import numpy          as     np
from   PIL            import Image, ImageMath, ImageFilter, ImageOps

from   digits_dict import digits_dict
from   text_dict   import text_dict

SIZE_OF_POSITIVE_IMAGE = (150, 150)
SIZE_OF_NEGATIVE_IMAGE = (150, 150)
POSITIVE_COUNT         = 1
NEGATIVE_COUNT         = 10
BARCODE_IMAGE_W        = 90
BARCODE_IMAGE_H        = 90

def get_digits(bc, barcode_class):
    digits = bc.digits
    if not digits:
        digits = digits_dict[barcode_class]()
    return digits

def random_barcode_class():
    return random.choice(barcode.PROVIDED_BARCODES)

def random_text(digits, barcode_class):
    text = text_dict[barcode_class](digits)
    return text

def gen_barcode():
    barcode_class = random_barcode_class()
    bc = barcode.get_barcode_class(barcode_class)
    digits = get_digits(bc, barcode_class)
    while True:
        text = random_text(digits, barcode_class)
        print(barcode_class)
        print(text)
        try:
            bc = bc(text, writer=ImageWriter())
        except BarcodeError:
            continue
        else:
            break
    return bc, barcode_class

def resize_image(filename):
    img = Image.open(filename)
    img.thumbnail((BARCODE_IMAGE_W, BARCODE_IMAGE_H))
    return img

def is_collision(box1, box2):
    b1_x1, b1_y1, b1_x2, b1_y2 = box1
    b2_x1, b2_y1, b2_x2, b2_y2 = box2
    
    ret = False
    if (b1_x1<=b2_x2<=b1_x2 and b2_x2-b1_x1>=0) or (b2_x1<=b1_x2<b2_x2 and b1_x2-b2_x1>=0):
        if (b1_y1<=b2_y2<b1_y2 and b2_y2-b1_y1>=0) or (b2_y1<=b1_y2<=b2_y2 and b1_y2-b2_y1>=0):
            ret = True
    return ret

def random_positions(n, image_size):
    # min_w = BARCODE_IMAGE_W
    # min_h = BARCODE_IMAGE_H
    # max_w = image_size[0]-BARCODE_IMAGE_W
    # max_h = image_size[1]-BARCODE_IMAGE_H
    min_w = 0
    min_h = 0
    max_w = abs(image_size[0]-BARCODE_IMAGE_W)
    max_h = abs(image_size[1]-BARCODE_IMAGE_H)
    boxes = []
    positions = []
    for i in range(n):
        c = 500
        while c>0:
            pos_x = random.randint(min_w, max_w)
            pos_y = random.randint(min_h, max_h)
            box1 = (pos_x, pos_y, pos_x+BARCODE_IMAGE_W, pos_y+BARCODE_IMAGE_H) # x1, y1 ,x2, y2
            if not any([is_collision(box1, box2) for box2 in boxes]):
                boxes.append(box1)
                positions.append([pos_x, pos_y])
                break
            c -= 1
    return positions

def paste_images(filenames, image_size=(1936, 2730)):
    pasted_image = Image.new("RGB", image_size, (255, 255, 255))
    positions = random_positions(len(filenames), image_size)
    for filename, pos in zip(filenames, positions):
        img = Image.open(filename)
        pasted_image.paste(img, pos)
        pos[2:] = list(img.size)
    return pasted_image, positions

def break_barcode(filename):
    img = Image.open(filename)
    if random.random()<0.8:
        img = img.filter(ImageFilter.GaussianBlur(10))
    img = img.resize([x // 30 for x in img.size]).resize(img.size)
    if random.random()<0.5:
        img = img.quantize(4)
    if random.random()<0.5:
        try:
            img = ImageOps.invert(img)
        except NotImplementedError:
            pass
    if random.random()<0.5:
        try:
            img = ImageOps.posterize(img, 2)
        except NotImplementedError:
            pass
    if random.random()<0.5:
        try:
            img = img.filter(ImageFilter.CONTOUR)
        except ValueError:
            pass
    return img

def random_crop_position(img, crop_size):
    img_w,  img_h  = img.size
    crop_w, crop_h = crop_size
    x1 = random.randint(0, img_w-crop_w)
    y1 = random.randint(crop_h, img_h-crop_h)
    x2 = x1+crop_w
    y2 = y1+crop_h
    return (x1, y1, x2, y2)

# positive
filenames = []
save_path = "images/positive/"
if not os.path.isdir(save_path):
    os.makedirs(save_path)
save_path = save_path+"positive{0}"
fp        = open("positive.dat", 'w')
for i in range(7001):
    print(i)
    bc, barcode_class = gen_barcode()
    filenames.append(bc.save(save_path.format(i), {"write_text":False}))
    img = resize_image(filenames[-1])
    img.save(save_path.format(i)+".png")
    if i!=0 and i%POSITIVE_COUNT==0:
        pasted_image, positions = paste_images(filenames, SIZE_OF_POSITIVE_IMAGE) # positions=(x, y, w, h)
        pasted_image_name = "images/positive/positive_pasted_image{0}.png".format(int(i/POSITIVE_COUNT)-1)
        pasted_image.save(pasted_image_name)
        text = "{0} {1} ".format(pasted_image_name, len(positions))
        text += " ".join([" ".join([str(pos) for pos in position]) for position in positions])+"\n"
        fp.write(text)
        filenames = []
fp.close()

# negative
save_path = "images/negative/"
if not os.path.isdir(save_path):
    os.makedirs(save_path)
save_path = save_path+"negative{0}.png"
dir_path = "/home/naka/workspace/images/"
fp = open("negative.dat", 'w')
filenames = os.listdir(dir_path)
for i in range(5000):
    print(i)
    filename = random.choice(filenames)
    path = os.path.join(dir_path, filename)
    img  = Image.open(path)
    img  = img.convert("L")
    crop_pos = random_crop_position(img, SIZE_OF_NEGATIVE_IMAGE)
    crop_img = img.crop(crop_pos)
    crop_img.save(save_path.format(i))
    fp.write(save_path.format(i)+"\n")
    
# negative
# filenames = []
# fp        = open("negative.dat", 'w')
# for i in range(1001):
#     print(i)
#     bc, barcode_class = gen_barcode()
#     filenames.append(bc.save("images/negative/negative{0}".format(i), {"write_text":False}))
#     img = break_barcode(filenames[-1])
#     img.save("images/negative/negative{0}.png".format(i))
#     if i!=0 and i%COUNT==0:
#         pasted_image, positions = paste_images(filenames, SIZE_OF_IMAGE) # positions=(x, y, w, h)
#         pasted_image_name = "images/negative/negative_pasted_image{0}.png".format(int(i/COUNT)-1)
#         pasted_image.save(pasted_image_name)
#         text = "{0}\n".format(pasted_image_name)
#         fp.write(text)
#         filenames = []
fp.close()
