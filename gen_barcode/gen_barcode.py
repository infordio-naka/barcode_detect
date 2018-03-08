import os
import random
import barcode
from   barcode.writer import ImageWriter
from   barcode.errors import BarcodeError
import numpy          as     np
from   PIL            import Image, ImageMath, ImageFilter, ImageOps

from   digits_dict import digits_dict
from   text_dict   import text_dict
from   saltpepper  import saltpepper

import xml.etree.ElementTree as ET
import xml.dom.minidom       as minidom

NUMBER_OF_POSITIVE     = 3001
NUMBER_OF_NEGATIVE     = 2501
SIZE_OF_POSITIVE_IMAGE = (1936, 2730)
SIZE_OF_NEGATIVE_IMAGE = (1936, 2730)
POSITIVE_COUNT         = 10
NEGATIVE_COUNT         = 10
BARCODE_IMAGE_W        = 300
BARCODE_IMAGE_H        = 150

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

def break_barcode(img):
    if random.random()<0.8:
        img = img.filter(ImageFilter.GaussianBlur(1))
    # img = img.resize([x // 30 for x in img.size]).resize(img.size)
    if random.random()<0.9:
        img = saltpepper(img)
    if random.random()<0.5:
        try:
            img = ImageOps.invert(img)
        except NotImplementedError:
            pass
    if random.random()<0.5:
        try:
            img = ImageOps.posterize(img, 1)
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

def export_xml(path):
    fp  = open(path)
    fp2 = open("annotations/trainval.txt", "w")
    for i, l in enumerate(fp):
        annotation     = ET.Element('annotation')
        filename       = ET.SubElement(annotation, 'filename')
        size           = ET.SubElement(annotation, 'size')
        width          = ET.SubElement(size, 'width')
        width.text     = "1936"
        height         = ET.SubElement(size, 'height')
        height.text    = "2730"
        depth          = ET.SubElement(size, 'depth')
        depth.text     = "3"

        l = l.strip().split(' ')
        filename.text = "barcode_{0}.jpg".format(i)
        num_obj= l[1]
        fp2.write("barcode_{0} {1}\n".format(i, num_obj))
        pos    = l[2:]
        pos = [[int(pos[i]), int(pos[i+1]), int(pos[i])+int(pos[i+2]), int(pos[i+2])+int(pos[i+3])] for i in range(0, len(pos), 4)]
        for p in pos:
            obj            = ET.SubElement(annotation, 'object')
            name           = ET.SubElement(obj, 'name')
            name.text      = "barcode"
            pose           = ET.SubElement(obj, 'pose')
            pose.text      = "Unspecified"
            truncated      = ET.SubElement(obj, 'truncated')
            truncated.text = "0"
            difficult      = ET.SubElement(obj, 'difficult')
            difficult.text = "0"
            bndbox         = ET.SubElement(obj, 'bndbox')
            xmin           = ET.SubElement(bndbox, 'xmin')
            xmin.text      = str(p[0])
            ymin           = ET.SubElement(bndbox, 'ymin')
            ymin.text      = str(p[1])
            xmax           = ET.SubElement(bndbox, 'xmax')
            xmax.text      = str(p[2])
            ymax           = ET.SubElement(bndbox, 'ymax')
            ymax.text      = str(p[3])
        string     = ET.tostring(annotation, 'utf-8')
        pretty_string = minidom.parseString(string).toprettyxml(indent='  ')
        
        xml_file = os.path.join("annotations/xmls/barcode_{0}.xml".format(i))
        with open(xml_file, 'w') as f:
            f.write(pretty_string)
    fp.close()
    fp2.close()

# positive
filenames = []
save_path = "images/positive/"
if not os.path.isdir(save_path):
    os.makedirs(save_path)
if not os.path.isdir("train_images"):
    os.makedirs("train_images")
save_path = save_path+"positive{0}"
fp        = open("positive.dat", 'w')
for i in range(NUMBER_OF_POSITIVE):
    print(i)
    bc, barcode_class = gen_barcode()
    filenames.append(bc.save(save_path.format(i), {"write_text":False}))
    img = resize_image(filenames[-1])
    img.save(save_path.format(i)+".jpg")
    if i!=0 and i%POSITIVE_COUNT==0:
        pasted_image, positions = paste_images(filenames, SIZE_OF_POSITIVE_IMAGE) # positions=>(x, y, w, h)
        pasted_image_name       = "images/positive/positive_pasted_image{0}.jpg".format(int(i/POSITIVE_COUNT)-1)
        train_pasted_image_name = "train_images/barcode_{0}.jpg".format(int(i/POSITIVE_COUNT)-1) # for object detection
        pasted_image.save(pasted_image_name)
        pasted_image.save(train_pasted_image_name)
        text = "{0} {1} ".format(pasted_image_name, len(positions))
        text += " ".join([" ".join([str(pos) for pos in position]) for position in positions])+"\n"
        fp.write(text)
        filenames = []
fp.close()

# negative
save_path = "images/negative/"
if not os.path.isdir(save_path):
    os.makedirs(save_path)
save_path = save_path+"negative{0}"
# dir_path = "/Users/sugiya/workspace/structured-ocr/test/images/"
fp = open("negative.dat", 'w')
# filenames = os.listdir(dir_path)
# for i in range(20):
#     print(i)
#     filename = random.choice(filenames)
#     path = os.path.join(dir_path, filename)
#     img  = Image.open(path)
#     img  = img.convert("L")
#     crop_pos = random_crop_position(img, SIZE_OF_NEGATIVE_IMAGE)
#     crop_img = img.crop(crop_pos)
#     crop_img.save(save_path.format(i))
#     fp.write(save_path.format(i)+"\n")

# negative
filenames = []
fp        = open("negative.dat", 'w')
for i in range(NUMBER_OF_NEGATIVE):
    print(i)
    bc, barcode_class = gen_barcode()
    filenames.append(bc.save(save_path.format(i), {"write_text":False}))
    img = resize_image(filenames[-1])
    img = break_barcode(img)
    img.save(save_path.format(i)+".jpg")
    if i!=0 and i%NEGATIVE_COUNT==0:
        pasted_image, positions = paste_images(filenames, SIZE_OF_NEGATIVE_IMAGE) # positions=>(x, y, w, h)
        pasted_image_name = "images/negative/negative_pasted_image{0}.jpg".format(int(i/NEGATIVE_COUNT)-1)
        pasted_image.save(pasted_image_name)
        text = "{0}\n".format(pasted_image_name)
        fp.write(text)
        filenames = []
fp.close()

if not os.path.isdir("annotations/xmls"):
    os.makedirs("annotations/xmls")
export_xml("positive.dat")
