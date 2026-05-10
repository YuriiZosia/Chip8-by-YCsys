import random
import time
import sys
import array
import pygame  # Бібліотека для малювання екрана та звуку

PRINT_DEBUG = False  # Вивід у консоль
DEBUG_IN_LOG_FILE = False  # Вивід у файл
LOG_FILE_NAME = "chip8_execution.log"

def print_debug_info(info):
    # 1. Вивід у термінал (якщо увімкнено)
    if PRINT_DEBUG:
        print(info)

    # 2. Запис у лог-файл (якщо увімкнено)
    if DEBUG_IN_LOG_FILE:
        try:
            # Відкриваємо файл у режимі 'a' (append), щоб дописувати в кінець
            with open(LOG_FILE_NAME, "a", encoding="utf-8") as f:
                timestamp = time.strftime("%H:%M:%S")
                f.write(f"[{timestamp}] {info}\n")
        except Exception as e:
            # Якщо виникла помилка доступу до файлу, просто виведемо її в консоль
            if PRINT_DEBUG:
                print(f"!! Помилка запису в лог: {e}")

def pygame_boot_screen(screen, clock, width, height):
    # Кольори YCsys (Cyberpunk / Retro)
    BG_COLOR = (10, 10, 15)       # Дуже темно-синій/сірий
    TEXT_COLOR = (0, 255, 100)    # Неоновий зелений
    HIGHLIGHT = (252, 213, 53)    # YCsys Жовтий
    BAR_BG = (40, 40, 50)         # Фон прогрес-бару
    
    # Шрифти (використовуємо стандартний моноширинний шрифт)
    pygame.font.init()
    font_large = pygame.font.SysFont("courier", 36, bold=True)
    font_small = pygame.font.SysFont("courier", 18)

    # Логотип (просто текст для стилістики)
    logo_text = "YCsys CHIP-8 BIOS v1.0"
    motto_text = "Код, що працює, а не існує."

    steps = [
        "Initializing CPU Registers...",
        "Setting up 4KB Memory Map...",
        "Clearing Display Buffer...",
        "Loading Fontset into 0x50...",
        "Establishing Pygame Video Link...",
        "SYSTEM READY."
    ]

    # Рендеримо статичний текст
    logo_surf = font_large.render(logo_text, True, HIGHLIGHT)
    motto_surf = font_small.render(motto_text, True, TEXT_COLOR)
    
    logo_rect = logo_surf.get_rect(center=(width//2, height//3))
    motto_rect = motto_surf.get_rect(center=(width//2, height//3 + 40))

    # Анімація завантаження
    for i, step in enumerate(steps):
        # Дозволяємо закрити вікно під час завантаження
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(BG_COLOR)
        
        # Малюємо лого
        screen.blit(logo_surf, logo_rect)
        screen.blit(motto_surf, motto_rect)

        # Малюємо поточний крок
        step_surf = font_small.render(f"> {step}", True, TEXT_COLOR)
        screen.blit(step_surf, (50, height//2 + 50))

        # Малюємо прогрес-бар
        progress = (i + 1) / len(steps)
        bar_width = width - 100
        bar_height = 20
        
        # Фон бару
        pygame.draw.rect(screen, BAR_BG, (50, height//2 + 80, bar_width, bar_height))
        # Заповнення бару
        pygame.draw.rect(screen, HIGHLIGHT, (50, height//2 + 80, bar_width * progress, bar_height))

        pygame.display.flip()
        
        # Рандомна затримка для "ефекту заліза"
        time.sleep(random.uniform(0.2, 0.6))

    time.sleep(0.5) # Пауза перед самим стартом

class Chip8:
    def __init__(self):
        # Пам'ять: 4096 комірок (4 КБ). Кожна комірка — 1 байт (0-255)
        # Це як склад, де лежить код гри та дані
        self.memory = [0] * 4096

        # Регістри: 16 штук (від V0 до VF). Кожен на 1 байт.
        # Це твій «блокнот на коліні» для швидких розрахунків
        self.v_registers = [0] * 16

        # Регістр адреси I: 2 байти. 
        # Використовується для зберігання адрес у пам'яті
        self.index_register = 0

        # Program Counter (PC): Вказівник на поточну команду.
        # Програми в CHIP-8 завжди починаються з адреси 0x200 (512 в десятковій)
        self.pc = 0x200

        # Екран: 64x32 пікселі. Кожен піксель або 0 (чорний), або 1 (білий)
        # Це двовимірний масив (сітка)
        self.display = [[0] * 32 for _ in range(64)]

        # Стек: Потрібен для запам'ятовування адрес повернення (якщо пішли в підпрограму)
        # Це як хлібні крихти, щоб знайти шлях назад
        self.stack = []

        # Стан клавіш: 16 кнопок (від 0 до F). 0 — відпущена, 1 — натиснута.
        self.keys = [0] * 16

        # Таймери: Затримка та звук. Зменшуються автоматично 60 разів на секунду
        self.delay_timer = 0
        self.sound_timer = 0

        # Стандартний шрифт CHIP-8 (80 байт)
        fontset = [
            0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
            0x20, 0x60, 0x20, 0x20, 0x70, # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
            0x90, 0x90, 0xF0, 0x10, 0x10, # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
            0xF0, 0x10, 0x20, 0x40, 0x40, # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90, # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
            0xF0, 0x80, 0x80, 0x80, 0xF0, # C
            0xE0, 0x90, 0x90, 0x90, 0xE0, # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
            0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        ]
        
        # Завантажуємо шрифт у самісінький початок пам'яті
        self.memory[0x50:0x50+len(fontset)] = fontset # використовуємо зріз для копіювання шрифту в пам'ять
        

    def load_rom(self, filename):
        with open(filename, "rb") as f:
            rom_data = f.read() # Зчитали один раз у змінну
            # пперевіримо чи розмір ROM не перевищує доступну пам'ять (від 0x200 до 0xFFF)
            if len(rom_data) > (0xFFF - 0x200 + 1):
                raise ValueError("ROM занадто великий для завантаження в пам'ять CHIP-8.")
            self.memory[0x200:0x200+len(rom_data)] = rom_data

    def cycle(self):
        # 1. Зчитування
        byte1 = self.memory[self.pc]
        byte2 = self.memory[self.pc + 1]
        opcode = (byte1 << 8) | byte2 # Об'єднуємо два байти в одну 16-бітну команду
        self.pc += 2

        # 2. Розбирання на запчастини
        t = (opcode >> 12) & 0xF  # & 0xF - це як маска, щоб отримати лише останні 4 біти
        x = (opcode >> 8) & 0xF
        y = (opcode >> 4) & 0xF
        n = opcode & 0xF          # 4 біти
        nn = opcode & 0x00FF      # 8 біт
        nnn = opcode & 0x0FFF     # 12 біт
        
        # Спеціальне форматування {x:X} виводить V10 як VA, V15 як VF
        print_debug_info(f"Зчитано команду: {hex(opcode)} (t={hex(t)}, x={hex(x)}, y={hex(y)}, n={hex(n)}, nn={hex(nn)}, nnn={hex(nnn)})")

        # 3. Логіка виконання (по одній команді за раз)
        
        if t == 0x0:
            if nnn == 0x0E0:
                # 00E0: Очищення екрана
                self.display = [[0] * 32 for _ in range(64)]
                print_debug_info("00E0: Екран очищено")
            elif nnn == 0x0EE:
                # 00EE: Повернення з підпрограми
                self.pc = self.stack.pop()
                print_debug_info(f"00EE: Повернення зі стеку на адресу {hex(self.pc)}")

        elif t == 0x1: # 1NNN: Стрибок на адресу NNN
            self.pc = nnn
            print_debug_info(f"1NNN: Стрибок на {hex(nnn)}")

        elif t == 0x2: # 2NNN: Виклик підпрограми (Додано!)
            self.stack.append(self.pc) # Зберігаємо поточну адресу повернення
            self.pc = nnn # Переходимо до підпрограми
            print_debug_info(f"2NNN: Виклик підпрограми за адресою {hex(nnn)}")

        elif t == 0x3: # 3XNN: Пропускати наступну команду, якщо Vx == NN
            if self.v_registers[x] == nn:
                self.pc += 2
                print_debug_info(f"3XNN виконано: V{x:X} == {hex(nn)}. Пропускаємо наступну команду.")
            else:
                print_debug_info(f"3XNN проігноровано: V{x:X} != {hex(nn)}.")

        elif t == 0x4: # 4XNN: Пропускати наступну команду, якщо Vx != NN
            if self.v_registers[x] != nn:
                self.pc += 2
                print_debug_info(f"4XNN виконано: V{x:X} != {hex(nn)}. Пропускаємо наступну команду.")
            else:
                print_debug_info(f"4XNN проігноровано: V{x:X} == {hex(nn)}.")
        
        elif t == 0x5: # 5XY0: Пропускати наступну команду, якщо Vx == Vy
            if n != 0:
                print_debug_info(f"Невідомий код команди: {hex(opcode)}. Пропускаємо.")
                return
            if self.v_registers[x] == self.v_registers[y]:
                self.pc += 2
                print_debug_info(f"5XY0 виконано: V{x:X} == V{y:X}. Пропускаємо наступну команду.")
            else:
                print_debug_info(f"5XY0 проігноровано: V{x:X} != V{y:X}.")

        elif t == 0x6: # 6XNN: Встановити Vx = NN
            self.v_registers[x] = nn
            print_debug_info(f"6XNN: V{x:X} встановлено в {hex(nn)}")

        elif t == 0x7: # 7XNN: Додати NN до Vx (без прапорця переносу)
            self.v_registers[x] = (self.v_registers[x] + nn) & 0xFF
            print_debug_info(f"7XNN: До V{x:X} додано {hex(nn)}")

        elif t == 0x8: # Математичні та логічні операції
            if n == 0x0: 
                self.v_registers[x] = self.v_registers[y]
                print_debug_info(f"8XY0: V{x:X} скопійовано з V{y:X} (Значення: {hex(self.v_registers[x])})")
            elif n == 0x1:
                self.v_registers[x] |= self.v_registers[y]
                print_debug_info(f"8XY1: V{x:X} |= V{y:X} (Результат: {hex(self.v_registers[x])})")
            elif n == 0x2:
                self.v_registers[x] &= self.v_registers[y]
                print_debug_info(f"8XY2: V{x:X} &= V{y:X} (Результат: {hex(self.v_registers[x])})")
            elif n == 0x3:
                self.v_registers[x] ^= self.v_registers[y]
                print_debug_info(f"8XY3: V{x:X} ^= V{y:X} (Результат: {hex(self.v_registers[x])})")
            elif n == 0x4:
                sum_val = self.v_registers[x] + self.v_registers[y]
                self.v_registers[0xF] = 1 if sum_val > 0xFF else 0
                self.v_registers[x] = sum_val & 0xFF
                print_debug_info(f"8XY4: V{x:X} += V{y:X}, Carry Flag (VF) = {self.v_registers[0xF]}")
            elif n == 0x5:
                not_borrow = 1 if self.v_registers[x] >= self.v_registers[y] else 0
                self.v_registers[x] = (self.v_registers[x] - self.v_registers[y]) & 0xFF
                self.v_registers[0xF] = not_borrow
                print_debug_info(f"8XY5: V{x:X} -= V{y:X}, NOT Borrow (VF) = {not_borrow}")
            elif n == 0x6:
                self.v_registers[0xF] = self.v_registers[x] & 0x1
                self.v_registers[x] >>= 1
                print_debug_info(f"8XY6: V{x:X} >>= 1, VF = {self.v_registers[0xF]}")
            elif n == 0xE:
                self.v_registers[0xF] = (self.v_registers[x] >> 7) & 0x1
                self.v_registers[x] = (self.v_registers[x] << 1) & 0xFF
                print_debug_info(f"8XYE: V{x:X} <<= 1, VF = {self.v_registers[0xF]}")
            elif n == 0x7:
                flag = 1 if self.v_registers[y] >= self.v_registers[x] else 0
                self.v_registers[x] = (self.v_registers[y] - self.v_registers[x]) & 0xFF
                self.v_registers[0xF] = flag
                print_debug_info(f"8XY7: V{x:X} = V{y:X} - V{x:X}, VF = {flag}")

        elif t == 0x9: # 9XY0: Пропускати наступну команду, якщо Vx != Vy
            if n != 0: return
            if self.v_registers[x] != self.v_registers[y]:
                self.pc += 2
                print_debug_info(f"9XY0 виконано: V{x:X} != V{y:X}. Пропускаємо наступну команду.")

        elif t == 0xA: # ANNN: I = NNN
            self.index_register = nnn
            print_debug_info(f"ANNN: I встановлено на {hex(nnn)}")

        elif t == 0xB: # BNNN: PC = NNN + V0
            self.pc = (nnn + self.v_registers[0]) & 0xFFF
            print_debug_info(f"BNNN: PC змінено на {hex(self.pc)}")

        elif t == 0xC: # CXNN: Vx = rand() & NN
            rand_val = random.randint(0, 255)
            self.v_registers[x] = rand_val & nn
            print_debug_info(f"CXNN: V{x:X} встановлено в {hex(self.v_registers[x])} (рандом: {hex(rand_val)})")

        elif t == 0xD: # DXYN: Малювання
            x_pos = self.v_registers[x] % 64
            y_pos = self.v_registers[y] % 32
            self.v_registers[0xF] = 0
            for row in range(n):
                sprite_byte = self.memory[self.index_register + row]
                for col in range(8):
                    if (sprite_byte & (0x80 >> col)) != 0:
                        final_x = (x_pos + col) % 64
                        final_y = (y_pos + row) % 32
                        if self.display[final_x][final_y] == 1:
                            self.v_registers[0xF] = 1 
                        self.display[final_x][final_y] ^= 1
            print_debug_info(f"DXYN: Намальовано спрайт ({n} рядків) у ({x_pos}, {y_pos}). VF={self.v_registers[0xF]}")

        elif t == 0xE: # Клавіатура
            key_code = self.v_registers[x]
            if nn == 0x9E:
                if self.keys[key_code] == 1:
                    self.pc += 2
                    print_debug_info(f"EX9E: Клавіша {hex(key_code)} натиснута. Skip.")
            elif nn == 0xA1:
                if self.keys[key_code] == 0:
                    self.pc += 2
                    print_debug_info(f"EXA1: Клавіша {hex(key_code)} вільна. Skip.")

        elif t == 0xF: # Таймери та Утиліти
            if nn == 0x07:
                self.v_registers[x] = self.delay_timer
                print_debug_info(f"FX07: V{x:X} отримав значення таймера затримки ({self.delay_timer})")
            
            elif nn == 0x0A: # FX0A: Очікування натискання клавіші (Додано!)
                pressed = False
                for i in range(16):
                    if self.keys[i] == 1:
                        self.v_registers[x] = i
                        pressed = True
                        break
                if not pressed:
                    self.pc -= 2 # Якщо нічого не натиснуто, процесор "топчеться" на місці
                else:
                    print_debug_info(f"FX0A: Клавіша {hex(self.v_registers[x])} натиснута, збережено у V{x:X}")

            elif nn == 0x15:
                self.delay_timer = self.v_registers[x]
                print_debug_info(f"FX15: Таймер затримки встановлено на {self.delay_timer}")
            
            elif nn == 0x18:
                self.sound_timer = self.v_registers[x]
                print_debug_info(f"FX18: Звуковий таймер встановлено на {self.sound_timer}")

            elif nn == 0x1E:
                self.index_register = (self.index_register + self.v_registers[x]) & 0xFFFF
                print_debug_info(f"FX1E: I += V{x:X}. Нове значення I: {hex(self.index_register)}")

            elif nn == 0x29:
                character = self.v_registers[x] & 0x0F
                self.index_register = 0x50 + (character * 5)
                print_debug_info(f"FX29: I вказує на шрифт символу {hex(character)} (адреса {hex(self.index_register)})")

            elif nn == 0x33:
                value = self.v_registers[x]
                self.memory[self.index_register] = value // 100
                self.memory[self.index_register + 1] = (value // 10) % 10
                self.memory[self.index_register + 2] = value % 10
                print_debug_info(f"FX33: BCD для {value} -> {value//100}, {(value//10)%10}, {value%10}")

            elif nn == 0x55:
                count = x + 1
                start = self.index_register
                self.memory[start : start + count] = self.v_registers[0 : count]
                print_debug_info(f"FX55: Збережено регістри V0-V{x:X} у пам'ять")

            elif nn == 0x65:
                count = x + 1
                start = self.index_register
                self.v_registers[0 : count] = self.memory[start : start + count]
                print_debug_info(f"FX65: Завантажено регістри V0-V{x:X} з пам'яті")

def select_rom():
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw() 
    file_path = filedialog.askopenfilename(title="Виберіть ROM-файл", filetypes=[("All Files", "*.ch8")])
    return file_path

def generate_cyberpunk_beep():
    # Математична генерація звуку (Square wave 440 Hz)
    sample_rate = 44100
    duration = 0.1  # Довжина одного "біпу"
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)
    
    for i in range(n_samples):
        # Робимо трохи агресивний, різкий звук (електронний)
        if int((float(i) / sample_rate) * 440 * 2) % 2 == 0:
            buf[i] = 16383
        else:
            buf[i] = -16384
            
    return pygame.mixer.Sound(buf)

if __name__ == "__main__":
    # Ініціалізація графіки та звуку
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=1)
    beep_sound = generate_cyberpunk_beep()
    beep_sound.play() # Тестовий гудок системи!

    SCALE = 15
    WIDTH = 64 * SCALE
    UI_WIDTH = 120  # Зменшена ширина панелі
    HEIGHT = 32 * SCALE
    paused = False  # Змінна стану для паузи
    
    screen = pygame.display.set_mode((WIDTH + UI_WIDTH, HEIGHT))
    pygame.display.set_caption("YCsys CHIP-8 [CYBERPUNK EDITION]")
    clock = pygame.time.Clock()

    # Запускаємо завантажувальний екран YCsys
    pygame_boot_screen(screen, clock, WIDTH + UI_WIDTH, HEIGHT)

    selected_file = select_rom()
    if not selected_file:
        print("Вихід із системи.")
        pygame.quit()
        sys.exit()

    chip8 = Chip8()
    chip8.load_rom(selected_file) 

    KEY_MAP = {
        pygame.K_1: 0x1, pygame.K_2: 0x2, pygame.K_3: 0x3, pygame.K_4: 0xC,
        pygame.K_q: 0x4, pygame.K_w: 0x5, pygame.K_e: 0x6, pygame.K_r: 0xD,
        pygame.K_a: 0x7, pygame.K_s: 0x8, pygame.K_d: 0x9, pygame.K_f: 0xE,
        pygame.K_z: 0xA, pygame.K_x: 0x0, pygame.K_c: 0xB, pygame.K_v: 0xF
    }

    # КІБЕРПАНК КОЛЬОРИ
    BG_COLOR = (10, 5, 20)          # Темний фіолетово-чорний фон
    CORE_COLOR = (0, 255, 255)      # Неоновий Cyan (серцевина пікселя)
    GLOW_COLOR = (0, 100, 255)      # Синє світіння

    # Поверхня для ефекту згасання (Trails/Motion Blur)
    trail_surface = pygame.Surface((WIDTH, HEIGHT))
    trail_surface.fill(BG_COLOR)
    trail_surface.set_alpha(65)     # Чим менше число, тим довший слід залишається

    # Шрифт для інформації (ініціалізуємо один раз перед циклом)
    font_debug = pygame.font.SysFont("courier", 18, bold=True)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key in KEY_MAP:
                    chip8.keys[KEY_MAP[event.key]] = 1
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                # Обробка паузи на клавішу пробілу
                if event.key == pygame.K_SPACE:
                    paused = not paused
                    status = "ПАУЗА" if paused else "ГРА"
                    print_debug_info(f">> Стан системи: {status}")

                # Обробка перезавантаження на Backspace
                if event.key == pygame.K_BACKSPACE:
                    print_debug_info(">> ПЕРЕЗАВАНТАЖЕННЯ СИСТЕМИ <<")
                    chip8 = Chip8()               # Створюємо чистий процесор
                    chip8.load_rom(selected_file) # Завантажуємо ту ж саму гру
                    paused = False                # Знімаємо з паузи
            
            if event.type == pygame.KEYUP:
                if event.key in KEY_MAP:
                    chip8.keys[KEY_MAP[event.key]] = 0

        # Виконуємо логіку процесора ТІЛЬКИ якщо не на паузі
        if not paused:
            # Швидкість гри (10 інструкцій на кадр)
            for _ in range(10): 
                chip8.cycle()

            # Робота таймерів
            if chip8.delay_timer > 0:
                chip8.delay_timer -= 1
                
            if chip8.sound_timer > 0:
                # Якщо таймер звуку активний і звук ще не грає — запускаємо біп
                if not pygame.mixer.get_busy():
                    beep_sound.play()
                chip8.sound_timer -= 1

        # --- РЕНДЕРИНГ КІБЕРПАНКУ ---
        
        # 1. Ефект "шлейфу". Замість screen.fill ми накладаємо напівпрозорий фон
        screen.blit(trail_surface, (0, 0))

        # 2. Малювання пікселів зі світінням
        for x in range(64):
            for y in range(32):
                if chip8.display[x][y] == 1:
                    pos_x = x * SCALE
                    pos_y = y * SCALE
                    
                    # Малюємо ауру світіння
                    pygame.draw.rect(screen, GLOW_COLOR, (pos_x - 2, pos_y - 2, SCALE + 4, SCALE + 4), border_radius=4)
                    
                    # Малюємо яскраву серцевину пікселя
                    pygame.draw.rect(screen, CORE_COLOR, (pos_x + 1, pos_y + 1, SCALE - 2, SCALE - 2), border_radius=2)

        # 3. Ефект Сканлайнів (Scanlines)
        for y_line in range(0, HEIGHT, 4):
            pygame.draw.line(screen, (0, 0, 0), (0, y_line), (WIDTH, y_line), 1)

        # --- РЕНДЕРИНГ DEBUG ПАНЕЛІ (YCsys UI) ---
        
        # Замальовуємо фон панелі
        pygame.draw.rect(screen, (20, 20, 30), (WIDTH, 0, UI_WIDTH, HEIGHT))
        # Розділювальна лінія
        pygame.draw.line(screen, (0, 255, 100), (WIDTH, 0), (WIDTH, HEIGHT), 2) 

        # Виводимо регістри V0 - VF
        for i in range(16):
            val = chip8.v_registers[i]
            # Форматуємо рядок: V0:00
            text_surf = font_debug.render(f"V{i:X}:{val:02X}", True, (0, 255, 255))
            screen.blit(text_surf, (WIDTH + 10, 10 + (i * 20)))

        # Вивід PC
        pc_surf = font_debug.render(f"PC:{chip8.pc:03X}", True, (252, 213, 53))
        screen.blit(pc_surf, (WIDTH + 10, HEIGHT - 50))

        # Вивід Index Register
        idx_surf = font_debug.render(f"I: {chip8.index_register:03X}", True, (252, 213, 53))
        screen.blit(idx_surf, (WIDTH + 10, HEIGHT - 30))

        # Вивід на екран
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()