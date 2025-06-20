import pyxel

GAME_TITLE = "Space Rescue"

SHIP_ACCEL_X = 0.08
SHIP_ACCEL_UP = 0.06
SHIP_ACCEL_DOWN = 0.04
MAX_SHIP_SPEED = 1.0
OBJECT_SPAWN_INTERVAL = 150


class OneKeyGame:
    def __init__(self):
        pyxel.init(160, 120, title=GAME_TITLE)

        pyxel.load("sake.pyxres")

        self.is_title = True
        self.reset_game()

        pyxel.run(self.update, self.draw)

    def reset_game(self):

        self.score = 0
        self.timer = 0

        self.ship_x = (pyxel.width -16) / 2
        self.ship_y = pyxel.height / 4
        self.ship_vx = 0
        self.ship_vy = 0
        self.ship_dir = 1
        self.is_jetting = False
        self.is_exploding = False

        self.survivors = []
        self.meteors = []

    def generate_distanced_pos(self, dist):
        while True:
            x =pyxel.rndi(0, pyxel.width - 8)
            y =pyxel.rndi(0, pyxel.height - 8)
            diff_x = x - self.ship_x
            diff_y = y - self.ship_y
            if diff_x**2 + diff_y**2 > dist**2:
                return (x, y)
            
    def add_survivor(self):
        survivor_pos = self.generate_distanced_pos(30)
        self.survivors.append(survivor_pos)

    def add_meteor(self):
        meteor_pos = self.generate_distanced_pos(60)
        self.meteors.append(meteor_pos)


        
    
    def update_ship(self):

        if pyxel.btn(pyxel.GAMEPAD1_BUTTON_A):
            self.is_jetting = True
            self.ship_vy = max(self.ship_vy - SHIP_ACCEL_UP, -MAX_SHIP_SPEED)
            self.ship_vx = max(
                min(self.ship_vx + self.ship_dir * SHIP_ACCEL_X, 1), -MAX_SHIP_SPEED
            )
            pyxel.play(0, 0)
        
        else:
            self.is_jetting = False
            self.ship_vy = min(self.ship_vy + SHIP_ACCEL_DOWN, MAX_SHIP_SPEED)

        if pyxel.btnr(pyxel.GAMEPAD1_BUTTON_A):
            self.ship_dir = -self.ship_dir

        self.ship_x += self.ship_vx
        self.ship_y += self.ship_vy

        if self.ship_x < 0:
            self.ship_x = 0
            self.ship_vx = abs(self.ship_vx)
            pyxel.play(0, 1)

        max_ship_x = pyxel.width - 16
        if self.ship_x > max_ship_x:
            self.ship_x = max_ship_x
            self.ship_vx = -abs(self.ship_vx)
            pyxel.play(0, 1)

        if self.ship_y < 0:
            self.ship_y < 0
            self.ship_vy = abs(self.ship_vy)
            pyxel.play(0, 1)

        max_ship_y = pyxel.height - 16
        if self.ship_y > max_ship_y:
            self.ship_y = max_ship_y
            self.ship_vy = -abs(self.ship_vy)
            pyxel.play(0, 1)   

    def add_objects(self):

        if self.timer == 0:
            self.add_survivor()
            self.add_meteor()
            self.timer = OBJECT_SPAWN_INTERVAL

        else:
            self.timer -= 1


    def check_ship_collision(self, x, y):
        return abs(self.ship_x - x) <= 10 and abs(self.ship_y - y) <= 10
    
    def handle_survivor_collisions(self):
        new_survivors = []
        for survivor_x, survivor_y in self.survivors:
            if self.check_ship_collision(survivor_x, survivor_y):
                self.score += 1
                pyxel.play(1, 2)
            else:
                new_survivors.append((survivor_x, survivor_y))
        self.survivors = new_survivors


    def handle_meteor_collisions(self):
        for meteor_x, meteor_y in self.meteors:
            if self.check_ship_collision(meteor_x, meteor_y):
                self.is_exploding = True
                self.is_title = True
                pyxel.play(1, 3)
    


    def update(self):
        if self.is_title:
            if pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
                self.is_title = False
                self.reset_game()
            return
        
        self.update_ship()
        self.add_objects()
        self.handle_survivor_collisions()
        self.handle_meteor_collisions()

    def draw_sky(self):
        num_grads = 4
        grad_height = 6
        grad_start_y = pyxel.height - grad_height * num_grads

        pyxel.cls(0)
        for i in range(num_grads):
            pyxel.dither((i+1) / num_grads )
            pyxel.rect(
                0, 
                grad_start_y + i * grad_height,
                pyxel.width,
                grad_height,
                1, 
            )
        pyxel.dither(1)


    def draw_ship(self):

        offset_y = (pyxel.frame_count % 3 + 2)if self.is_jetting else 0
        offset_x = offset_y * -self.ship_dir


        pyxel.blt(
            self.ship_x - self.ship_dir * 3 + offset_x,
            self.ship_y,
            0,
            0,
            0,
            16 * self.ship_dir,
            16,
            0,
        )

        pyxel.blt(
            self.ship_x,
            self.ship_y + 3 +offset_y,
            0,
            16,
            16, 
            16,
            16, 
            0,
        )

        pyxel.blt(self.ship_x, self.ship_y, 0, 16, 0, 16, 16, 0)


        if self.is_exploding:
            blast_x = self.ship_x + pyxel.rndi(1, 6)
            blast_y = self.ship_y + pyxel.rndi(1, 6)
            blast_radius = pyxel.rndi(2, 4)
            blast_color =pyxel.rndi(7, 10)
            pyxel.circ(blast_x, blast_y, blast_radius, blast_color)



    def draw_survivors(self):
        for survivor_x, survivor_y in self.survivors:
            pyxel.blt(survivor_x, survivor_y, 0, 32, 0,16, 16, 0)

    def draw_meteors(self):
        for meteor_x, meteor_y in self.meteors:
            pyxel.blt(meteor_x, meteor_y, 0, 48, 0, 16, 16, 0)        


    def draw_score(self):
        score = f"SCORE:{self.score}"
        for i in range(1, -1, -1):
            color = 7 if i == 0 else 0
            pyxel.text(3 + i, 3, score, color)

    def draw_title(self):
        for i in range(1, -1, -1):
            color = 10 if i == 0 else 8
            pyxel.text(57, 50+i, GAME_TITLE, color)
            pyxel.text(42, 70, "- Press Enter Key -", 3)


    def draw(self):
        
        self.draw_sky()
        self.draw_ship()
        self.draw_survivors()
        self.draw_meteors()
        self.draw_score()

        if self.is_title:
            self.draw_title()
            
OneKeyGame()