import random
import time
import sys
import pygame  # Бібліотека для малювання екрана та звуку

PRINT_DEBUG = True  # Встановіть в False, щоб вимкнути вивід відлагоджувальної інформації
pxl = "█" # Pixel (full block), пригодиться для виводу екрану в консоль (якщо потрібно)

def print_debug_info(info):
    if PRINT_DEBUG:
        print(info)

def loading():
    # ANSI кольори
    YELLOW = "\033[38;2;252;213;53m"
    GRAY = "\033[38;2;112;122;138m"
    CYAN = "\033[36m"
    RESET = "\033[0m"
    CLEAR = "\033[H\033[J" # Очистка екрана

    ansi_logo = """
██╗   ██╗ ██████╗███████╗██╗   ██╗███████╗
╚██╗ ██╔╝██╔════╝██╔════╝╚██╗ ██╔╝██╔════╝
 ╚████╔╝ ██║     ███████╗ ╚████╔╝ ███████╗
  ╚██╔╝  ██║     ╚════██║  ╚██╔╝  ╚════██║
   ██║   ╚██████╗███████║   ██║   ███████║
   ╚═╝    ╚═════╝╚══════╝   ╚═╝   ╚══════╝"""

    print(CLEAR)
    
    # 1. Ефект появи логотипу
    for line in ansi_logo.splitlines():
        print(f"{YELLOW}{line}{RESET}")
        time.sleep(0.05)

    print(f"\n{YELLOW}Yurii Code system (YCsys) © 2026. Код, що працює, а не існує.{RESET}")
    print(f"{GRAY}{'-' * 60}{RESET}\n")

    # 2. Анімація завантаження компонентів CHIP-8
    steps = [
        "Initializing CPU Registers (V0-VF)...",
        "Setting up 4KB Memory Map...",
        "Clearing Display Buffer (64x32)...",
        "Loading Fontset into Memory...",
        "Setting up Timers (Delay/Sound)...",
        "CHIP-8 Interpreter Ready."
    ]

    for i, step in enumerate(steps):
        # Імітація читання адрес пам'яті
        addr = hex(random.randint(0x200, 0xFFF)).upper()
        
        # Рядок прогресу
        progress = (i + 1) / len(steps)
        bar_length = 20
        filled = int(progress * bar_length)
        bar = f"{YELLOW}█{RESET}" * filled + f"{GRAY}░{RESET}" * (bar_length - filled)
        
        # Вивід (використовуємо \r щоб оновлювати один і той самий рядок)
        sys.stdout.write(f"\r{CYAN}[{addr}]{RESET} {step.ljust(40)} [{bar}] {int(progress*100)}%")
        sys.stdout.flush()
        
        time.sleep(random.uniform(0.3, 0.7)) # Рандомна затримка для реалізму

    print(f"\n\n{YELLOW}>> SYSTEM BOOT COMPLETE. RUNNING EMULATOR...{RESET}\n")
    time.sleep(0.5)

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
        # 1. Зчитування (це в тебе працює добре)
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
        print_debug_info(f"Зчитано команду: {hex(opcode)} (t={hex(t)}, x={hex(x)}, y={hex(y)}, n={hex(n)}, nn={hex(nn)}, nnn={hex(nnn)})")

        # 3. Логіка виконання (по одній команді за раз)
        
        if t == 0x0:
            if nnn == 0x0E0:
                # Очищення екрана
                self.display = [[0] * 32 for _ in range(64)]
                print_debug_info("Екран очищено")
            elif nnn == 0x0EE:
                # Повернення з підпрограми
                self.pc = self.stack.pop()
                print_debug_info("Повернення зі стеку")

        elif t == 0x1: # 1NNN: Стрибок на адресу NNN
            self.pc = nnn
            print_debug_info(f"Стрибок на {hex(nnn)}")

        elif t == 0x3: # 3XNN: Пропускати наступну команду, якщо Vx == NN
            if self.v_registers[x] == nn:
                self.pc += 2
                print_debug_info(f"Умова 3XNN виконана: V{x} == {hex(nn)}. Пропускаємо наступну команду.")
            else:
                print_debug_info(f"Умова 3XNN не виконана: V{x} != {hex(nn)}.")

        elif t == 0x4: # 4XNN: Пропускати наступну команду, якщо Vx != NN
            if self.v_registers[x] != nn:
                self.pc += 2
                print_debug_info(f"Умова 4XNN виконана: V{x} != {hex(nn)}. Пропускаємо наступну команду.")
            else:
                print_debug_info(f"Умова 4XNN не виконана: V{x} == {hex(nn)}.")
        
        elif t == 0x5: # 5XY0: Пропускати наступну команду, якщо Vx == Vy

            if n != 0:
                print_debug_info(f"Невідомий код команди: {hex(opcode)}. Пропускаємо.")
                print_debug_info(f"Очікувалося, що останній півбайт буде 0, але отримано {hex(n)}. Пропускаємо команду.")
                print_debug_info("Це може бути помилка в коді гри/емулятора. Пропускаємо виконання цієї команди.")

                return
            if self.v_registers[x] == self.v_registers[y]:
                self.pc += 2
                print_debug_info(f"Умова 5XY0 виконана: V{x} == V{y}. Пропускаємо наступну команду.")
            else:
                print_debug_info(f"Умова 5XY0 не виконана: V{x} != V{y}.")

        elif t == 0x6: # 6XNN: Встановити Vx = NN
            self.v_registers[x] = nn
            print_debug_info(f"V{x} встановлено в {hex(nn)}")

        elif t == 0x7: # 7XNN: Додати NN до Vx (без прапорця переносу)
            self.v_registers[x] = (self.v_registers[x] + nn) & 0xFF
            print_debug_info(f"До V{x} додано {hex(nn)}")

        elif t == 0x8: # Різні математичні та логічні операції між Vx та Vy, залежно від останнього півбайта (n)
            if n == 0x0: 
                # 8XY0: Присвоєння значення одного регістра іншому
                self.v_registers[x] = self.v_registers[y]
                print_debug_info(f"8XY0: V{x} скопійовано з V{y} (Значення: {hex(self.v_registers[x])})")

            elif n == 0x1:
                # 8XY1: Бітове АБО (якщо хоча б один біт = 1)
                self.v_registers[x] |= self.v_registers[y]
                print_debug_info(f"8XY1: V{x} = V{x} OR V{y} (Результат: {hex(self.v_registers[x])})")

            elif n == 0x2:
                # 8XY2: Бітове І (тільки якщо обидва біти = 1)
                self.v_registers[x] &= self.v_registers[y]
                print_debug_info(f"8XY2: V{x} = V{x} AND V{y} (Результат: {hex(self.v_registers[x])})")

            elif n == 0x3:
                # 8XY3: Бітове XOR (якщо біти різні)
                self.v_registers[x] ^= self.v_registers[y]
                print_debug_info(f"8XY3: V{x} = V{x} XOR V{y} (Результат: {hex(self.v_registers[x])})")

            elif n == 0x4:
                # 8XY4: Додавання з прапорцем переносу (Carry Flag)
                sum_val = self.v_registers[x] + self.v_registers[y]
                
                # Якщо сума > 255 (FF), встановлюємо VF = 1
                if sum_val > 0xFF:
                    self.v_registers[0xF] = 1
                else:
                    self.v_registers[0xF] = 0
                
                # Записуємо тільки молодші 8 біт (залишок від 256)
                self.v_registers[x] = sum_val & 0xFF
                print_debug_info(f"8XY4: V{x} += V{y}, Carry Flag (VF) = {self.v_registers[0xF]}")

            elif n == 0x5:
                # 8XY5: V[x] = V[x] - V[y]
                # 1. Визначаємо прапорець (VF) ДО віднімання
                if self.v_registers[x] >= self.v_registers[y]:
                    not_borrow = 1
                else:
                    not_borrow = 0
                
                # 2. Робимо віднімання
                result = self.v_registers[x] - self.v_registers[y]
                
                # 3. Записуємо результат (тримаємо в межах 0-255)
                self.v_registers[x] = result & 0xFF
                
                # 4. Оновлюємо прапорець
                self.v_registers[0xF] = not_borrow
                print_debug_info(f"8XY5: V{x} -= V{y}, NOT Borrow (VF) = {not_borrow}")

            elif n == 0x6:
                # 8XY6: Зсув вправо
                # Беремо найменший біт
                self.v_registers[0xF] = self.v_registers[x] & 0x1
                self.v_registers[x] >>= 1
                print_debug_info(f"8XY6: V{x} >>= 1, VF = {self.v_registers[0xF]}")

            elif n == 0xE:
                # 8XYE: Зсув вліво
                # Беремо найстарший біт (7-й біт)
                self.v_registers[0xF] = (self.v_registers[x] >> 7) & 0x1
                # Зсуваємо і відсікаємо зайве
                self.v_registers[x] = (self.v_registers[x] << 1) & 0xFF
                print_debug_info(f"8XYE: V{x} <<= 1, VF = {self.v_registers[0xF]}")

            elif n == 0x7:
                # 8XY7: Vx = Vy - Vx
                # 1. Визначаємо прапорець (якщо Vy >= Vx, то VF = 1)
                if self.v_registers[y] >= self.v_registers[x]:
                    flag = 1
                else:
                    flag = 0

                # 2. Обчислюємо результат
                result = self.v_registers[y] - self.v_registers[x]
                
                # 3. Записуємо результат у Vx
                self.v_registers[x] = result & 0xFF
                
                # 4. Присвоюємо прапорець регістру VF
                self.v_registers[0xF] = flag
                
                print_debug_info(f"8XY7: V{x} = V{y} - V{x}, VF = {flag}")
        elif t == 0x9: # 9XY0: Пропускати наступну команду, якщо Vx != Vy
            if n != 0:
                print_debug_info(f"Невідомий код команди: {hex(opcode)}. Пропускаємо.")
                print_debug_info(f"Очікувалося, що останній півбайт буде 0, але отримано {hex(n)}. Пропускаємо команду.")
                print_debug_info("Це може бути помилка в коді гри/емулятора. Пропускаємо виконання цієї команди.")

                return
            if self.v_registers[x] != self.v_registers[y]:
                self.pc += 2
                print_debug_info(f"Умова 9XY0 виконана: V{x} != V{y}. Пропускаємо наступну команду.")
            else:
                print_debug_info(f"Умова 9XY0 не виконана: V{x} == V{y}.")

        elif t == 0xA: # ANNN: I = NNN Це просто встановлення вказівника на дані
            self.index_register = nnn
            print_debug_info(f"I встановлено на {hex(nnn)}")

        elif t == 0xB: # BNNN: PC = NNN + V0 Процесор стрибає не просто на адресу nnn, а додає до неї значення з V0. Це такий собі «динамічний перехід»
            self.pc = (nnn + self.v_registers[0]) & 0xFFF
            print_debug_info(f"PC змінено на {hex((nnn + self.v_registers[0]) & 0xFFF)} (NNN + V0)")

        elif t == 0xC: # CXNN: Vx = rand() & NN random.randint(0, 255) дає нам випадковий байт, а маска & nn дозволяє грі контролювати діапазон цього хаосу. Без цієї команди Тетріс би завжди видавав однакові фігури.
            rand_val = random.randint(0, 255)
            self.v_registers[x] = rand_val & nn
            print_debug_info(f"V{x} встановлено в {hex(self.v_registers[x])} (рандом: {hex(rand_val)})")

        elif t == 0xD:
            # 1. Початкові координати (беремо остачу від ділення, щоб не вийти за екран)
            x_pos = self.v_registers[x] % 64
            y_pos = self.v_registers[y] % 32
            
            # 2. Скидаємо прапорець зіткнень VF в 0
            self.v_registers[0xF] = 0
            
            # 3. Цикл по рядках спрайта (n — це висота, яку ми витягли з opcode)
            for row in range(n):
                # Отримуємо байт спрайта з пам'яті
                sprite_byte = self.memory[self.index_register + row]
                
                # 4. Цикл по 8 бітах цього байта
                for col in range(8):
                    # Перевіряємо, чи поточний біт спрайта дорівнює 1
                    # (0x80 >> col) — це маска, яка рухається зліва направо по байту
                    if (sprite_byte & (0x80 >> col)) != 0:
                        
                        # Координати з урахуванням зміщення (row та col)
                        final_x = (x_pos + col) % 64
                        final_y = (y_pos + row) % 32
                        
                        # Перевіряємо на зіткнення: якщо на екрані вже є піксель (1)
                        if self.display[final_x][final_y] == 1:
                            self.v_registers[0xF] = 1 # Є зіткнення!
                        
                        # Малюємо через XOR (1 стає 0, 0 стає 1)
                        self.display[final_x][final_y] ^= 1
            
            print_debug_info(f"0xDXYN: Намальовано спрайт ({n} рядків) у позиції ({x_pos}, {y_pos}). VF={self.v_registers[0xF]}")

        elif t == 0xE: # EX9E, EXA1: Робота з клавіатурою
            # Отримуємо код клавіші з регістра Vx
            key_code = self.v_registers[x]

            if nn == 0x9E: # EX9E: Пропустити команду, якщо клавіша натиснута
                if self.keys[key_code] == 1:
                    self.pc += 2
                    print_debug_info(f"EX9E: Клавіша {hex(key_code)} натиснута. Skip.")
                else:
                    print_debug_info(f"EX9E: Клавіша {hex(key_code)} НЕ натиснута.")

            elif nn == 0xA1: # EXA1: Пропустити команду, якщо клавіша НЕ натиснута
                if self.keys[key_code] == 0:
                    self.pc += 2
                    print_debug_info(f"EXA1: Клавіша {hex(key_code)} вільна. Skip.")
                else:
                    print_debug_info(f"EXA1: Клавіша {hex(key_code)} натиснута.")

        elif t == 0xF: # Різні операції, залежно від останнього півбайта (nn)
            if nn == 0x07:
                self.v_registers[x] = self.delay_timer
                print_debug_info(f"FX07: V{x} отримав значення таймера затримки")
            
            elif nn == 0x15:
                self.delay_timer = self.v_registers[x]
                print_debug_info(f"FX15: Таймер затримки встановлено на V{x}")
            
            elif nn == 0x18:
                self.sound_timer = self.v_registers[x]
                print_debug_info(f"FX18: Звуковий таймер встановлено на V{x}")

            elif nn == 0x1E:
                self.index_register = (self.index_register + self.v_registers[x]) & 0xFFFF # зробив класичним додаванням, бо у Python числа "гумові", тому замість переповнення отримаю >= 0x10000
                print_debug_info(f"FX1E: I += V{x} ({self.v_registers[x]}). Нове значення I: {hex(self.index_register)}")

            elif nn == 0x29:
                # Беремо тільки молодші 4 біти (0-15), бо в наборі лише 16 символів
                character = self.v_registers[x] & 0x0F
                self.index_register = 0x50 + (character * 5)
                
                print_debug_info(f"FX29: Встановлено I на адресу шрифту для символу {hex(character)}: {hex(self.index_register)}")

            elif nn == 0x33:
                # FX33: BCD розкладання
                value = self.v_registers[x]
                self.memory[self.index_register] = value // 100          # Сотні
                self.memory[self.index_register + 1] = (value // 10) % 10 # Десятки
                self.memory[self.index_register + 2] = value % 10         # Одиниці
                print_debug_info(f"FX33: BCD для {value} -> {value//100}, {(value//10)%10}, {value%10}")

            elif nn == 0x55:
                # FX55: Dump регістрів V0...Vx (включно, тому x + 1)
                count = x + 1
                start = self.index_register
                self.memory[start : start + count] = self.v_registers[0 : count]
                print_debug_info(f"FX55: Збережено регістри V0-V{x} у пам'ять")

            elif nn == 0x65:
                # FX65: Load регістрів V0...Vx
                count = x + 1
                start = self.index_register
                self.v_registers[0 : count] = self.memory[start : start + count]
                print_debug_info(f"FX65: Завантажено регістри V0-V{x} з пам'яті")

def select_rom():
    # Функція для вибору ROM-файлу за допомогою діалогового вікна
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()  # Сховати головне вікно

    file_path = filedialog.askopenfilename(title="Виберіть ROM-файл", filetypes=[("All Files", "*.ch8")])
    return file_path

# Проведемо тест передаваного коду
if __name__ == "__main__":
    loading()  # Показуємо анімацію завантаження
    selected_file = select_rom()
    print(f"Ви вибрали файл: {selected_file}")
    chip8 = Chip8()
    chip8.load_rom(selected_file)  # selected_file - це шлях до вашого ROM-файлу
    # виконаємо 5 циклів для перевірки
    for _ in range(20):
        chip8.cycle()

input("Натисніть Enter, щоб вийти...")