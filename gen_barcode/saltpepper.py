import random
from   itertools import product
from   PIL       import Image

def saltpepper(img, salt=0.05, pepper=0.05):
    w, h = img.size
    output_image = Image.new("RGB", img.size)
    output_pix   = output_image.load()
    img_pix      = img.load()
    for i, (x, y) in enumerate(product(*map(range, (w, h)))):
        r = random.random()
        if r < salt:
            output_pix[x, y] = (255, 255, 255)
        elif r > 1 - pepper:
            output_pix[x, y] = (0, 0, 0)
        else:
            output_pix[x, y] = img_pix[x, y]
    return output_image

if __name__ == "__main__":
    img = Image.open("./test.png")
    saltpepper(img).save("salt.png")
