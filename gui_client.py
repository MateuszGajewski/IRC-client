from irc_client import IRCClient
import threading
import time
from tkinter import *
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from datetime import datetime

#Klasa implementująca interfejs graficzny

class Window(Frame):
    #Inicjalizacja okna programu
    def __init__(self, master):
        Frame.__init__(self, master)
        self.root = master
        self.client = IRCClient()
        self.grid()
        self.tabs = {}
        self.run_login_window()
        self.channels = ['No channel']
        self.start_channel = 'No channel'
        self.current_tab_name = self.start_channel

    #Wywoływanie okna logowania
    def run_login_window(self):

        root.title('~~  IRC  ~~')

        self.loginWindow = Toplevel()
        self.loginWindow.transient(root)
        w = 280
        h = 125
        sw = self.loginWindow.winfo_screenwidth()
        sh = self.loginWindow.winfo_screenheight()
        x = (sw - w) / 2
        y = (sh - h) / 2
        self.loginWindow.geometry('%dx%d+%d+%d' % (w, h, x, y))

        self.server_ip_input = Entry(self.loginWindow, width=24)
        self.server_ip_input.place(x=125, y=10)
        self.server_ip_input.insert(0, '127.0.0.1')
        Label(self.loginWindow, text='Adres IP serwera').place(x=5, y=10)

        self.server_port_input = Entry(self.loginWindow, width=24)
        self.server_port_input.place(x=125, y=35)
        self.server_port_input.insert(0, '1234')
        Label(self.loginWindow, text='Port serwera').place(x=5, y=35)

        self.username_input = Entry(self.loginWindow, width=24)
        self.username_input.place(x=125, y=60)
        self.username_input.focus_force()
        Label(self.loginWindow, text='NICK').place(x=5, y=60)

        self.usernameButton = Button(self.loginWindow, text='POŁĄCZ', command=self.connect_to_server, height=1, width=8)
        self.usernameButton.bind('<Return>', self.connect_to_server)
        self.usernameButton.place(x=100, y=90)

    #Funkcja służąca do nawiązywania połączenia z serwerem
    def connect_to_server(self, event=None):
        username = self.username_input.get()
        #Ustalanie początkoweg nicku
        if username == '':
            messagebox.showinfo(message='Podaj NICK.', icon='warning')
        elif ' ' in username:
            messagebox.showinfo(message='Nazwa użytkownika nie może zawierać spacji.', icon='warning')
        else:
            self.nick = username
            self.client.server = self.server_ip_input.get()
            self.client.port = int(self.server_port_input.get())
            try:
                self.client.connect()
            except (ConnectionRefusedError) as e:
                messagebox.showinfo(message='Nie można połączyć się z serwerem.', icon='warning')
                return
            except (OSError) as e:
                messagebox.showinfo(message=e, icon='warning')
                return
            self.client.send("NICK " + username+"\n")
            time.sleep(1)

            self.run_chat_window()
            self.start_reading()
            self.loginWindow.destroy()
    #Wywoływanie okna czatu
    def run_chat_window(self):

        root.title('~~  IRC  ~~')

        self.tab_control = ttk.Notebook(root)
        self.tab_control.grid(row=0, column=0, sticky=W+E+N+S)

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.tab_control.columnconfigure(3, weight=1)
        self.tab_control.rowconfigure(0, weight=1)

        for channel in self.channels:
            self.create_channel_tab(channel)
            self.current_tab_name = channel
        self.tab_control.bind('<Button-1>', self.switch_tab)

    #Zmiana nazwy kanału przy dołączaniu do nowego kanału
    def switch_tab(self, event):
        clicked_tab = self.tab_control.tk.call(self.tab_control._w, "identify", "tab", event.x, event.y)
        channel_name = self.tab_control.tab(clicked_tab, "text")

        if channel_name != self.current_tab_name:

            old_text_box = self.tabs[self.current_tab_name]['textbox']
            old_text_box.delete("1.0", END)

            self.current_tab_name = channel_name
            channel_number = channel_name[-1]
            self.join_channel(channel_number)

    #Ustalanie parametrów okna czatu
    def create_channel_tab(self, tab_name):
        self.textboxframe = ttk.Frame(self.tab_control)
        self.textboxframe.grid(row=0, column=0, sticky=N + S + E + W)

        self.text_box = ScrolledText(self.textboxframe, height=24, width=47, wrap=WORD)
        self.text_box.grid(row=0, column=0, padx=(10, 0), pady=(10, 5), sticky=N + S + E + W)
        self.text_box.config(state=DISABLED)

        self.entry_box = ScrolledText(self.textboxframe, height=2, width=47, wrap=WORD)
        self.entry_box.grid(row=2, column=0, padx=(10, 0), pady=(0, 10), sticky=N + S + E + W)
        self.entry_box.bind('<Return>', lambda: self.write(tab_name))

        self.sendButton = Button(self.textboxframe, text='WYŚLIJ', command=lambda: self.write(tab_name), height=2, width=8)
        self.sendButton.bind('<Return>', lambda: self.write(tab_name))
        self.sendButton.grid(row=4, column=0, padx=(10, 0), pady=(0, 10), sticky=N + S + E + W)

        Grid.rowconfigure(self.textboxframe, 0, weight=1)
        Grid.columnconfigure(self.textboxframe, 0, weight=1)

        self.tabs[tab_name] = {}
        self.tabs[tab_name]['tab'] = self.textboxframe
        self.tabs[tab_name]['textbox'] = self.text_box
        self.tabs[tab_name]['entrybox'] = self.entry_box

        self.tab_control.add(self.textboxframe, text=tab_name)

    #Inicjalizacja wątku odbierającego wiadomości
    def start_reading(self):
        thread = threading.Thread(target=self.read, daemon=True)
        thread.start()

    #Pobieranie tekstu z formularza
    def get_text(self, scrolled_text):
        text = scrolled_text.get("1.0", 'end-1c')
        scrolled_text.delete('1.0', END)
        scrolled_text.focus_force()
        return text

    #Wysyłanie wiadomości przez użytkownika
    def write(self, tab_name):
        to_send =''
        entry_box = self.tabs[tab_name]['entrybox']

        message =self.get_text(entry_box)
        print(message)
        if(message[0]=='/'):
            n = message.find(' ')
            to_send = message[1:n].upper() + message[n:]
            text_box = self.tabs[self.current_tab_name]['textbox']

            if (message[0:5].upper() == '/JOIN'):
                if(message[6] != '#'):
                    messagebox.showinfo(message='Nazwa kanału musi zaczynać się od #.', icon='warning')
                    return

                self.tabs[self.current_tab_name]['tab'].destroy()
                self.create_channel_tab(message[message.find(' ')+1:])
                self.current_tab_name = message[message.find(' ')+1:]
                text_box = self.tabs[self.current_tab_name]['textbox']

            if(message[0:5].upper()=='/NICK'):
                m = (message[7:]).find(' ')
                if (m != -1):
                    messagebox.showinfo(message='Nick nie może zawierać spacji.', icon='warning')
                    return
                else:
                    self.nick = message[6:]
            if (message[0:5].upper() == '/HELP'):
                help_text = "Dostępne komendy:\n" \
                            "/nick nowy_nick\n" \
                            "~nick nie powinien zawierać spacji\n" \
                            "/join #nazwa_kanału\n" \
                            "~nazwa kanału powinna zaczynać się od #\n" \
                            "/privmsg nazwa_użytkownika wiadomośc\n"
                text_box.after(0, self.insert_text(text_box, help_text))
                return


            text_box.after(0, self.insert_text(text_box, message[n + 1:]))

        else:
            to_send = 'PRIVMSG ' + self.current_tab_name + ' :' + message
            text_box = self.tabs[self.current_tab_name]['textbox']
            now = datetime.now()
            time = now.strftime("<%H:%M> ")
            text_box.after(0, self.insert_text(text_box, time + self.nick + ': '+message))
        #Wysyłanie wiadomości do serwera
        self.client.send(to_send + '\n')



    #Parsowanie odpowiedzi od serwera
    def parse_response(self, response):
        ans = ''
        n = response.find(' ')
        substr = response[0:n]
        if (substr.find('!') != -1):
            ans = substr[2:substr.find('!')]+": "
            n = response.find(':', 2)
            ans += response[n+1:]
        else:
            n = response.find(':', 1)
            ans = response[n+1:]
        now = datetime.now()
        time = now.strftime("<%H:%M> ")

        return time + ans

    #Wątek odbierający wiadomości
    def read(self):
        while 1:
            response = self.client.get_response()
            response = self.parse_response(response)
            text_box = self.tabs[self.current_tab_name]['textbox']
            text_box.after(0, self.insert_text(text_box, response))

    #Dodawanie tekstu do okienka czatu
    def insert_text(self, frame, text):
        frame.configure(state='normal')
        frame.insert(END, text + '\n')
        frame.yview(END)

#Start programu
if __name__ == '__main__':
    root = Tk()
    app = Window(root)
    root.mainloop()
