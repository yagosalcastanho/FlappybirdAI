import pygame
import os
import random
import neat

#definição de variaveis como modo de jogo, gerações de ia, tamanho da tela, imagens de fundo e do flapy, placar e fonte
ai_playing = True
ai_generation = 0

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 800

IMAGE_TUBE = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
IMAGE_GROUND = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
IMAGE_BACKGROUND = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
IMAGES_BIRD = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png'))),
]

pygame.font.init()
FONT_POINTS = pygame.font.SysFont('arial', 50) #fonte score pontos

class Flappy: 
    IMGS = IMAGES_BIRD 
    #animação de rotação do flappy bird
    MAX_ROTATION = 25
    VEL_ROTATION = 20
    TEMP_ANIMATION = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.vel = 0
        self.height = self.y
        self.temp = 0
        self.cont_image = 0
        self.image = self.IMGS[0]

    def jump(self):
        self.vel = -10.5
        self.temp = 0
        self.height = self.y

    def move(self): 
    #calcular deslocamento
        self.temp += 1
        translation = 1.5 * (self.temp**2) + self.vel * self.temp

    #restringir deslocamento
        if translation > 16:
            translation = 16
        elif translation < 0:
            translation -= 2

    #angulo do flappy bird
        self.y += translation
        
        if translation < 0 or self.y < (self.height + 50):
            if self.angle < self.MAX_ROTATION:
                self.MAX_ROTATION = self.MAX_ROTATION
        else:
            if self.angle > -90:
                self.angle -= self.MAX_ROTATION
        
    def draw(self, screen):
    #definir qual imagem o flappy vai usar
        self.cont_image += 1

        if self.cont_image < self.TEMP_ANIMATION:
            self.image = self.IMGS[0]
        elif self.cont_image < self.TEMP_ANIMATION*2:
            self.image = self.IMGS[1]
        elif self.cont_image < self.TEMP_ANIMATION*3:
            self.image = self.IMGS[2]
        elif self.cont_image < self.TEMP_ANIMATION*4:
            self.image = self.IMGS[1]
        elif self.cont_image >= self.TEMP_ANIMATION*4 + 1:
            self.image = self.IMGS[0]
            self.cont_image = 0

    #se o flappy estiver caindo e não bater asa
        if self.angle <= -80:
            self.image = self.IMGS[1]
            self.cont_image = self.TEMP_ANIMATION*2

    #desenha imagem flappy rotacionada
        image_turned = pygame.transform.rotate(self.image, self.angle)
        post_center_image = self.image.get_rect(topleft=(self.x, self.y)).center
        rectangle = image_turned.get_rect(center=post_center_image)
        screen.blit(image_turned, rectangle.topleft)

    #if mascara flappy tem pixel em comun com tube, bate, else não bate.
    def get_mask(self):
        return pygame.mask.from_surface(self.image)

class Tube:
    DISTANCE = 200
    VELOCITY = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.post_top = 0
        self.post_base = 0
        self.TUBE_TOP = pygame.transform.flip(IMAGE_TUBE, False, True)
        self.TUBE_BASE = IMAGE_TUBE
        self.passed = False
        self.define_height()
        
    #altura dos tubes
    def define_height(self):
        self.height = random.randrange(50, 450)
        self.post_top = self.height - self.TUBE_TOP.get_height()
        self.post_base = self.height + self.DISTANCE

    def move(self):
        self.x -= self.VELOCITY

    #desenho tubes normais e invertidos na tela
    def draw(self, screen):
        screen.blit(self.TUBE_TOP, (self.x, self.post_top))
        screen.blit(self.TUBE_BASE, (self.x, self.post_base))

    #caso flappy acerte o tube
    def colision(self, flappy_bird):
        flappy_mask = flappy_bird.get_mask()
        top_mask = pygame.mask.from_surface(self.TUBE_TOP)
        base_mask = pygame.mask.from_surface(self.TUBE_BASE)

        distance_top = (self.x - flappy_bird.x, self.post_top - round(flappy_bird.y))
        distance_base = (self.x - flappy_bird.x, self.post_base - round(flappy_bird.y))

    #pega mask top, mask base, mask do flappy e verifica colisao entre elas
        top_point = flappy_mask.overlap(top_mask, distance_top)
        base_point = flappy_mask.overlap(base_mask, distance_base )
    
        if base_point or top_point:
            return True
        else: 
            return False
    

