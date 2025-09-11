import pygame
import random
import os

# Inicializa o Pygame
try:
    pygame.init()
except Exception as e:
    print(f"Erro ao inicializar Pygame: {e}")
    exit()

# --- Configurações da tela ---
info_tela = pygame.display.Info()
LARGURA, ALTURA = info_tela.current_w, info_tela.current_h
tela = pygame.display.set_mode((LARGURA, ALTURA), pygame.FULLSCREEN)
pygame.display.set_caption("SpaceFox")

# --- Cores ---
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CINZA = (150, 150, 150)
AZUL_CLARO = (50, 50, 200)

# --- Caminho dos arquivos de imagem ---
pasta_do_jogo = "/storage/emulated/0/SpaceFox"
caminho_jogador = os.path.join(pasta_do_jogo, "player.png")
caminho_obstaculo = os.path.join(pasta_do_jogo, "obstacle.png")
caminho_fundo = os.path.join(pasta_do_jogo, "fundo.png")

# --- Carrega e redimensiona as imagens ---
try:
    imagem_jogador = pygame.image.load(caminho_jogador).convert_alpha()
    imagem_obstaculo = pygame.image.load(caminho_obstaculo).convert_alpha()
    imagem_fundo = pygame.image.load(caminho_fundo).convert()

    TAMANHO_JOGADOR = LARGURA // 10
    TAMANHO_OBSTACULO = LARGURA // 12
    imagem_jogador = pygame.transform.scale(imagem_jogador, (TAMANHO_JOGADOR, TAMANHO_JOGADOR))
    imagem_obstaculo = pygame.transform.scale(imagem_obstaculo, (TAMANHO_OBSTACULO, TAMANHO_OBSTACULO))
    imagem_fundo = pygame.transform.scale(imagem_fundo, (LARGURA, ALTURA))

except pygame.error as e:
    print("\nERRO GRAVE: Não foi possível carregar uma ou mais imagens.")
    print(f"Verifique se os arquivos 'player.png', 'obstacle.png' e 'fundo.png' estão na pasta:")
    print(f"-> {pasta_do_jogo}")
    print(f"Detalhes do erro: {e}\n")
    pygame.quit()
    exit()

# --- Classe do Fundo ---
class Fundo(pygame.sprite.Sprite):
    def __init__(self, y_pos, velocidade):
        super().__init__()
        self.image = imagem_fundo
        self.rect = self.image.get_rect()
        self.rect.y = y_pos
        self.velocidade = velocidade

    def update(self):
        self.rect.y += self.velocidade
        if self.rect.y > ALTURA:
            self.rect.y = -ALTURA

# --- Classe do Jogador ---
class Jogador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = imagem_jogador
        self.rect = self.image.get_rect()
        self.rect.centerx = LARGURA // 2
        self.rect.bottom = ALTURA - 200
        self.velocidade_x = 0

    def update(self):
        self.rect.x += self.velocidade_x
        if self.rect.right > LARGURA:
            self.rect.right = LARGURA
        if self.rect.left < 0:
            self.rect.left = 0

# --- Classe do Obstáculo ---
class Obstaculo(pygame.sprite.Sprite):
    def __init__(self, velocidade_atual):
        super().__init__()
        self.image = imagem_obstaculo
        self.rect = self.image.get_rect()
        self.spawn(velocidade_atual)

    def spawn(self, base_speed):
        self.rect.x = random.randrange(LARGURA - self.rect.width)
        self.rect.y = random.randrange(-1000, -50)
        self.velocidade_y = base_speed + random.uniform(0.5, 2.5)

    def update(self):
        self.rect.y += self.velocidade_y
        if self.rect.top > ALTURA:
            self.kill()

# --- Funções de UI ---
def desenha_texto(superficie, texto, tamanho, x, y, cor=BRANCO):
    fonte = pygame.font.Font(None, tamanho)
    texto_superficie = fonte.render(texto, True, cor)
    texto_retangulo = texto_superficie.get_rect()
    texto_retangulo.midtop = (x, y)
    superficie.blit(texto_superficie, texto_retangulo)

def desenha_botao(superficie, texto, x, y, largura, altura, cor_fundo, cor_texto):
    botao_rect = pygame.Rect(x, y, largura, altura)
    pygame.draw.rect(superficie, cor_fundo, botao_rect, border_radius=10)
    fonte = pygame.font.Font(None, 40)
    texto_superficie = fonte.render(texto, True, cor_texto)
    texto_retangulo = texto_superficie.get_rect(center=botao_rect.center)
    superficie.blit(texto_superficie, texto_retangulo)
    return botao_rect

