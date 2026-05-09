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

if __name__ == "__main__":
    loading() 
    selected_file = select_rom()
    print(f"Ви вибрали файл: {selected_file}")
    chip8 = Chip8()
    chip8.load_rom(selected_file) 
    for _ in range(20):
        chip8.cycle()

input("Натисніть Enter, щоб вийти...")