import pyxel
import math
import random


class Block:
    def __init__(self, color):
        self.doomed = False
        self.color = color


class GameBlock:
    def __init__(self, x, y):
        colors = [None]*3
        self.b1 = Block(random.randint(7,11))
        self.b2 = Block(random.randint(7,11))
        self.b3 = Block(random.randint(7,11))
        self.x = x
        self.y = y

    def draw(self):
        pyxel.rect(self.x, self.y, self.x + 9, self.y + 9, self.b1.color)
        pyxel.rect(self.x, self.y + 10, self.x + 9, self.y + 19, self.b2.color)
        pyxel.rect(self.x, self.y + 20, self.x + 9, self.y + 29, self.b3.color)


class App:
    def __init__(self):
        self.amount_of_rows = 30
        self.amount_of_blocks = 7*self.amount_of_rows
        self.block_array = [None]*self.amount_of_blocks
        self.gb = GameBlock(40,10)
        self.nb = GameBlock(180,10)
        self.left_block = False
        self.right_block = False
        self.score = 0
        self.highscore = 0
        self.gameon = False
        self.speed = 1
        self.label = "PRESS SPACE BAR TO START..."
        pyxel.init(200, 255, caption='Resourcis')
        pyxel.run(self.update, self.draw)

    # read inputs, move things
    def update(self):
        self.left_block = False
        self.right_block = False

        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if not self.gameon and not pyxel.btn(pyxel.KEY_SPACE):
            return

        elif not self.gameon and pyxel.btn(pyxel.KEY_SPACE):
            self.gameon = True
            self.label = "Play!"
            self.block_array = [None] * self.amount_of_blocks
            self.score=0
            pyxel.sound(0).set('RF3F3F3', 'TTSS PPPN', '7777 7531', 'NFNF NVVS', 60)
            pyxel.sound(0).speed = 60
            pyxel.play(0,0)

        # change the colors
        if pyxel.btnp(pyxel.KEY_UP):
            tb = self.gb.b1
            self.gb.b1 = self.gb.b2
            self.gb.b2 = self.gb.b3
            self.gb.b3 = tb

        # speedfall
        if pyxel.btn(pyxel.KEY_SPACE) or pyxel.btn(pyxel.KEY_DOWN):
            self.gb.y += self.speed * 3

        # make the gameblock (normal) fall
        self.gb.y += self.speed

        # boundaries
        i = self.coordinates_to_index(self.gb.x, self.gb.y+20)

        # find out if there is a block below
        if i > 6:
            if self.block_array[i-7] is not None:
                self.save_blocks_to_array()

        # find out if there is a block on the left
        if (i%7 != 0):
            if self.block_array[i-1] is not None:
                self.left_block = True

        # find out if there is a block on the right
        if (i%7 != 6):
            if self.block_array[i+1] is not None:
                self.right_block = True

        # check if hits the floor
        if self.gb.y + 30 > 240:
            self.save_blocks_to_array()

        # finally move if possible
        if pyxel.btnp(pyxel.KEY_LEFT) and not self.left_block and self.gb.x>19:
            self.gb.x -= 10

        if pyxel.btnp(pyxel.KEY_RIGHT) and not self.right_block and self.gb.x<70:
            self.gb.x += 10

        self.find_adjacent_colors_in_rows()
        self.find_adjacent_colors_in_columns()

        # finally kill the doomed ones
        self.doom()

        # let loose pieces fall
        self.cleanup()

        # make it faster little by little
        if (pyxel.frame_count%450 == 0):
            self.speed = self.speed + 0.1

    # take the blocks and put them into the array
    def save_blocks_to_array(self):
        self.block_array[self.coordinates_to_index(self.gb.x, self.gb.y)] = self.gb.b1
        self.block_array[self.coordinates_to_index(self.gb.x, self.gb.y + 10)] = self.gb.b2
        self.block_array[self.coordinates_to_index(self.gb.x, self.gb.y + 20)] = self.gb.b3
        # check gameover when storing the blocks
        if self.gb.y < 40:
            self.gameover()
        # next piece
        self.gb = self.nb
        self.gb.x=40
        self.gb.y=10
        self.nb = GameBlock(180,10)

    # what to do when game is over
    def gameover(self):
        self.label = "GAME OVER!"
        self.gameon = False
        if self.score > self.highscore:
            self.highscore = self.score

    # find colors
    def find_adjacent_colors_in_rows(self):
        # one row at a time
        for l in range(self.amount_of_rows):
            for i in range(0,7):
                # start from the third block in the row
                if (i > 1):
                    c1 = self.block_array[i+l*7]
                    c2 = self.block_array[i-1+l*7]
                    c3 = self.block_array[i-2+l*7]

                    # check same 3 colors on a row
                    if c1 != None and c2 != None and c3 != None and c1.color == c2.color and c2.color == c3.color:
                        c1.doomed = c2.doomed = c3.doomed =True

    def find_adjacent_colors_in_columns(self):
        # one column at a time
        for l in range(0, 7):
            for i in range(self.amount_of_rows):
                # start from the 3rd block in the column
                    if (i > 1):
                        c1 = self.block_array[l+i*7-14]
                        c2 = self.block_array[l+i*7-7]
                        c3 = self.block_array[l+i*7]

                        # check same 3 colors on a column
                        if c1 != None and c2 != None and c3 != None and c1.color == c2.color and c2.color == c3.color:
                            c1.doomed = c2.doomed = c3.doomed = True

    # delete doomed blocks
    def doom(self):
        for i in range(self.amount_of_blocks):
            if self.block_array[i] != None and self.block_array[i].doomed:
                self.score += 1
                self.block_array[i] = None

    # cleanup
    def cleanup(self):
        # find all blocks which are not on the bottom row and which have no block below
        for i in range(len(self.block_array)-7):
            if self.block_array[i+7] is not None:
                if self.block_array[i] is None:
                    self.block_array[i] = self.block_array[i+7]
                    self.block_array[i+7] = None

    def coordinates_to_game_coordinates(self, x, y):
        # x is always in sync between 10 pixels
        gx = (x/10)-1
        gy = math.floor((y-10)/10)
        return int(gx), int(22-gy)

    def game_coordinates_to_index(self, x, y):
        return 7*y+x

    def coordinates_to_index(self, x, y):
        gx, gy = self.coordinates_to_game_coordinates(x, y)
        return self.game_coordinates_to_index(gx, gy)

    def index_to_coordinates(self, index):
            row = math.floor(index/7)
            column = index%7
            return ((1+column)*10), 10+((22-row)*10)

    # draw everything
    def draw(self):
        # clear screen
        pyxel.cls(1)

        # draw all the blocks in the grid
        for i in range(len(self.block_array)):
            # draw only if there is a block there
            if self.block_array[i] is not None:
                x,y = self.index_to_coordinates(i)
                pyxel.rect(x, y, x + 9, y + 9, self.block_array[i].color)

        # draw the gameblocks
        if self.gameon:
            self.gb.draw()
            self.nb.draw()

        # draw dashboard
        pyxel.text(100, 10,"SCORE: "+str(self.score),6)
        pyxel.text(100, 30, "HIGH SCORE: " + str(self.highscore), 6)
        pyxel.text(100, 240, self.label, 6)

        # draw floor and walls
        pyxel.rect(1, 240, 88, 248, 12)
        pyxel.rect(1, 0, 8, 247, 12)
        pyxel.rect(81, 0, 88, 247, 12)

        # bar
        pyxel.rect(1, 50, 8, 52, 10)
        pyxel.rect(81, 50, 88, 52, 10)

        # pyxel.blt(10,10,0,0,0,10,10)


App()