class Ground:
    VELOCITY = 5
    WIDTH = IMAGE_GROUND.get_width()
    IMAGE = IMAGE_GROUND
    
    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
    #passagem do chão negativa(pra esquerda) em relação a tela
    #x2 + largura = posição do x1 (mesma coisa inversamente)

    def move(self):
        self.x1 -= self.VELOCITY
        self.x2 -= self.VELOCITY

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, screen):
        screen.blit(self.IMAGE, (self.x1, self.y))
        screen.blit(self.IMAGE, (self.x2, self.y))

def draw_screen(screen, flappys, tubes, ground, points):
    screen.blit(IMAGE_BACKGROUND, (0, 0))
    for flappy_bird in flappys:
        flappy_bird.draw(screen)
    for tube in tubes:
        tube.draw(screen)

    text = FONT_POINTS.render(f'Score: {points}', 1, (255, 255, 255))
    screen.blit(text, (SCREEN_WIDTH - 10 - text.get_width(), 10))

    if ai_playing:
        text = FONT_POINTS.render(f'Gen: {ai_generation}', 1, (255, 255, 255))
        screen.blit(text, (10, 10))


    ground.draw(screen)
    pygame.display.update()

def main(genomes, config): 
    #fitness function (o quão bem o flappy ta voando), no NEAT precisa de dois parametros
    #um cria config redes neurais (genome), outro os criterios NEAT (config)
    global ai_generation
    ai_generation += 1

    if ai_playing:
        neural_nets = []
        genome_lists = []
        flappys = []
        #variavel descartavel na lista de tuplas
        for _, genome in genomes:
            neural_net = neat.nn.FeedForwardNetwork.create(genome, config)
            neural_nets.append(neural_net)
            genome.fitness = 0 #score interna flappy, se ele erra, ele perde, se acerta, ele ganha
            genome_lists.append(genome)
            flappys.append(Flappy(230, 350))
    else:
        flappys = [Flappy(230, 350)]
    ground = Ground(736)
    tubes = [Tube(700)]
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    points = 0
    clock = pygame.time.Clock()
    #um jogo é um constante while true com varios refreshs

    running = True
    while running:
        clock.tick(30)
    #define lista de eventos com interação do usuario

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()
            #espaço pra pular se for "playing", se for "ia" não
            if not ai_playing:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        for flappy in flappys:
                            flappy.jump()

        index_tube = 0
        #descobrir qual tube olhar
        if len(flappys) > 0:
            if len(tubes) > 1 and flappys[0].x > (tubes[0].x + tubes[0].TUBE_TOP.get_width()):
                index_tube = 1
        else:
            running = False
            break

        #mover cenario
        for i, flappy in enumerate(flappys):
            flappy.move()
            #aumentar fitness flappy gradualmente
            genome_lists[i].fitness += 0.1
            output = neural_nets[i].activate((flappy.y,
                                                abs(flappy.y - tubes[index_tube].height),
                                                abs(flappy.y - tubes[index_tube].post_base)))
            # -1 e 1 -> if output > 0.5 flappy pula
            if output[0] > 0.5:
                flappy.jump()
        ground.move()

        add_tube = False
        remove_tubes = []
        for tube in tubes:
            #pega flappy dentro posição listas, se ele colidir com o cano, remove da lista.
            for i, flappy in enumerate(flappys):
                if tube.colision(flappy):
                    flappys.pop(i)
                    if ai_playing:
                        genome_lists[i].fitness -= 1 #penalizar ia por errar
                        genome_lists.pop(i)
                        neural_nets.pop(i)
                #se flappy já passou por um tube, criar um novo, movendo tubes
                if not tube.passed and flappy.x > tube.x:
                    tube.passed = True
                    add_tube = True

            tube.move()
            if tube.x + tube.TUBE_TOP.get_width() < 0:
                remove_tubes.append(tube)
                
        #se flappy passa por um cano, soma um ponto
        if add_tube:
            points += 1
            tubes.append(Tube(600))
            for genome in genome_lists:
                genome.fitness += 5
        for tube in remove_tubes:
            tubes.remove(tube)

        #se a posição do flappy for abaixo do chão ou acima do teto, o flappy morre
        for i, flappy in enumerate(flappys):
            if(flappy.y + flappy.image.get_height()) > ground.y or flappy.y < 0:
                flappys.pop(i)
                if ai_playing:
                    genome_lists.pop(i)
                    neural_nets.pop(i)

        draw_screen(screen, flappys, tubes, ground, points )

def run_neat(config_path):
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,  
                                config_path)
    
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())

    if ai_playing:
        population.run(main, 50)
    else:
        main(None, None)


if __name__ == '__main__':
    path = os.path.dirname(__file__)
    path_config = os.path.join(path, 'config.txt')
    run_neat(path_config)