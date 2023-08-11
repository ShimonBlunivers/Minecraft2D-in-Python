from tkinter import *
from PIL import Image,ImageTk
import math

class ItemDrop:
    def __init__(self, world, block):
        self.world = world
        self.block = block
        self.size = 20
        self.inventory = self.world.inventory
        self.isTool = False
        self.drop_image = ImageTk.PhotoImage((self.block.material.texture_drop).resize((self.size, self.size), Image.ANTIALIAS))
        self.bounce_speed_limit = 50
        self.fall_speed = 5
        self.y_speed = 0
        self.grounded = False

        self.entity = world.canvas.create_image(self.world.canvas.coords(self.block.block_entity)[0] + self.world.one_block_width/2 - self.size/2 ,self.world.canvas.coords(self.block.block_entity)[1] - self.world.one_block_width/2 , anchor=NW, image=self.drop_image)
        self.world.entities.append(self.entity)
        self.real_position = [self.block.position[0] * world.one_block_width, self.block.position[1] * world.one_block_width]
        self.position = self.world.canvas.coords(self.entity)
        self.world.items_on_ground.append(self)


    def update(self):
        self.position = self.world.canvas.coords(self.entity)
        self.distance_from_player = round(math.hypot((self.position[0]+self.size/2) - self.world.player_coords[0]-self.world.main_player.width/2, (self.position[1]+self.size/2) - self.world.player_coords[1]-self.world.main_player.height/2))

        if self.distance_from_player > (self.world.main_player.range*100/3):
            
            self.grounded = False
            touching = self.world.canvas.find_overlapping(self.real_position[0], self.real_position[1], self.real_position[0] + self.world.one_block_width, self.real_position[1] + self.world.one_block_width + self.size)
            
            for ground in self.world.ground_tiles:
                if ground.block_entity in touching: 
                    self.grounded = True
            if self.grounded:
                self.y_speed += 1
                self.world.canvas.move(self.entity, 0, (abs(self.y_speed)-self.bounce_speed_limit/2)/10)
                if self.y_speed >= self.bounce_speed_limit:
                    self.y_speed = -self.bounce_speed_limit
            else:
                self.world.canvas.move(self.entity, 0, self.fall_speed)
                self.real_position[1] += self.fall_speed
        else:
            speed = 5
            if (self.position[0]+self.size/2) < (self.world.player_coords[0]+self.world.main_player.width/2):
                self.world.canvas.move(self.entity, speed, 0)
                self.real_position[0] += speed
            else:
                self.world.canvas.move(self.entity, -speed, 0)
                self.real_position[0] -= speed
            
            if (self.position[1]+self.size/2) < (self.world.player_coords[1]+self.world.main_player.height/2):
                self.world.canvas.move(self.entity, 0, speed)
                self.real_position[1] += speed
            else:
                self.world.canvas.move(self.entity, 0, -speed)
                self.real_position[1] -= speed

        if self.distance_from_player < (self.world.main_player.range*100/5):
            self.destroy()
            self.pick_up_block()


    def destroy(self):
        self.world.canvas.delete(self.entity)
        self.world.items_on_ground.remove(self)
        self.world.entities.remove(self.entity)

    def pick_up_block(self):
        
        for slot in self.inventory.slots:
            
            if slot.item == self.block.material.name and slot.amount < self.block.material.stack:
                slot.amount += 1
                slot.showItem()
                return
            elif slot.item == None:
                slot.item = self.block.material.name
                slot.amount = 1
                slot.showItem()
                return