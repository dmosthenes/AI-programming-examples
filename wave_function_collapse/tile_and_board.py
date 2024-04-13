from PIL import Image, ImageChops
import os
from itertools import product
import math
import numpy as np
import pygame


class TileCreator():
    """
    Takes a set of images and generates a set of objects of the Tile class.
    Optionally rotates images as part of the set.
    """

    def __init__(self, tile_directory, scaling_factor, rotation=False):

        self.images = []

        # Load all the images from the directory
        for image_name in os.listdir(tile_directory):

            image = Image.open(os.path.join(tile_directory, image_name))
            width, height = image.size
            image = image.resize((scaling_factor, scaling_factor))

            self.images.append(image)

            # Rotate the image three times
            if rotation:

                rotated_images = [image.rotate(90 * i) for i in range(1,4)]

                # Compare each image to each other image
                mse_threshold = 1000
                if all([mse(image, rotated_images[i], mse_threshold) for i in range(3)]):
                    continue
                else:
                    self.images.extend(rotated_images)
             

    def generate_tiles(self):
        """
        Creates a dictionary of self.tiles and returns it, containing each tile
        with a sub dictionary listing compatible tiles for each side of the given
        tile.
        """

        # Loop over each image and create a dictionary of dictionaries
        # Containing the pixel average for each section of edge

        # This dictionary is a mapping of the name for each side to a list of 
        # tuples formatted as (colour average, image)
        # Eg. self.sides["top"] returns a list of the colour average of the top
        # of each image in the tileset with the image itself the [1] element of the tuple
        self.sides = {}

        # A list of the names of the sides
        name_of_sides = ["top", "right", "left", "bottom"]

        # Number the images / tiles
        self.numbered_images = {}
        for image_num, image in enumerate(self.images):

            self.numbered_images[image_num] = image

        # Initialise the four lists in the self.sides dictionary for each side
        for side in name_of_sides:
            self.sides[side] = []

        # This dictionary is a mapping from each image number to a dictionary  in which 
        # each side is a key and each value is the colour average for that side
        # Eg. self.tile_maps[2]["top"] returns the colour average for the
        # top of the second image.
        self.tile_maps = {}

        for image_num, image in self.numbered_images.items():
            
            self.tile_maps[image_num] = {}

            for side in name_of_sides:
                self.sides[side].append((average_colour_tuple(side, image, 3), image))
                self.tile_maps[image_num][side] = self.sides[side][-1][0]

        # Create a dictionary mapping each image to a dictionary of sides in which
        # each side is mapped to a list of other images which are compatible for
        # that side
        # Eg. self.tile_to_tile[2]["top"] returns a list of other images which
        # match with the top of the second image.
        self.tile_to_tile = {}

        for image_num, sides in self.tile_maps.items():

            self.tile_to_tile[image_num] = {}

            for side_name, side_value in sides.items():

                self.tile_to_tile[image_num][side_name] = set()

                # Ex. compare top with other top
                # Get other side list
                for other_side_value, other_image in self.sides[opposite(side_name)]:

                    if mse(side_value, other_side_value, 900):

                        # Get number of other image
                        other_image_num = -1
                        for num_num, other_other_image in self.numbered_images.items():
                            if other_other_image == other_image:
                               other_image_num = num_num

                        self.tile_to_tile[image_num][side_name].add(other_image_num)

        # Initialise the Tile objects for each image
        out = set()

        self.numbered_tiles = {}

        for image_num, image in self.numbered_images.items():

            tile = Tile(image, self.tile_to_tile[image_num])

            out.add(tile)

            self.numbered_tiles[image_num] = tile

            # out.append(Tile(image, [self.numbered_images[image_num] for image_num in self.tile_to_tile[image_num]]))

        self.tiles = out
        return out


def mse_deprecated(image1, image2, threshold):
    """
    Returns True if images are similar within threshold, otherwise False.
    """

    diff = ImageChops.difference(image1, image2)
    squared_diff = np.array(diff).astype(np.float32) ** 2
    mse = np.mean(squared_diff)

    if mse < threshold:
        return True
    return False

def mse(image1, image2, threshold):
    """
    Returns True if images are similar within threshold, otherwise False.
    """

    # Convert images to Numpy arrays
    array1 = np.array(image1).astype(np.float32)
    array2 = np.array(image2).astype(np.float32)

    # Calculate squared difference
    squared_diff = (array1 - array2) ** 2

    # Calculate mean squared error
    mse = np.mean(squared_diff)

    # Check if MSE is within threshold
    return mse < threshold


def average_colour_tuple(side, image, n):
    """
    Returns a tuple of n colour averages across a given edge: ((rgb), (rgb),(rgb)).
    """

    width, height = image.size

    # Gather pixels along each edge of the image
    match side:
        case "top":
            pixel_list = [image.getpixel((x, 0)) for x in range(0, width)]
        case "right":
            pixel_list = [image.getpixel((width-1, y)) for y in range(0, height)]
        case "bottom":
            pixel_list = [image.getpixel((x, height-1)) for x in range(0, width)]
        case "left":
            pixel_list = [image.getpixel((0, y)) for y in range(0, height)]

    return pixel_list

    split_list = []

    # split list into n parts
    split_length = len(pixel_list) // n

    for i in range(n):

        if i == n - 1:
            split_list.append(pixel_list[split_length * i:])
        
        else:
            split_list.append(pixel_list[split_length * i: split_length * (i + 1)])

    # Iterate over each sublist and find the average
    out = []

    for sub_list in split_list:

        # Pick middle pixel
        pix = sub_list[round(len(sub_list) / 2)]

        out.append(pix)

    return tuple(out)


