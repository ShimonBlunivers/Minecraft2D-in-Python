from tkinter import *
from PIL import Image,ImageTk

class Player:

    def __init__(self, image, window, canvas, dimensions, world):
        
        self.world = world
        self.health = 5
        self.max_health = self.health
        self.spawn_location = [850,200]
        self.dimensions = dimensions
        self.window = window
        self.canvas = canvas
        self.grounded = False
        self.height = 120
        self.width = 48
        img = (Image.open(image+'.png'))
        img = img.resize((self.width,self.height), Image.ANTIALIAS)
        self.img = ImageTk.PhotoImage(img)
        self.tick = 10
        self.fall_acceleration = .2
        self.fall_speed = 0
        self.speed = 4
        self.jump_speed = 6 # 6
        self.ground_tiles = []
        self.ladder_tiles = []
        self.blocks = []
        self.wall_bump = False
        self.ladder = False
        self.climbing_speed = 3
        self.left = False
        self.right = False
        self.jumping = False # Jumping/Not jumping
        self.climbing = False
        self.range = 2
        self.generate()
        self.player_coords = self.canvas.coords(self.player_image)
        self.hitImg = ImageTk.PhotoImage((Image.open('dead.png')).resize((self.width,self.height), Image.ANTIALIAS))
        self.dead = False
        self.knockback_force = 0
        self.hitted = False
        self.cooldown = 0

    def generate(self):
        self.player_image = self.canvas.create_image(self.spawn_location[0], self.spawn_location[1], anchor=NW, image=self.img)

    def key_release(self, event):

        if event.keysym.lower() == 'a':
            self.left = False
        if event.keysym.lower() == 'd':
            self.right = False
        if event.keysym.lower() == 'space':
            self.jumping = False
        if event.keysym.lower() == 'w':
            self.climbing = False

    def key_press(self,event):
        if event.keysym.lower() == 'a':
            self.left = True

        if event.keysym.lower() == 'd':
            self.right = True

        if event.keysym.lower() == 'space':
            self.jumping = True

        if event.keysym.lower() == 'w':
            self.climbing = True
        
        self.world.inventory.select(event)

    def control(self):

        self.wall_bump = False

        player_coords = self.canvas.coords(self.player_image)
        self.player_coords = self.canvas.coords(self.player_image)
        if self.left and not self.right:
            touching = self.canvas.find_overlapping(player_coords[0] - self.speed, player_coords[1], player_coords[0] + self.width, player_coords[1] + self.height - 1)
            for ground in self.ground_tiles:
                for touch in touching:
                    if touch == ground.block_entity:
                        self.wall_bump = True
            if self.wall_bump == False:
                if player_coords[0] > self.dimensions[0]/4:
                    self.canvas.move(self.player_image, -self.speed, 0)
                else:
                    self.world.world_position[0] += self.speed
                    for blok in self.world.entities:
                        self.canvas.move(blok, self.speed, 0)

        if self.right and not self.left:
            touching = self.canvas.find_overlapping(player_coords[0], player_coords[1], player_coords[0] + self.width + self.speed, player_coords[1] + self.height - 1)
            for ground in self.ground_tiles:
                for touch in touching:
                    if touch == ground.block_entity:
                        self.wall_bump = True
            if self.wall_bump == False:
                if player_coords[0] + self.width < self.dimensions[0] - self.dimensions[0]/4:
                    self.canvas.move(self.player_image, self.speed, 0)
                else:
                    self.world.world_position[0] -= self.speed
                    for blok in self.world.entities:
                        self.canvas.move(blok, -self.speed, 0)
        
        if self.climbing:
            self.ladder = False
            touching = self.canvas.find_overlapping(player_coords[0], player_coords[1], player_coords[0] + self.width, player_coords[1] + self.height)
            for ledr in self.ladder_tiles:
                for touch in touching:
                    if touch == ledr.block_entity:
                        self.ladder = True
                        self.grounded = True
            if self.ladder == True:
                self.fall_speed = -self.climbing_speed


        if self.jumping and self.grounded:
            self.fall_speed = -self.jump_speed


    def death(self):
        self.dead = True
        self.world.window.after(169, self.die)  

    def die(self):
        self.canvas.delete(self.player_image)
        self.world.window.after(2000, self.exit) 

    def exit(self):
        self.window.destroy()

    def hit(self, damage):
        self.hitted = True
        self.canvas.delete(self.player_image)
        self.player_image = self.canvas.create_image(self.player_coords[0], self.player_coords[1], anchor=NW, image=self.hitImg)
        self.health -= damage
        # self.knockback(1)
        self.world.window.after(200, self.deleteHitImage)

    def deleteHitImage(self):
        self.hitted = False
        
        self.canvas.delete(self.player_image)
        self.player_image = self.canvas.create_image(self.player_coords[0], self.player_coords[1], anchor=NW, image=self.img)
    
    def knockback(self, force):
        self.knockback_force = -force * 10
        self.world.window.after(20*force, self.knockback_end)

    def knockback_end(self):
        self.knockback_force = 0
