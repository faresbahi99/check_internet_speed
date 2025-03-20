import speedtest as st
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from ttkthemes import ThemedStyle
import threading
import matplotlib.pyplot as plt
import json
import csv
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import gettext
import customtkinter as ctk


class SpeedTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Internet Speed Test")
        self.root.geometry("500x500")
        self.root.resizable(True, True)

        self.style = ThemedStyle(self.root)
        self.style.set_theme("equilux")

        self.test_results = []
        self.selected_server = None
        self.stop_test = False
        self.current_language = "en"
        self.init_ui()
        self.init_internationalization()

    def init_ui(self):
        self.frame = ctk.CTkFrame(self.root)
        self.frame.pack(expand=True, fill="both", padx=20, pady=20)

        self.title_label = ctk.CTkLabel(self.frame, text="Internet Speed Test", font=("Arial", 20, "bold"), text_color="#FFD700")
        self.title_label.pack(pady=10)

        self.start_button = ctk.CTkButton(self.frame, text="Start Test", command=self.start_test)
        self.start_button.pack(pady=10)

        self.stop_button = ctk.CTkButton(self.frame, text="Stop Test", command=self.stop_test)
        self.stop_button.pack(pady=5)

        self.server_button = ctk.CTkButton(self.frame, text="Select Server", command=self.select_server)
        self.server_button.pack(pady=5)

        self.down_speed_label = ctk.CTkLabel(self.frame, text="Download Speed: N/A", font=("Arial", 12))
        self.down_speed_label.pack(pady=5)

        self.up_speed_label = ctk.CTkLabel(self.frame, text="Upload Speed: N/A", font=("Arial", 12))
        self.up_speed_label.pack(pady=5)

        self.ping_label = ctk.CTkLabel(self.frame, text="Ping: N/A", font=("Arial", 12))
        self.ping_label.pack(pady=5)

        self.ip_label = ctk.CTkLabel(self.frame, text="IP: N/A", font=("Arial", 12))
        self.ip_label.pack(pady=5)

        self.progress_bar = ctk.CTkProgressBar(self.frame, mode='indeterminate', width=300)
        self.progress_bar.pack(pady=10)

        self.export_button = ctk.CTkButton(self.frame, text="Export CSV", command=self.export_csv)
        self.export_button.pack(pady=5)

        self.share_button = ctk.CTkButton(self.frame, text="Share Results", command=self.share_results_social)
        self.share_button.pack(pady=5)

        self.theme_button = ctk.CTkButton(self.frame, text="Toggle Theme", command=self.toggle_theme)
        self.theme_button.pack(pady=5)

        self.language_frame = ctk.CTkFrame(self.frame)
        self.language_frame.pack(pady=10)
        ctk.CTkButton(self.language_frame, text="English", command=lambda: self.change_language("en")).pack(side="left", padx=5)
        ctk.CTkButton(self.language_frame, text="العربية", command=lambda: self.change_language("ar")).pack(side="left", padx=5)
        ctk.CTkButton(self.language_frame, text="Français", command=lambda: self.change_language("fr")).pack(side="left", padx=5)

        plt.ion()
        self.fig = plt.figure()

    def init_internationalization(self):
        gettext.bindtextdomain("base", localedir="locales")
        gettext.textdomain("base")
        self._ = gettext.gettext

    def change_language(self, lang):
        self.current_language = lang
        gettext.bindtextdomain("base", localedir="locales")
        gettext.textdomain("base")
        self._ = gettext.gettext
        self.update_ui_texts()

    def update_ui_texts(self):
        self.title_label.configure(text=self._("Internet Speed Test"))
        self.start_button.configure(text=self._("Start Test"))
        self.stop_button.configure(text=self._("Stop Test"))
        self.server_button.configure(text=self._("Select Server"))
        self.down_speed_label.configure(text=self._("Download Speed: N/A"))
        self.up_speed_label.configure(text=self._("Upload Speed: N/A"))
        self.ping_label.configure(text=self._("Ping: N/A"))
        self.ip_label.configure(text=self._("IP: N/A"))
        self.export_button.configure(text=self._("Export CSV"))
        self.share_button.configure(text=self._("Share Results"))
        self.theme_button.configure(text=self._("Toggle Theme"))

    def start_test(self):
        self.down_speed_label.configure(text=self._("Testing download speed..."), text_color="black")
        self.up_speed_label.configure(text=self._("Testing upload speed..."), text_color="black")
        self.ping_label.configure(text=self._("Testing ping..."), text_color="black")
        self.progress_bar.start()
        threading.Thread(target=self.speed_test, daemon=True).start()

    def speed_test(self):
        try:
            test = st.Speedtest()
            if self.selected_server:
                test.get_servers([self.selected_server])
            else:
                test.get_best_server()

            down_speed = round(test.download() / 10**6, 2)
            up_speed = round(test.upload() / 10**6, 2)
            ping = test.results.ping
            ip, isp, city, country = self.get_ip_info()

            self.down_speed_label.configure(text=self._("Download Speed: {} Mbps").format(down_speed), text_color="#4CAF50")
            self.up_speed_label.configure(text=self._("Upload Speed: {} Mbps").format(up_speed), text_color="#2196F3")
            self.ping_label.configure(text=self._("Ping: {} ms").format(ping), text_color="#FF5722")
            self.ip_label.configure(text=self._("IP: {} | ISP: {} ({}, {})").format(ip, isp, city, country), text_color="#8E44AD")

            self.test_results.append((down_speed, up_speed, ping))
            self.root.after(100, self.update_graph)
            self.save_results()

            self.progress_bar.stop()
            self.progress_bar.set(1.0)
            self.root.after(2000, lambda: self.progress_bar.set(0.0))

            messagebox.showinfo(self._("Test Complete"), self._("Speed test completed successfully!"))
        except st.ConfigRetrievalError:
            messagebox.showerror(self._("Error"), self._("Failed to retrieve speedtest configuration. Check your internet connection."))
        except Exception as e:
            messagebox.showerror(self._("Error"), self._("An error occurred: {}").format(str(e)))

    def stop_test(self):
        self.stop_test = True
        self.progress_bar.stop()
        messagebox.showinfo(self._("Test Stopped"), self._("Speed test stopped by the user."))

    def update_graph(self):
        plt.clf()
        plt.plot([x[0] for x in self.test_results], label=self._("Download Speed (Mbps)"), marker='o', linestyle='-')
        plt.plot([x[1] for x in self.test_results], label=self._("Upload Speed (Mbps)"), marker='s', linestyle='-')
        plt.xlabel(self._("Test Number"))
        plt.ylabel(self._("Speed (Mbps)"))
        plt.legend()
        plt.title(self._("Internet Speed Test Results"))
        plt.draw()
        plt.pause(0.1)

    def save_results(self):
        with open("speed_results.json", "w") as file:
            json.dump(self.test_results, file)

    def export_csv(self):
        with open("speed_results.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([self._("Download Speed (Mbps)"), self._("Upload Speed (Mbps)"), self._("Ping (ms)")])
            writer.writerows(self.test_results)
        messagebox.showinfo(self._("Export"), self._("Results exported to speed_results.csv"))

    def toggle_theme(self):
        current_theme = self.style.theme_use()
        self.style.set_theme("arc" if current_theme == "equilux" else "equilux")

    def share_results_email(self):
        if not self.test_results:
            messagebox.showwarning(self._("No Data"), self._("Run a speed test first!"))
            return
        last_result = self.test_results[-1]
        email = simpledialog.askstring(self._("Share Results"), self._("Enter your email address:"))
        if email:
            try:
                msg = MIMEMultipart()
                msg["From"] = "your_email@example.com"
                msg["To"] = email
                msg["Subject"] = self._("Internet Speed Test Results")
                body = self._("Download: {} Mbps\nUpload: {} Mbps\nPing: {} ms").format(last_result[0], last_result[1], last_result[2])
                msg.attach(MIMEText(body, "plain"))
                server = smtplib.SMTP("smtp.example.com", 587)
                server.starttls()
                server.login("your_email@example.com", "your_password")
                server.sendmail("your_email@example.com", email, msg.as_string())
                server.quit()
                messagebox.showinfo(self._("Success"), self._("Results sent successfully!"))
            except Exception as e:
                messagebox.showerror(self._("Error"), self._("Failed to send email: {}").format(str(e)))

    def share_results_social(self):
        if not self.test_results:
            messagebox.showwarning(self._("No Data"), self._("Run a speed test first!"))
            return
        last_result = self.test_results[-1]
        message = self._("Download: {} Mbps\nUpload: {} Mbps\nPing: {} ms").format(last_result[0], last_result[1], last_result[2])
        messagebox.showinfo(self._("Share Results"), self._("Copy the results and share them on your social media:\n\n{}").format(message))

    def select_server(self):
        try:
            test = st.Speedtest()
            servers = test.get_servers() or {}
            if not servers:
                messagebox.showerror(self._("Error"), self._("No servers found. Please check your internet connection."))
                return
            server_list = [f"{server[0]['id']} - {server[0]['name']}" for server in servers.values() if isinstance(server, list)]
            self.selected_server = simpledialog.askstring(self._("Select Server"), self._("Enter server ID:"))
            if self.selected_server:
                messagebox.showinfo(self._("Server Selected"), self._("Server {} selected.").format(self.selected_server))
        except st.ConfigRetrievalError:
            messagebox.showerror(self._("Error"), self._("Failed to retrieve server list. Check your internet connection."))
        except Exception as e:
            messagebox.showerror(self._("Error"), self._("An error occurred: {}").format(str(e)))

    def get_ip_info(self):
        try:
            response = requests.get("https://ipinfo.io/json")
            data = response.json()
            return data.get("ip"), data.get("org"), data.get("city"), data.get("country")
        except Exception:
            return self._("Unknown"), self._("Unknown"), self._("Unknown"), self._("Unknown")


if __name__ == "__main__":
    root = ctk.CTk()
    app = SpeedTestApp(root)
    root.mainloop()