def average_colour_tuple_deprecated(side, image, n):
    """
    Returns a tuple of n colour averages across a given edge: ((rgb), (rgb),(rgb)).
    """

    width, height = image.size
    step = int(math.sqrt(width))

    # Gather pixels along each edge of the image
    match side:
        case "top":
            pixel_list = [image.getpixel((x, 0)) for x in range(0, width, step)]
        case "right":
            pixel_list = [image.getpixel((width-1, y)) for y in range(0, height, step)]
        case "bottom":
            pixel_list = [image.getpixel((x, height-1)) for x in range(0, width, step)]
        case "left":
            pixel_list = [image.getpixel((0, y)) for y in range(0, height, step)]

    split_list = []

    # split list into n parts
    split_length = len(pixel_list) // n

    for i in range(n):

        if i == n - 1:
            split_list.append(pixel_list[split_length * i:])
        
        else:
            split_list.append(pixel_list[split_length * i: split_length * (i + 1)])

    # Iterate over each sublist and find the average
    out = []

    for sub_list in split_list:

        # Code for averaging out pixels in sub-list
        avg = (0, 0, 0)

        # Loop over each pixel in the sub_list
        for pixel in sub_list:

            avg = tuple(x + y for x,y in zip(avg, pixel))

        out.append(tuple(x / len(sub_list) for x in avg))

    # Return a tuple of colour average
    return tuple(out)


def opposite(side_name):
    """
    Returns the opoposite to the given side.
    """

    match side_name:
        case "right":
            return "left"
        case "left":
            return "right"
        case "top":
            return "bottom"
        case "bottom":
            return "top"


class Tile():
    """
    A Tile object with an image and compatible tiles dictionary.
    """

    def __init__(self, image, compatible_tiles):

        self.image = image
        self.width, self.height = image.size
        # List of numbers corresponding with numbered tiles dictionary
        self.compatible_tiles = compatible_tiles

        image_data = image.tobytes()

        width, height = image.size

        self.surface = pygame.image.fromstring(image_data, (width, height), image.mode)
    
    
    def __eq__(self, other):

        return self.image == other.image
    
    def __hash__(self):
        return hash(self.image.tobytes())

class Board():
    """
    A Board object containing a number of Square objects. Use the numbered_tiles
    dictionary to convert from the numbered tiles listed in the compatible tiles
    dictionary to actual images.
    """

    def __init__(self, rows, cols, tiles, numbered_tiles):
        # Create a Square for each position on the board
        self.rows = rows
        self.cols = cols
        self.tiles = tiles
        self.numbered_tiles = numbered_tiles
        self.squares = []
        # Create the squares for the board
        for i,j in product(range(rows), range(cols)):
            self.squares.append(Square(i,j,rows,cols))


class Square():
    """
    A Square object with a list of neighbours of the form (i,j) which constrain 
    the tiles that may be placed adjacent.
    """

    def __init__(self, x, y, width, height):
        self.coordinates = (x,y)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.neighbours = {}

        # Get coordinates for the neighbouring squares
        for iter, (i,j) in enumerate(product(range(x -1, x+2), range(y-1, y+2))):
            if i < 0 or i >= self.width or j < 0 or j >= self.height or iter % 2 == 0:
                continue

            if i == self.x -1:
                self.neighbours["left"] = (i,j)
            elif j == self.y -1:
                self.neighbours["top"] = (i,j)
            elif i == self.x +1:
                self.neighbours["right"] = (i,j)
            else:
                self.neighbours["bottom"] = (i,j)
    
    def __repr__(self):
        # return f"{self.x}, {self.y}, {self.neighbours}"
        return f"Square: ({self.x}, {self.y})"

        # return f"Square: ({self.x}, {self.y}) with neighbours: {self.neighbours}"
    
    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        if isinstance(other, Square):
            if (self.x, self.y) == (other.x, other.y):
                return True
        return False
    
    def __deepcopy__(self, memo):
        new_square = Square(self.x, self.y, self.width, self.height)
        memo[id(self)] = new_square
        return new_square


def test_compat(directory):

    tile_maker = TileCreator(directory, True)
    tiles = tile_maker.generate_tiles()

    os.mkdir("Test")

    for i, tile in enumerate(tiles):

        os.mkdir(os.path.join("test", f"{i}"))

        for side, other_tiles in tile.compatible_tiles.items():

            os.mkdir(os.path.join("test", f"{i}", f"{side}"))

            for j, other_tile in enumerate(other_tiles):

                other_image = tile_maker.numbered_images[other_tile]

                other_image.save(os.path.join("test", f"{i}", f"{side}", f"{j}.png"))

            tile.image.save(os.path.join("test", f"{i}", f"{side}", "current_image.png"))



def main():

#     tile_maker = TileCreator(os.path.join("images", "polka"), True)

#     tiles = tile_maker.generate_tiles()

#     # Print out which image numbers are possible for the top of the 0th tile
#     tile = tiles.pop()
#     tile = tiles.pop()
#     tile = tiles.pop()
#     tile = tiles.pop()
#     tile = tiles.pop()

#     for num, image in tile_maker.numbered_images.items():

#         image.save(f"{num}.png")

#         if image == tile.image:

#             print(num)

#     tile.image.save("current_image.png")

#     print(tile.compatible_tiles)

#     for image_num, image in tile_maker.numbered_images.items():

#         if image_num in tile.compatible_tiles["right"]:

#             image.save(f"compat-{image_num}.png")



    # s = Square(5, 15, 20, 20)
    # print(s.neighbours)

    test_compat(os.path.join("images", "grass_and_stone"))

if __name__ == "__main__":
    main()