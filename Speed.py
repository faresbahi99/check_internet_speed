import speedtest as st
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from ttkthemes import ThemedStyle
import threading
import matplotlib.pyplot as plt
import json
import csv
import requests
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import gettext
import customtkinter as ctk

selected_server = None

# Initialize test results and language settings
test_results = []
current_language = "en"  # Default language is English

# Initialize gettext for internationalization
gettext.bindtextdomain("base", localedir="locales")
gettext.textdomain("base")
_ = gettext.gettext

# Function to change language
def change_language(lang):
    global current_language
    current_language = lang
    gettext.bindtextdomain("base", localedir="locales")
    gettext.textdomain("base")
    _ = gettext.gettext
    update_ui_texts()

# Function to update UI texts based on the selected language
def update_ui_texts():
    title_label.configure(text=_("Internet Speed Test"))
    start_button.configure(text=_("Start Test"))
    export_button.configure(text=_("Export CSV"))
    share_button.configure(text=_("Share Results"))
    theme_button.configure(text=_("Toggle Theme"))
    stop_button.configure(text=_("Stop Test"))
    server_button.configure(text=_("Select Server"))
    down_speed_label.configure(text=_("Download Speed: N/A"))
    up_speed_label.configure(text=_("Upload Speed: N/A"))
    ping_label.configure(text=_("Ping: N/A"))
    ip_label.configure(text=_("IP: N/A"))

# Function to get IP information
def get_ip_info():
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        return data.get("ip"), data.get("org"), data.get("city"), data.get("country")
    except Exception:
        return _("Unknown"), _("Unknown"), _("Unknown"), _("Unknown")

# Function to perform the speed test
# Function to perform the speed test
def speed_Test():
    global selected_server
    global stop_test
    stop_test = False

    try:
        test = st.Speedtest()
        
        # Manual server selection
        if selected_server:
            test.get_servers([selected_server])
        else:
            test.get_best_server()
        
        down_speed = round(test.download() / 10**6, 2)
        up_speed = round(test.upload() / 10**6, 2)
        ping = test.results.ping
        ip, isp, city, country = get_ip_info()
        
        down_speed_label.configure(text=_("Download Speed: {} Mbps").format(down_speed), text_color="#4CAF50")
        up_speed_label.configure(text=_("Upload Speed: {} Mbps").format(up_speed), text_color="#2196F3")
        ping_label.configure(text=_("Ping: {} ms").format(ping), text_color="#FF5722")
        ip_label.configure(text=_("IP: {} | ISP: {} ({}, {})").format(ip, isp, city, country), text_color="#8E44AD")
        
        test_results.append((down_speed, up_speed, ping))
        root.after(100, update_graph)
        save_results()
        
        progress_bar.stop()
        progress_bar.set(1.0)  # Set progress bar to 100%
        root.after(2000, lambda: progress_bar.set(0.0))  # Reset progress bar after 2 seconds
        
        # Send notification
        messagebox.showinfo(_("Test Complete"), _("Speed test completed successfully!"))
    except st.ConfigRetrievalError:
        messagebox.showerror(_("Error"), _("Failed to retrieve speedtest configuration. Check your internet connection."))
    except Exception as e:
        messagebox.showerror(_("Error"), _("An error occurred: {}").format(str(e)))

# Function to start the test in a separate thread
def start_test():
    down_speed_label.configure(text=_("Testing download speed..."), text_color="black")
    up_speed_label.configure(text=_("Testing upload speed..."), text_color="black")
    ping_label.configure(text=_("Testing ping..."), text_color="black")
    progress_bar.start()
    threading.Thread(target=speed_Test, daemon=True).start()

# Function to start the test in a separate thread
def start_test():
    down_speed_label.configure(text=_("Testing download speed..."), text_color="black")
    up_speed_label.configure(text=_("Testing upload speed..."), text_color="black")
    ping_label.configure(text=_("Testing ping..."), text_color="black")
    progress_bar.start()
    threading.Thread(target=speed_Test, daemon=True).start()

# Function to stop the test
def stop_test():
    global stop_test
    stop_test = True
    progress_bar.stop()
    messagebox.showinfo(_("Test Stopped"), _("Speed test stopped by the user."))

# Function to update the graph
def update_graph():
    plt.clf()
    plt.plot([x[0] for x in test_results], label=_("Download Speed (Mbps)"), marker='o', linestyle='-')
    plt.plot([x[1] for x in test_results], label=_("Upload Speed (Mbps)"), marker='s', linestyle='-')
    plt.xlabel(_("Test Number"))
    plt.ylabel(_("Speed (Mbps)"))
    plt.legend()
    plt.title(_("Internet Speed Test Results"))
    plt.draw()
    plt.pause(0.1)

# Function to save results to a JSON file
def save_results():
    with open("speed_results.json", "w") as file:
        json.dump(test_results, file)

