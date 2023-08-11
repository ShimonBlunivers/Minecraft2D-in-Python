from tkinter import *
from PIL import Image,ImageTk

class Zombie:

    def __init__(self, world, spawn_location):

        self.world = world
        self.health = 5
        self.max_health = self.health
        self.spawn_location = spawn_location
        self.position = self.spawn_location
        self.grounded = False
        self.height = 120
        self.width = 48
        self.damage = 1

        self.sight = 20
        self.range = 2

        image = 'zombie'
        img = (Image.open(image+'.png'))
        img = img.resize((self.width,self.height), Image.ANTIALIAS)
        self.img = ImageTk.PhotoImage(img)
        self.hitImg = ImageTk.PhotoImage((Image.open('zombiehit.png')).resize((self.width,self.height), Image.ANTIALIAS))
        self.fall_acceleration = .2
        self.y_speed = 0
        self.speed = 0
        self.jump_speed = 5 # 5
        self.walk_speed = 3 # 3
        self.cooldown = 0
        self.hitCooldown = 80

        self.object = self.world.canvas.create_image(self.spawn_location[0], self.spawn_location[1], anchor=NW, image=self.img)

        self.world.mobs.append(self)
        self.world.zombies.append(self)

    def update(self):
        self.real_position = [self.position[0] + self.world.world_position[0], self.position[1] + self.world.world_position[1]]

        if self.health <= 0:
            self.die()
        
        if self.cooldown > 0:
            self.cooldown -= 1


        self.fall()
        self.AI()
        self.move()
        self.world.canvas.moveto(self.object, self.real_position[0], self.real_position[1])

    def move(self):
        blocked = False
        touching = self.world.canvas.find_overlapping(self.real_position[0] + self.speed, self.real_position[1] + 5, self.real_position[0] + self.width + self.speed, self.real_position[1] + self.height - 5)
        for blok in self.world.ground_tiles:
            if blok.block_entity in touching:
                blocked = True
        if not blocked:
            self.position[0] += self.speed

        self.position[1] += self.y_speed
    
    def fall(self):
        self.grounded = False

        touching = self.world.canvas.find_overlapping(self.real_position[0], self.real_position[1], self.real_position[0] + self.width, self.real_position[1] + self.height + self.y_speed)
        for blok in self.world.ground_tiles:
            if blok.block_entity in touching:
                self.grounded = True
                self.y_speed = 0

        if not self.grounded:
            self.y_speed += self.fall_acceleration

            
        
    def jump(self):
        if self.grounded:
            self.y_speed = -self.jump_speed



    def AI(self):
        prejump_detect = self.world.canvas.find_overlapping(self.real_position[0] - self.width, self.real_position[1] + self.height/3, self.real_position[0] + self.width*2, self.real_position[1] + self.height - self.height/3)
        jump = False
        for blok in self.world.ground_tiles:
            if blok.block_entity in prejump_detect:
                jump = True


        if self.world.main_player.player_image in self.world.canvas.find_overlapping(self.real_position[0] - self.sight*10, self.real_position[1] - self.sight*5, self.real_position[0] + self.width + self.sight*10, self.real_position[1] + self.height + self.sight*5):
            if self.world.main_player.player_image not in self.world.canvas.find_overlapping(self.real_position[0] - self.range*10, self.real_position[1] - self.range*5, self.real_position[0] + self.width + self.range*10, self.real_position[1] + self.height + self.range*5):
                if self.real_position[0] < self.world.main_player.player_coords[0]:
                    self.speed = self.walk_speed
                else:
                    self.speed = -self.walk_speed
                if jump and self.speed != 0:
                    self.jump()
            else:
                self.speed = 0
                if self.cooldown == 0:
                    self.world.main_player.hit(self.damage)
                    self.cooldown = self.hitCooldown

        else:
            self.speed = 0
            

    def hit(self, damage):
        self.hitted = True
        self.world.canvas.delete(self.object)
        self.object = self.world.canvas.create_image(self.real_position[0], self.real_position[1], anchor=NW, image=self.hitImg)
        self.health -= damage
        # self.knockback(1)
        self.world.window.after(200, self.deleteHitImage)

    def deleteHitImage(self):
        self.hitted = False
        
        self.world.canvas.delete(self.object)
        if self.health > 0:
            self.object = self.world.canvas.create_image(self.real_position[0], self.real_position[1], anchor=NW, image=self.img)


    def die(self):
        self.world.canvas.delete(self.object)
        self.world.zombies.remove(self)
        self.world.mobs.remove(self)
