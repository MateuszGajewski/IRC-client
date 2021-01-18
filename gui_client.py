from irc_client import IRCClient
import code
import threading
import time
from tkinter import *
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText

class Window(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.root = master
        self.client = IRCClient()
        self.grid()
        self.tabs = {}
        self.run_login_window()
        self.channels = [
                            'No channel',
                         ]
        self.start_channel = 'No channel'
        self.current_tab_name = self.start_channel


    def run_login_window(self):  # Builds the UI for the username entry window
        self.loginWindow = Toplevel()
        self.loginWindow.transient(root)
        w = 280
        h = 240
        sw = self.loginWindow.winfo_screenwidth()
        sh = self.loginWindow.winfo_screenheight()
        x = (sw - w) / 2
        y = (sh - h) / 2
        self.loginWindow.geometry('%dx%d+%d+%d' % (w, h, x, y))

        self.server_ip_input = Entry(self.loginWindow, width=24)
        self.server_ip_input.place(x=75, y=10)
        self.server_ip_input.insert(0, '127.0.0.1')
        Label(self.loginWindow, text='Server IP').place(x=5, y=10)

        self.server_port_input = Entry(self.loginWindow, width=24)
        self.server_port_input.place(x=75, y=32)
        self.server_port_input.insert(0, '3000')
        Label(self.loginWindow, text='Server Port').place(x=5, y=32)

        self.username_input = Entry(self.loginWindow, width=24)
        self.username_input.place(x=75, y=54)
        self.username_input.focus_force()
        Label(self.loginWindow, text='Username').place(x=5, y=54)

        self.usernameButton = Button(self.loginWindow, text='Connect', command=self.connect_to_server, height=2, width=8)
        self.usernameButton.bind('<Return>', self.connect_to_server)
        self.usernameButton.place(x=90, y=185)

    def connect_to_server(self, event=None):

        username = self.username_input.get()
        if username == '':
            messagebox.showinfo(message='You must enter a username', icon='warning')
        elif ' ' in username:
            messagebox.showinfo(message='Username cannot contain spaces', icon='warning')
        self.nick = username
        self.client.server = self.server_ip_input.get()
        self.client.port = int(self.server_port_input.get())
        try:
            self.client.connect()
        except (ConnectionRefusedError):
            messagebox.showinfo(message='Cannot connect to the server', icon='warning')
            return
        except (OSError):
            print('already connected')
            pass
        self.client.send("NICK " + username+"\n")
        time.sleep(1)

        """response = self.client.get_response()

        print(response)
        if response[0:8] != 'signedin':
            messagebox.showinfo(message='Some error occured: ' + response, icon='warning')
            return

        self.client.send('ok')"""

        self.run_chat_window()
        self.start_reading()
        self.loginWindow.destroy()

    def run_chat_window(self):  # Builds the UI for the main window

        root.title('IRC')

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

    def switch_tab(self, event):
        clicked_tab = self.tab_control.tk.call(self.tab_control._w, "identify", "tab", event.x, event.y)
        channel_name = self.tab_control.tab(clicked_tab, "text")

        if channel_name != self.current_tab_name:

            #clear old chat box
            old_text_box = self.tabs[self.current_tab_name]['textbox']
            old_text_box.delete("1.0", END)

            self.current_tab_name = channel_name
            channel_number = channel_name[-1]
            self.join_channel(channel_number)


    def create_channel_tab(self, tab_name):
        self.textboxframe = ttk.Frame(self.tab_control)
        self.textboxframe.grid(row=0, column=0, sticky=N + S + E + W)

        self.text_box = ScrolledText(self.textboxframe, height=24, width=47, wrap=WORD)
        self.text_box.grid(row=0, column=0, padx=(10, 0), pady=(10, 5), sticky=N + S + E + W)
        self.text_box.config(state=DISABLED)

        self.entry_box = ScrolledText(self.textboxframe, height=2, width=47, wrap=WORD)
        self.entry_box.grid(row=2, column=0, padx=(10, 0), pady=(0, 10), sticky=N + S + E + W)
        self.entry_box.bind('<Return>', lambda: self.write(tab_name))

        self.sendButton = Button(self.textboxframe, text='send', command=lambda: self.write(tab_name), height=2, width=8)
        self.sendButton.bind('<Return>', lambda: self.write(tab_name))
        self.sendButton.grid(row=4, column=0, padx=(10, 0), pady=(0, 10), sticky=N + S + E + W)

        Grid.rowconfigure(self.textboxframe, 0, weight=1)
        Grid.columnconfigure(self.textboxframe, 0, weight=1)

        self.tabs[tab_name] = {}
        self.tabs[tab_name]['tab'] = self.textboxframe
        self.tabs[tab_name]['textbox'] = self.text_box
        self.tabs[tab_name]['entrybox'] = self.entry_box

        self.tab_control.add(self.textboxframe, text=tab_name)

    def start_reading(self):
        thread = threading.Thread(target=self.read, daemon=True)
        thread.start()

    def get_text(self, scrolled_text):
        text = scrolled_text.get("1.0", 'end-1c')
        scrolled_text.delete('1.0', END)
        scrolled_text.focus_force()
        return text

    def write(self, tab_name):
        to_send =''
        entry_box = self.tabs[tab_name]['entrybox']
        message = self.get_text(entry_box)
        print(message)
        if(message[0]=='/'):
            n = message.find(' ')
            to_send = message[1:n].upper() + message[n:]
            text_box = self.tabs[self.current_tab_name]['textbox']
            text_box.after(0, self.insert_text(text_box, message[n + 1:]))
            if (message[0:5].upper() == '/JOIN'):
                self.tabs[self.current_tab_name]['tab'].destroy()
                self.create_channel_tab(message[message.find(' ')+1:])
                #self.tabs[self.current_tab_name]['tab'] = message[message.find(' ')+1:]
                self.current_tab_name  = message[message.find(' ')+1:]


        else:
            to_send = 'PRIVMSG ' + self.current_tab_name + ' :' + message
            text_box = self.tabs[self.current_tab_name]['textbox']
            text_box.after(0, self.insert_text(text_box, self.nick + ': '+message))

        self.client.send(to_send + '\n')


    def join_channel(self, number):
        print('channel: '+ str(number))
        self.client.join_channel(number)

    def parse_response(self, response):
        print(response)
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
        return ans


    def read(self):
        while 1:
            response = self.client.get_response()
            response = self.parse_response(response)

            text_box = self.tabs[self.current_tab_name]['textbox']
            print(response)
            text_box.after(0, self.insert_text(text_box, response))

    def insert_text(self, frame, text):
        frame.configure(state='normal')
        frame.insert(END, text + '\n')
        # Autoscroll to the bottom
        frame.yview(END)


if __name__ == '__main__':
    root = Tk()
    app = Window(root)
    root.mainloop()