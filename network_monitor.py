import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque
import threading
import time
import random
import socket
import platform
from datetime import datetime

class SimpleNetMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Простой монитор сети")
        self.root.geometry("800x600")
        
        # Данные
        self.active = False
        self.data = {
            'times': deque(maxlen=50),
            'download': deque(maxlen=50),
            'upload': deque(maxlen=50)
        }
        
        self.stats = {
            'total_dl': 0,
            'total_ul': 0,
            'current_dl': 0,
            'current_ul': 0
        }
        
        self.setup_ui()
        self.update_clock()
    
    def setup_ui(self):
        # Верхняя панель
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        self.status_label = ttk.Label(top_frame, text="Готов", font=('Arial', 10))
        self.status_label.pack(side=tk.LEFT)
        
        self.time_label = ttk.Label(top_frame, text="00:00:00", font=('Arial', 10))
        self.time_label.pack(side=tk.RIGHT)
        
        # Кнопки управления
        btn_frame = ttk.Frame(self.root, padding="10")
        btn_frame.pack(fill=tk.X)
        
        self.start_btn = ttk.Button(btn_frame, text="Начать мониторинг", 
                                   command=self.start_monitoring, width=20)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="Остановить", 
                                  command=self.stop_monitoring, 
                                  state=tk.DISABLED, width=20)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # График
        graph_frame = ttk.LabelFrame(self.root, text="Сетевой трафик", padding="10")
        graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Статистика
        stats_frame = ttk.Frame(self.root)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 4 колонки статистики
        stats = [
            ("Всего скачано:", "total_dl"),
            ("Всего отправлено:", "total_ul"),
            ("Текущая скорость DL:", "current_dl"),
            ("Текущая скорость UL:", "current_ul")
        ]
        
        for i, (text, key) in enumerate(stats):
            frame = ttk.LabelFrame(stats_frame, text=text, padding="5")
            frame.grid(row=0, column=i, padx=5, sticky=(tk.W, tk.E))
            
            self.stats[key + "_label"] = ttk.Label(frame, text="0", font=('Arial', 12))
            self.stats[key + "_label"].pack()
            
            unit = " KB" if "speed" not in text else " KB/s"
            ttk.Label(frame, text=unit).pack()
        
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(2, weight=1)
        stats_frame.columnconfigure(3, weight=1)
        
        # Протоколы
        proto_frame = ttk.LabelFrame(self.root, text="Имитация протоколов", padding="10")
        proto_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.proto_vars = {}
        protocols = ['HTTP (80)', 'HTTPS (443)', 'FTP (21)', 'Другие']
        
        for i, proto in enumerate(protocols):
            ttk.Label(proto_frame, text=proto, width=15).grid(row=0, column=i*2, padx=5)
            self.proto_vars[proto] = tk.StringVar(value="0%")
            ttk.Label(proto_frame, textvariable=self.proto_vars[proto], 
                     width=10).grid(row=0, column=i*2+1, padx=5)
    
    def start_monitoring(self):
        if not self.active:
            self.active = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Мониторинг активен", foreground="green")
            
            # Запуск потока мониторинга
            thread = threading.Thread(target=self.monitor_network)
            thread.daemon = True
            thread.start()
    
    def stop_monitoring(self):
        self.active = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Остановлено", foreground="red")
    
    def monitor_network(self):
        """Основной цикл мониторинга"""
        while self.active:
            try:
                # Имитация сетевой активности
                current_time = datetime.now().strftime("%H:%M:%S")
                
                # Генерируем случайные значения трафика
                download = random.randint(10, 1000)  # КБ/с
                upload = random.randint(5, 500)      # КБ/с
                
                # Обновляем статистику
                self.stats['total_dl'] += download
                self.stats['total_ul'] += upload
                self.stats['current_dl'] = download
                self.stats['current_ul'] = upload
                
                # Добавляем данные для графика
                self.data['times'].append(current_time)
                self.data['download'].append(download)
                self.data['upload'].append(upload)
                
                # Обновляем протоколы
                self.update_protocols()
                
                # Обновляем GUI
                self.root.after(0, self.update_display)
                
                # Пауза
                time.sleep(1)
                
            except Exception as e:
                print(f"Ошибка мониторинга: {e}")
                time.sleep(1)
    
    def update_protocols(self):
        """Обновление имитации протоколов"""
        total = sum([self.stats['current_dl'], self.stats['current_ul']])
        if total > 0:
            # Распределяем по протоколам
            http_pct = random.randint(30, 50)
            https_pct = random.randint(30, 50)
            ftp_pct = random.randint(1, 5)
            other_pct = 100 - http_pct - https_pct - ftp_pct
            
            self.proto_vars['HTTP (80)'].set(f"{http_pct}%")
            self.proto_vars['HTTPS (443)'].set(f"{https_pct}%")
            self.proto_vars['FTP (21)'].set(f"{ftp_pct}%")
            self.proto_vars['Другие'].set(f"{other_pct}%")
    
    def update_display(self):
        """Обновление всего отображения"""
        # Обновляем статистику
        self.stats['total_dl_label'].config(text=f"{self.stats['total_dl']:,}")
        self.stats['total_ul_label'].config(text=f"{self.stats['total_ul']:,}")
        self.stats['current_dl_label'].config(text=f"{self.stats['current_dl']}")
        self.stats['current_ul_label'].config(text=f"{self.stats['current_ul']}")
        
        # Обновляем график
        self.update_graph()
    
    def update_graph(self):
        """Обновление графика"""
        self.ax.clear()
        
        times = list(self.data['times'])
        download = list(self.data['download'])
        upload = list(self.data['upload'])
        
        if times and download and upload:
            # Ограничиваем количество точек для читаемости
            if len(times) > 20:
                display_times = times[-20:]
                display_dl = download[-20:]
                display_ul = upload[-20:]
            else:
                display_times = times
                display_dl = download
                display_ul = upload
            
            # Рисуем графики
            self.ax.plot(display_times, display_dl, 'g-', linewidth=2, label='Скачивание')
            self.ax.plot(display_times, display_ul, 'r-', linewidth=2, label='Отправка')
            
            # Настройки графика
            self.ax.set_xlabel('Время')
            self.ax.set_ylabel('Скорость (KB/s)')
            self.ax.set_title('Сетевой трафик в реальном времени')
            self.ax.legend()
            self.ax.grid(True, alpha=0.3)
            
            # Поворачиваем метки времени
            if len(display_times) > 5:
                plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45)
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    def update_clock(self):
        """Обновление времени"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_clock)

def main():
    root = tk.Tk()
    app = SimpleNetMonitor(root)
    root.mainloop()

if __name__ == "__main__":
    main()