# Function to export results to a CSV file
def export_csv():
    with open("speed_results.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([_("Download Speed (Mbps)"), _("Upload Speed (Mbps)"), _("Ping (ms)")])
        writer.writerows(test_results)
    messagebox.showinfo(_("Export"), _("Results exported to speed_results.csv"))

# Function to toggle between light and dark themes
def toggle_theme():
    current_theme = style.theme_use()
    style.set_theme("arc" if current_theme == "equilux" else "equilux")

# Function to share results via email
def share_results_email():
    if not test_results:
        messagebox.showwarning(_("No Data"), _("Run a speed test first!"))
        return
    last_result = test_results[-1]
    email = simpledialog.askstring(_("Share Results"), _("Enter your email address:"))
    if email:
        try:
            msg = MIMEMultipart()
            msg["From"] = "your_email@example.com"
            msg["To"] = email
            msg["Subject"] = _("Internet Speed Test Results")
            body = _("Download: {} Mbps\nUpload: {} Mbps\nPing: {} ms").format(last_result[0], last_result[1], last_result[2])
            msg.attach(MIMEText(body, "plain"))
            server = smtplib.SMTP("smtp.example.com", 587)
            server.starttls()
            server.login("your_email@example.com", "your_password")
            server.sendmail("your_email@example.com", email, msg.as_string())
            server.quit()
            messagebox.showinfo(_("Success"), _("Results sent successfully!"))
        except Exception as e:
            messagebox.showerror(_("Error"), _("Failed to send email: {}").format(str(e)))

# Function to share results on social media
def share_results_social():
    if not test_results:
        messagebox.showwarning(_("No Data"), _("Run a speed test first!"))
        return
    last_result = test_results[-1]
    message = _("Download: {} Mbps\nUpload: {} Mbps\nPing: {} ms").format(last_result[0], last_result[1], last_result[2])
    messagebox.showinfo(_("Share Results"), _("Copy the results and share them on your social media:\n\n{}").format(message))

# Function to manually select a server
def select_server():
    global selected_server
    
    try:
        test = st.Speedtest()
        servers = test.get_servers() or {}

        if not servers:
            messagebox.showerror(_("Error"), _("No servers found. Please check your internet connection."))
            return

        server_list = [f"{server[0]['id']} - {server[0]['name']}" for server in servers.values() if isinstance(server, list)]
        
        selected_server = simpledialog.askstring(_("Select Server"), _("Enter server ID:"))
        if selected_server:
            messagebox.showinfo(_("Server Selected"), _("Server {} selected.").format(selected_server))
    except st.ConfigRetrievalError:
        messagebox.showerror(_("Error"), _("Failed to retrieve server list. Check your internet connection."))
    except Exception as e:
        messagebox.showerror(_("Error"), _("An error occurred: {}").format(str(e)))

# Main application window
root = ctk.CTk()
root.title(_("Internet Speed Test"))
root.geometry("500x500")
root.resizable(True, True)
style = ThemedStyle(root)
style.set_theme("equilux")

# Use padx and pady for padding instead of padding
frame = ctk.CTkFrame(root)
frame.pack(expand=True, fill="both", padx=20, pady=20)

# Title Label
title_label = ctk.CTkLabel(frame, text=_("Internet Speed Test"), font=("Arial", 20, "bold"), text_color="#FFD700")
title_label.pack(pady=10)

# Start Button
start_button = ctk.CTkButton(frame, text=_("Start Test"), command=start_test)
start_button.pack(pady=10)

# Stop Button
stop_button = ctk.CTkButton(frame, text=_("Stop Test"), command=stop_test)
stop_button.pack(pady=5)

# Server Selection Button
server_button = ctk.CTkButton(frame, text=_("Select Server"), command=select_server)
server_button.pack(pady=5)

# Results Labels
down_speed_label = ctk.CTkLabel(frame, text=_("Download Speed: N/A"), font=("Arial", 12))
down_speed_label.pack(pady=5)
up_speed_label = ctk.CTkLabel(frame, text=_("Upload Speed: N/A"), font=("Arial", 12))
up_speed_label.pack(pady=5)
ping_label = ctk.CTkLabel(frame, text=_("Ping: N/A"), font=("Arial", 12))
ping_label.pack(pady=5)
ip_label = ctk.CTkLabel(frame, text=_("IP: N/A"), font=("Arial", 12))
ip_label.pack(pady=5)

# Progress Bar
progress_bar = ctk.CTkProgressBar(frame, mode='indeterminate', width=300)
progress_bar.pack(pady=10)

# Buttons for Extra Features
export_button = ctk.CTkButton(frame, text=_("Export CSV"), command=export_csv)
export_button.pack(pady=5)
share_button = ctk.CTkButton(frame, text=_("Share Results"), command=share_results_social)
share_button.pack(pady=5)
theme_button = ctk.CTkButton(frame, text=_("Toggle Theme"), command=toggle_theme)
theme_button.pack(pady=5)

# Language Selection
language_frame = ctk.CTkFrame(frame)
language_frame.pack(pady=10)
ctk.CTkButton(language_frame, text="English", command=lambda: change_language("en")).pack(side="left", padx=5)
ctk.CTkButton(language_frame, text="العربية", command=lambda: change_language("ar")).pack(side="left", padx=5)
ctk.CTkButton(language_frame, text="Français", command=lambda: change_language("fr")).pack(side="left", padx=5)

plt.ion()
plt.figure()
root.mainloop()