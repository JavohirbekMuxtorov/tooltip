import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
import keyboard
import win32clipboard
import win32gui
import win32api
import win32con
import time
import urllib.request
import os
import threading

class SelectionTooltip:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.tooltip = tk.Toplevel(self.root)
        self.tooltip.withdraw()
        self.tooltip.overrideredirect(True)
        self.tooltip.attributes("-topmost", True)
        
        self.label = ttk.Label(
            self.tooltip, 
            padding=5,
            background='#FFFFDD',
            wraplength=300,
            font=('Arial', 10)
        )
        self.label.pack()
        
        self.show_time = None
        self.display_duration = 2  # Tooltip display time
        self.qa_pairs = self.load_qa_from_url()
        self.is_enabled = True  # Tooltip enabled flag
    
    def load_qa_from_url(self):
        try:
            url = "https://raw.githubusercontent.com/JavohirbekMuxtorov/tooltip/refs/heads/main/answer.txt"
            response = urllib.request.urlopen(url)
            data = response.read().decode('utf-8')
            
            qa_pairs = []
            current_qa = None
            
            for line in data.split('\n'):
                line = line.strip()
                if line and not '====' in line:
                    if '+++++' in line:
                        if current_qa:
                            qa_pairs.append(current_qa)
                        current_qa = None
                    else:
                        if not current_qa:
                            current_qa = {"question": line, "answers": []}
                        else:
                            current_qa["answers"].append(line)
            
            if current_qa:
                qa_pairs.append(current_qa)
            
            print("Successfully loaded answers from server")
            return qa_pairs
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading answers from server: {e}")
            return []
    
    def find_answer(self, selected_text):
        for qa in self.qa_pairs:
            if selected_text.lower() in qa["question"].lower():
                correct_answers = [ans[1:].strip() for ans in qa["answers"] if ans.startswith("#")]
                if correct_answers:
                    return "\n".join(correct_answers)
        return None
    
    def get_selected_text(self):
        try:
            keyboard.press_and_release("ctrl+c")
            time.sleep(0.1)
            text = pyperclip.paste()
            return text.strip() if text else None
        except:
            return None
    
    def show_tooltip(self, text):
        self.label.config(text=text)
        self.tooltip.deiconify()
        self.update_tooltip_position()
        self.show_time = time.time()
    
    def update_tooltip_position(self):
        x = self.root.winfo_pointerx()
        y = self.root.winfo_pointery()
        self.tooltip.geometry(f'+{x+15}+{y+10}')
    
    def hide_tooltip(self):
        self.tooltip.withdraw()
    
    def check_toggle_state(self):
        if keyboard.is_pressed('q'):
            print("Exiting program...")
            self.root.quit()
            exit()
        
        if keyboard.is_pressed('caps lock'):
            self.is_enabled = not self.is_enabled
            print("Tooltip toggled", "ON" if self.is_enabled else "OFF")
            time.sleep(0.3)
    
    def run(self):
        if not self.qa_pairs:
            messagebox.showerror("Error", "No answers loaded. Program will exit.")
            return
        
        last_selection = None
        tooltip_visible = False
        
        print("Running... Select text to see answer!")
        print("Press CAPS LOCK to toggle tooltip, Q to exit")
        
        while True:
            try:
                self.check_toggle_state()
                
                if self.is_enabled:
                    current_selection = self.get_selected_text()
                    current_time = time.time()
                    
                    if current_selection and current_selection != last_selection:
                        answer = self.find_answer(current_selection)
                        if answer:
                            self.show_tooltip(answer)
                            tooltip_visible = True
                            self.show_time = current_time
                            last_selection = current_selection
                    
                    if tooltip_visible and self.show_time:
                        if current_time - self.show_time >= self.display_duration:
                            self.hide_tooltip()
                            tooltip_visible = False
                            self.show_time = None
                            last_selection = None
                
                self.root.update()
                time.sleep(0.1)
                
            except tk.TclError:
                break
            except KeyboardInterrupt:
                break

if __name__ == "__main__":
    try:
        app = SelectionTooltip()
        app.run()
    except KeyboardInterrupt:
        print("\nExiting...")
