from tkinter import *
from PIL import Image,ImageTk
from items import *

class Block:

    def __init__(self, material, world, position):
        
        self.tick = 10
        self.start_position = position
        self.position = position
        self.world = world
        self.hit_textures = []
        self.material = material
        self.calm_cycles = 0
        if material.hex_color == True:
            self.block_entity = world.canvas.create_rectangle(self.position[0] * world.one_block_width, self.position[1] * world.one_block_width, self.position[0] * world.one_block_width + world.one_block_width, self.position[1] * world.one_block_width + world.one_block_width, fill = material.texture, width = 0)
        else:
            self.block_entity = world.canvas.create_image(self.position[0] * world.one_block_width, self.position[1] * world.one_block_width, anchor=NW, image=material.texture)

        self.health = material.durability
        self.max_health = material.durability

        if material.collisional:
            world.ground_tiles.append(self)
        if material.name == 'ladder':
            world.ladder_tiles.append(self)
        self.world.entities.append(self.block_entity)
        world.blocks.append(self) 
        self.world.blocksID[self.block_entity] = self

    def update(self):

        self.position = [self.start_position[0] + self.world.world_position[0]/self.world.one_block_width, self.start_position[1] + self.world.world_position[1]/self.world.one_block_width]

        self.world.blocksID[self.block_entity] = self
        if self.health == 0:
            self.destroy()

        if self.health > 0:
            if self.health != self.max_health:
                self.calm_cycles += 1

            if self.calm_cycles == 400:
                self.calm_cycles = 0
                self.health += 1
                if len(self.hit_textures) != 0:
                    for x in self.hit_textures:
                        self.world.canvas.delete(x)
                        self.hit_textures.remove(x)
                        self.world.entities.remove(x)
                if self.health > 0:
                    if self.health == self.max_health -1:
                        hit = self.material.hit1
                    if self.health == self.max_health -2:
                        hit = self.material.hit2
                    if self.health == self.max_health -3:
                        hit = self.material.hit3
                    
                    if self.health != self.max_health:
                        self.hit_texture = self.world.canvas.create_image(self.world.canvas.coords(self.block_entity)[0],self.world.canvas.coords(self.block_entity)[1], anchor=NW, image=hit)
                        self.hit_textures.append(self.hit_texture)
                        self.world.entities.append(self.hit_texture)
    def destroy(self):
            ItemDrop(self.world, self)
            self.world.blocks.remove(self)
            self.world.canvas.delete(self.block_entity)




class Material:
    def __init__(self, name, texture, collisional, durability, world):

        if list(texture)[0] == '#':
            self.texture = texture
            self.hex_color = True
        else:
            self.texture = ImageTk.PhotoImage((Image.open(texture+'.png')).resize((world.one_block_width, world.one_block_width), Image.ANTIALIAS))
            self.hex_color = False
        
        self.hit1 = ImageTk.PhotoImage((Image.open('hit1.png')).resize((world.one_block_width, world.one_block_width), Image.ANTIALIAS))
        self.hit2 = ImageTk.PhotoImage((Image.open('hit2.png')).resize((world.one_block_width, world.one_block_width), Image.ANTIALIAS))
        self.hit3 = ImageTk.PhotoImage((Image.open('hit3.png')).resize((world.one_block_width, world.one_block_width), Image.ANTIALIAS))

        self.code = ''
        self.collisional = collisional
        self.name = name
        self.isTool = False
        self.texture_drop = Image.open(f'{self.name}drop.png')
        self.stack = 64
        self.durability = durability
        
        if self.name.lower() == 'ground':
            self.code = 'G'
        elif self.name.lower() == 'bedrock':
            self.code = 'Q'
        elif self.name.lower() == 'wood':
            self.code = 'w'
        elif self.name.lower() == 'water':
            self.code = 'W'
        elif self.name.lower() == 'leaf':
            self.code = 'L'
        elif self.name.lower() == 'grass':
            self.code = 'g'
        elif self.name.lower() == 'ladder':
            self.code = 'l'
            self.stack = 16
        elif self.name.lower() == 'stone':
            self.code = 'S'

        world.materials.append(self)