# --- Variáveis do jogo ---
placar = 0
melhor_placar = 0
relogio = pygame.time.Clock()
estado_jogo = "MENU"
FPS = 45
velocidade_base_fundo = 6
velocidade_jogador = 10
intervalo_spawn_inicial = 50 # Número de frames para o primeiro obstáculo
frames_desde_ultimo_obstaculo = 0

# --- Loop principal ---
rodando = True
while rodando:
    relogio.tick(FPS)
    
    # --- Estado MENU ---
    if estado_jogo == "MENU":
        tela.blit(imagem_fundo, (0, 0))
        desenha_texto(tela, "SpaceFox", 80, LARGURA // 2, ALTURA // 4)
        botao_start = desenha_botao(tela, "Começar", LARGURA // 2 - 125, ALTURA // 2, 250, 80, AZUL_CLARO, BRANCO)
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if botao_start.collidepoint(evento.pos):
                    jogador = Jogador()
                    fundo1 = Fundo(0, velocidade_base_fundo)
                    fundo2 = Fundo(-ALTURA, velocidade_base_fundo)
                    
                    todos_sprites = pygame.sprite.Group()
                    todos_sprites.add(fundo1, fundo2, jogador)
                    obstaculos = pygame.sprite.Group()
                    placar = 0
                    frames_desde_ultimo_obstaculo = 0
                    estado_jogo = "JOGANDO"
        
        pygame.display.flip()

    # --- Estado JOGANDO ---
    elif estado_jogo == "JOGANDO":
        largura_botao = LARGURA // 4
        altura_botao = LARGURA // 8
        espacamento = LARGURA // 4
        
        botao_esquerda = desenha_botao(tela, "Esquerda", espacamento - largura_botao // 2, ALTURA - 200, largura_botao, altura_botao, CINZA, PRETO)
        botao_direita = desenha_botao(tela, "Direita", LARGURA - espacamento - largura_botao // 2, ALTURA - 200, largura_botao, altura_botao, CINZA, PRETO)

        # Aumenta a velocidade do jogo a cada 50 pontos
        velocidade_atual = velocidade_base_fundo + (placar // 50) * 0.5
        
        # Diminui o intervalo de spawn com a dificuldade
        intervalo_spawn_obstaculos = max(30, intervalo_spawn_inicial - (placar // 50) * 2)

        # Lógica de spawn controlada
        frames_desde_ultimo_obstaculo += 1
        if frames_desde_ultimo_obstaculo >= intervalo_spawn_obstaculos:
            obst = Obstaculo(velocidade_atual)
            todos_sprites.add(obst)
            obstaculos.add(obst)
            frames_desde_ultimo_obstaculo = 0

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if botao_esquerda.collidepoint(evento.pos):
                    jogador.velocidade_x = -velocidade_jogador
                if botao_direita.collidepoint(evento.pos):
                    jogador.velocidade_x = velocidade_jogador
            if evento.type == pygame.MOUSEBUTTONUP:
                jogador.velocidade_x = 0
        
        todos_sprites.update()
        
        colisoes = pygame.sprite.spritecollide(jogador, obstaculos, True)
        if colisoes:
            estado_jogo = "GAME_OVER"
            if placar > melhor_placar:
                melhor_placar = placar
        
        placar += 1

        tela.fill(PRETO)
        todos_sprites.draw(tela)
        desenha_texto(tela, f"Pontos: {placar}", 30, LARGURA // 2, 20)
        
        desenha_botao(tela, "Esquerda", espacamento - largura_botao // 2, ALTURA - 200, largura_botao, altura_botao, CINZA, PRETO)
        desenha_botao(tela, "Direita", LARGURA - espacamento - largura_botao // 2, ALTURA - 200, largura_botao, altura_botao, CINZA, PRETO)

        pygame.display.flip()

    # --- Estado GAME_OVER ---
    elif estado_jogo == "GAME_OVER":
        tela.fill(PRETO)
        desenha_texto(tela, "Fim de Jogo!", 60, LARGURA // 2, ALTURA // 4)
        desenha_texto(tela, f"Sua Pontuação: {placar}", 40, LARGURA // 2, ALTURA // 2)
        if placar > melhor_placar:
            desenha_texto(tela, "Novo Recorde!", 30, LARGURA // 2, ALTURA // 2 + 50)
        desenha_texto(tela, f"Melhor Pontuação: {melhor_placar}", 40, LARGURA // 2, ALTURA // 2 + 100)
        
        botao_reiniciar = desenha_botao(tela, "Jogar Novamente", LARGURA // 2 - 125, ALTURA * 3 // 4, 250, 80, AZUL_CLARO, BRANCO)
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if botao_reiniciar.collidepoint(evento.pos):
                    estado_jogo = "MENU"
        
        pygame.display.flip()

pygame.quit()
