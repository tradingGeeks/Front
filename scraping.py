from tkinter import *
from PIL import ImageTk, Image
from selenium import webdriver
from bs4 import BeautifulSoup as bs
from subprocess import call
import requests
from bs4 import BeautifulSoup
from time import sleep
from urllib.parse import urlsplit, urlparse
import functools
import pandas as pd
import sqlite3

class Front(object):
    def __init__(self, window):
        self.window = window
        self.window.title("Antonio Colmenares & Chloe Martin - Automated Scraping")
        self.window.configure(background="gray95")
        self.font = ("ms serif", 16)
        self.data = {}

        #record scraping failure
        db = sqlite3.connect("scraping_failure.db")
        cur = db.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS fail(id INTEGER PRIMARY KEY, element VARCHAR, s_type VARCHAR, website varchar)")
        db.commit()
        db.close()

        furthest_label_column=13

        self.exit_bt = Button(master=self.window, text="Exit", fg="black", highlightbackground='red',
                              highlightthickness=2, font=self.font, command=sys.exit)
        self.exit_bt.grid(row=0, column=furthest_label_column, sticky = "E")

        self.webFrame = Frame(master=self.window, padx=5, pady=5, bg="gray95")
        self.webFrame.grid(row=1, column=2, columnspan=furthest_label_column, rowspan=2, sticky="NSEW")
        self.webFrame.grid_columnconfigure(0, weight=1)
        self.webFrame.grid_rowconfigure(0, weight=1)

        self.lb = Label(self.webFrame, text="Website to be scraped: ", font=self.font, fg="gray17", bg="gray95")
        self.lb.grid(row=1, column=0, sticky="NSEW")

        self.url = StringVar()

        self.url_entry = Entry(self.webFrame, textvariable=self.url, bg="gray90", highlightbackground="gray95")
        self.entry_text = "Enter website in URL format"
        self.url_entry.insert(0, self.entry_text)
        self.url_entry.bind("<Button-1>", self.clearWebsiteEntry)
        self.url_entry.grid(row=2, column=0, sticky="NSEW", padx=3, ipadx=1)

        self.search_bt_status = False
        self.search_bt = Button(self.webFrame, text="Search", fg="gray29", bg="gray90", relief = "raised",
                         font=self.font, command=self.openWebsite, highlightbackground="gray95")
        self.search_bt.grid(row=2, column=furthest_label_column, sticky="NSEW")

        option_row = 10

        self.options = Frame(master=self.window, padx=5, pady=5, bg="gray95")
        self.options.grid(row=option_row, column=1, rowspan=30, columnspan=5)

        self.lb = Label(self.options, text="1", font=self.font, fg= "IndianRed2", bg="gray95")
        self.lb.grid(row=option_row, column=1)

        # get emails
        self.email_cvalue = BooleanVar()
        self.email_checkbox = Checkbutton(self.options, text="Get emails", font=self.font,
                                          fg="gray29", bg="gray95", highlightbackground="gray95",
                                          variable=self.email_cvalue)
        self.email_checkbox.grid(row=option_row, column=3, sticky="NSW")

        # get linkedin urls from main url page
        self.lin_cvalue = BooleanVar()
        self.lin_checkbox = Checkbutton(self.options, text="Get linkedin URL profiles", font=self.font,
                                        fg="gray29", bg="gray95", highlightbackground="gray95",
                                        variable=self.lin_cvalue, command=self.linkedinMoreOptions)
        self.lin_checkbox.grid(row=option_row + 1, column=3, sticky="NSW")

        # get foreign URLs
        self.foreign_cvalue = BooleanVar()
        self.foreign_checkbox = Checkbutton(self.options, text="Get all foreign URLs", font=self.font,
                                            fg="gray29", bg="gray95", highlightbackground="gray95",
                                            variable=self.foreign_cvalue)
        self.foreign_checkbox.grid(row=option_row + 2, column=3, sticky="NSW")

        # get all local URLs
        self.local_cvalue = BooleanVar()
        self.local_checkbox = Checkbutton(self.options, text="Get all local URLs", font=self.font,
                                          fg="gray29", bg="gray95", highlightbackground="gray95",
                                          variable=self.local_cvalue)
        self.local_checkbox.grid(row=option_row + 3, column=3, sticky="NSW")

        # show more options
        self.show_more = False #avoid the show more options being non existing in the method executeScrape
        self.show_bt = Button(self.options, text="Show More", font=self.font, fg="gray29", bg="gray95",
                              highlightbackground="gray95", command=self.showMoreOptions)
        self.show_bt.grid(row=option_row + 4, column=3, sticky="NSW", padx=5, pady=5)


        # scraping quantity
        self.lb = Label(self.options, text="2", font=self.font, fg="IndianRed2", bg="gray95")
        self.lb.grid(row=option_row + 8, column=1)

        self.bt = Button(master=self.options, text="Scrape entered URL", fg="gray29", bg="gray90", relief="raised",
                         font=self.font, command= lambda:self.executeScrape("main"))
        self.bt.grid(row=option_row + 8, column=3)

        self.bt = Button(master=self.options, text="Scrape entire website", fg="gray29", bg="gray90", relief="raised",
                         font=self.font, command=lambda:self.executeScrape("entire"))
        self.bt.grid(row=option_row + 8, column=4)

        # results
        self.lb = Label(self.options, text="3", font=self.font, fg="IndianRed2", bg="gray95")
        self.lb.grid(row=option_row + 10, column=1)

        self.scrollbar = Scrollbar(master=self.options)
        self.scrollbar.grid(row=option_row + 10, column=3)

        self.listbox = Listbox(master=self.options, fg="gray29", bg="gray95", font=self.font,
                               yscrollcommand=self.scrollbar.set, height=10, width=10, bd=0,
                               highlightthickness = 0.8, highlightbackground="IndianRed2"
                               )
        self.listbox.grid(row=option_row+10, column=2, columnspan=3, sticky="NSWE",
                          padx=5, pady=5, ipadx=5, ipady=5)
        self.scrollbar.config(bg="IndianRed2", highlightbackground="gray95",
                                   command=self.listbox.yview)

        self.listbox.bind("<Double-Button-1>", self.viewScrape)

    def widFlash(self, event, wid):
        wid.config(highlightbackground="IndianRed2")
        self.window.after(150, lambda: wid.config(highlightbackground="gray95"))

    def openWebsite(self):
        if self.url_entry.get()== self.entry_text or self.url_entry.get() == "":
            self.window.bind("<Button-1>", functools.partial(self.widFlash, wid=self.url_entry))
            return

        else:
            self.search_bt_status = True
            self.url_entry.config(state = 'disabled')

            self.clear_bt = Button(self.webFrame, text="Clear All", font=self.font, fg="OliveDrab4", bg="gray95",
                                   highlightbackground="gray95", command= self.clearAll)
            self.clear_bt.grid(row=0, column=0)

            self.canvas = Canvas(master=self.window, width=320, height=200, bg="gray95")
            self.canvas.grid(row=3, column=2, columnspan=7, rowspan=5, padx=5, pady=5, sticky="NSEW")


            #open website from entry widget
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
            chrome_options.add_argument("--kiosk")
            browser = webdriver.Chrome('/Users/chloemartin/Downloads/chromedriver 2', options=chrome_options)
    
            try:
                browser.get(self.url_entry.get())
    
            except:
                browser.close()
                self.clearWebsiteEntry
    
            else:
                call(["screencapture", "screenshot.jpg"])
                sleep(1.5)
                browser.close()

            #display website screenshot on canvas
            screenshot = Image.open("screenshot.jpg")
            size = 320, 200
            screenshot.thumbnail(size)
            self.canvas.image = ImageTk.PhotoImage(screenshot)
            self.canvas.create_image(164, 3, image=self.canvas.image, anchor="n")

    def clearWebsiteEntry(self, event):
        self.url_entry.delete(0, END)

    def clearAll(self):
        #like a start from scratch
        self.url_entry.config(state='normal')
        self.url_entry.delete(0, END)
        self.url.set("")
        self.canvas.destroy()
        self.search_bt_status = False
        self.email_cvalue.set(False)
        self.lin_cvalue.set(False)
        self.foreign_cvalue.set(False)
        self.local_cvalue.set(False)
        self.data = {}

        if self.show_more==True:
            try:
                self.lin_user_cvalue.set(False)
            except:
                pass
            try:
                self.lin_group_cvalue.set(False)
            except:
                pass
            try:
                self.lin_corp_cvalue.set(False)
            except:
                pass
            try:
                self.tw_cvalue.set(False)
            except:
                pass
            try:
                self.fb_cvalue.set(False)
            except:
                pass
            try:
                self.in_cvalue.set(False)
            except:
                pass
            try:
                self.geo_cvalue.set(False)
            except:
                pass
            try:
                self.ph_cvalue.set(False)
            except:
                pass
        self.show_more = False

        try:
            self.listbox.delete(0, END)
        except:
            return

    def exceptionAlarmHandling(self, event):
        self.window.focus_force()
        self.window.bell()

    def linkedinMoreOptions(self):
        if self.lin_cvalue.get() == False:
            return
        else:
            # create a new window for choosing options
            new_window = Toplevel(self.window)
            new_window.geometry("330x108")
            new_window.title("Linkedin Scrape Options")
            new_window.bind("<FocusOut>", self.exceptionAlarmHandling)
            new_window.configure(background="gray95")

            self.lb = Label(master=new_window, text="Choose the type of linkedin profile: ", font=self.font,
                            fg = "gray17", bg="gray95")
            self.lb.grid(row=0, column=0, sticky="NSEW")

            # options
            self.lin_user_cvalue = BooleanVar()
            self.lin_user = Checkbutton(master=new_window, text="Get user profiles", font=self.font,
                                        fg="gray29", bg="gray95", highlightbackground="gray95",
                                        variable=self.lin_user_cvalue)
            self.lin_user.grid(row=1, column=0, sticky="NSW")

            self.lin_corp_cvalue = BooleanVar()
            self.lin_corp = Checkbutton(master=new_window, text="Get corporation profiles", font=self.font,
                                        fg="gray29", bg="gray95", highlightbackground="gray95",
                                        variable=self.lin_corp_cvalue)
            self.lin_corp.grid(row=2, column=0, sticky="NSW")

            self.lin_group_cvalue = BooleanVar()
            self.lin_group = Checkbutton(master=new_window, text="Get group profiles", font=self.font,
                                        fg="gray29", bg="gray95", highlightbackground="gray95",
                                         variable=self.lin_group_cvalue)
            self.lin_group.grid(row=3, column=0, sticky="NSW")

            #return to main window
            self.bt = Button(master=new_window, text="Validate", command=new_window.destroy)
            self.bt.grid(row=2, column=1, sticky="NSW")

    def showMoreOptions(self):
        #create a new window for showing more scraping options
        self.show_more = True

        new_window = Toplevel()
        new_window.geometry("400x200")
        new_window.title("More Scraping Options")
        new_window.configure(background="gray95")

        self.lb = Label(master=new_window, text="More Scraping Options: ", font=self.font,
                        fg="gray17", bg="gray95")
        self.lb.grid(row=0, column=0, sticky="NSEW")

        # twitter
        self.tw_cvalue = BooleanVar()
        self.tw_checkbox = Checkbutton(master=new_window, text="Get twitter URLs", font=self.font,
                                       fg="gray29", bg="gray95", highlightbackground="gray95",
                                       variable=self.tw_cvalue)
        self.tw_checkbox.grid(row=1, column=0, sticky="NSW")

        # facebook
        self.fb_cvalue = BooleanVar()
        self.fb_checkbox = Checkbutton(master=new_window, text="Get facebook URLs", font=self.font,
                                       fg="gray29", bg="gray95", highlightbackground="gray95",
                                       variable=self.fb_cvalue)
        self.fb_checkbox.grid(row=2, column=0, sticky="NSW")

        # instagram
        self.in_cvalue = BooleanVar()
        self.in_checkbox = Checkbutton(master=new_window, text="Get instagram URLs", font=self.font,
                                       fg="gray29", bg="gray95", highlightbackground="gray95",
                                       variable=self.in_cvalue)
        self.in_checkbox.grid(row=3, column=0, sticky="NSW")

        # get all location urls
        self.geo_cvalue = BooleanVar()
        self.geo_checkbox = Checkbutton(master=new_window, text="Get Google Maps location coordinate URL", font=self.font,
                                        fg="gray29", bg="gray95", highlightbackground="gray95",
                                        variable=self.geo_cvalue)
        self.geo_checkbox.grid(row=4, column=0, sticky="NSW")

        # phone numbers
        self.ph_cvalue = BooleanVar()
        self.ph_checkbox = Checkbutton(master=new_window, text="Get phone numbers",
                                       font=self.font,
                                       fg="gray29", bg="gray95", highlightbackground="gray95",
                                       variable=self.ph_cvalue)
        self.ph_checkbox.grid(row=5, column=0, sticky="NSW")

        # return to main window
        self.bt = Button(master=new_window, text="Validate", command=new_window.destroy)
        self.bt.grid(row=2, column=1, sticky="NSW")

    def executeScrape(self, quantity):
        if self.search_bt_status == False:
            self.window.bind("<Button-1>", functools.partial(self.widFlash, wid=self.search_bt))
            return

        else:
            if self.email_cvalue.get() == True:
                self.data["Email"] = self.atSearch("email", quantity)

            if self.lin_cvalue.get() == True:
                temp = self.generalSearch("linkedin", quantity)
                for key in temp.keys():
                    self.data[key] = temp.get(key)

            if self.foreign_cvalue.get() == True:
                self.data["Foreign"] = self.linkSearch("foreign")

            if self.local_cvalue.get() == True:
                self.data["Local"] = self.linkSearch("local")

            if self.show_more==True:
                if self.tw_cvalue.get() == True:
                    self.data["Twitter"] = self.generalSearch("twitter", quantity)

                if self.fb_cvalue.get() == True:
                    self.data["Facebook"] = self.generalSearch("facebook", quantity)

                if self.in_cvalue.get() == True:
                    self.data["Instagram"] = self.generalSearch("instagram", quantity)

                if self.geo_cvalue.get() == True:
                    self.data["Location"] = self.atSearch("location", quantity)

                if self.ph_cvalue.get() == True:
                    self.data["Phone"] = self.phoneSearch(quantity)

            db = sqlite3.connect("scraping_failure.db")
            cur = db.cursor()

            for d in self.data.keys():
                if self.data.get(d) is None:
                    var = d + "-  Failed"
                    self.listbox.insert(END, var)

                    cur.execute("INSERT INTO fail VALUES(NULL, ?, ?, ?)", (d, quantity, self.url_entry.get()))
                    db.commit()

                else:
                    if len(self.data.get(d)) == 0:
                        var = d + "-  Failed"
                        self.listbox.insert(END, var)

                        cur.execute("INSERT INTO fail VALUES(NULL, ?, ?, ?)", (d, quantity, self.url_entry.get()))
                        db.commit()


                    elif len(self.data.get(d)) != 0:
                        var = d + "-  Success"
                        self.listbox.insert(END, var)

            db.close()

    def atSearch(self, search_item, quantity):
        url = []

        if quantity=="main":
            url.append(self.url_entry.get())

        elif quantity=="entire":
            url = self.linkSearch("local")

        items = []
        if len(url) ==0:
            return items

        else:
            for u in url:
                print(url.index(u), u)
                try:
                    content = requests.get(u)
                    soup = BeautifulSoup(content.text, 'lxml')
                except:
                    continue

                itemselector = soup.select('a')

                for each in itemselector:
                    try:
                        i = each.attrs['href']
                    except:
                        try:
                            i = each.attrs('href')
                        except:
                            continue

                    if "@" in i:
                        items.append(i)
                        print("@ --->", i)

            for item in items:
                print(items.index(item), item)
                if search_item=='location':
                    if '/maps/' not in item:
                        items.remove(item)
                elif search_item=='email': #CHECK SI EL EMAIL ES VALIDO ANTONIO
                    if '/maps/' in item:
                        items.remove(item)

                    # only keep emails (with no "mailto:" text at the beginning)
                    if 'mailto:' in item:
                        email_index = items.index(item)
                        items.remove(item)
                        temp = item.split(':')
                        items.insert(email_index, temp[1])
            print(list(set(items)))
            return list(set(items))

    def linkSearch(self, type):
        local_links = []
        foreign_links = []

        input_url = self.url_entry.get()
        try:
            content = requests.get(input_url)
            soup = BeautifulSoup(content.text, 'lxml')

        except:
            return
        itemselector = soup.select('a')

        #get base URL of website - code partially copied and adapted from
        #https://medium.com/swlh/how-to-build-a-url-crawler-to-map-a-website-using-python-3e7db83feb7a
        parts = urlsplit(input_url)
        base = "{0.netloc}".format(parts)
        strip_base = base.replace("www.", "")
        base_url = "{0.scheme}://{0.netloc}".format(parts)
        path = input_url[:input_url.rfind('/')+1] if '/' in parts.path else input_url

        for each in itemselector:
            try:
                href = each.attrs['href']
            except:
                try:
                    href = each.attrs('href')
                except:
                    continue

            if href.startswith('/'): #all <a> elements with an href attribute that is a link,
                                    # but does not have the complete URL.
                                    # It starts with a bar as it is a link within the website
                link = base_url+href
                local_links.append(link)

            elif strip_base in href: #this is any href attribute that basically contains
                                    #the name of the website and the code of the domain
                local_links.append(href)

            elif not href.startswith('http'): #if it starts with any other character
                                                # that is not 'http' nor '/'
                link= path+href
                local_links.append(link)

            else:
                foreign_links.append(href)

        if type=="foreign":
            return(list(set(foreign_links)))

        elif type=="local":
            return(list(set(local_links)))

    def generalSearch(self, search_item, quantity):
        url = []

        if quantity == "main":
            url.append(self.url_entry.get())

        elif quantity == "entire":
            url = self.linkSearch("local")

        items = []
        items_dic = {}

        if len(url) ==0:
            if search_item == "linkedin":
                return items_dic
            else:
                return items
        else:
            for u in range(len(url)):
                try:
                    content = requests.get(url[u])
                    soup = BeautifulSoup(content.text, 'lxml')
                except:
                    continue

                itemselector = soup.select('a')

                for each in itemselector:
                    try:
                        i = each.attrs['href']
                        if search_item in i:
                            items.append(i)
                    except:
                        try:
                            i = each.attrs('href')
                            if search_item in i:
                                items.append(i)
                        except:
                            continue

                if search_item=='linkedin':
                    # check and save type of linkedin profile
                    user = []
                    company = []
                    group = []
                    for l in items:
                        if '/in/' in l:
                            user.append(l)

                        if '/company/' in l:
                            company.append(l)

                        if '/groups/' in l:
                            group.append(l)

                    if self.lin_user_cvalue.get() == True:
                        items_dic[search_item.capitalize() + " User"] = list(set(user))

                    if self.lin_corp_cvalue.get() == True:
                        items_dic[search_item.capitalize() + " Company"] = list(set(company))

                    if self.lin_group_cvalue.get() == True:
                        items_dic[search_item.capitalize() + " Group"] = list(set(group))

            if search_item == 'linkedin':
                return items_dic
            else:
                return list(set(items))

    def phoneSearch(self, quantity):
        url = []

        if quantity == "main":
            url.append(self.url_entry.get())

        elif quantity == "entire":
            url = self.linkSearch("local")

        phones = []
        if len(url) ==0:
            return phones

        else:
            for u in url:
                print(url.index(u), u)
                try:
                    content = requests.get(u)
                    soup = BeautifulSoup(content.text, 'lxml')
                except:
                    continue

                #Select phone number by common used class names for showing phones
                class_items = ['tel', 'Tel', 'phone', 'Phone', 'call', 'Call']

                a_selector = soup.select('a')
                for each in a_selector:
                    try:
                        href = each.attrs['href']
                    except:
                        try:
                            href = each.attrs('href')
                        except:
                            continue

                    for class_item in class_items:
                        if class_item in href:
                            print(class_item, "--->", href)
                            phones.append(href)

                #p_selector = soup.select('p')
                for class_item in class_items:
                    p_selector = soup.select('p.'+class_item)
                    for each in p_selector:
                        ph= each.text
                        print("PH", ph)
                        phones.append(ph)

            '''
            temp = ""
            for p in phones:
                for letter in p:
                    if not(letter.isalpha()):
                        temp+=letter
            phones = temp
            print(phones)
            '''
            return list(set(phones))

    def viewScrape(self, event):
        var = self.listbox.get(ACTIVE)
        if "Success" not in var:
            self.window.bell()
            return

        else:
            # create a new window for viewing scrape
            view_window = Toplevel(self.window)
            view_window.geometry("500x500")
            view_window.title(var+" - VIEW")
            view_window.configure(background="gray95")

            element = var.split("-")[0]
            scraped = self.data.get(element)
            df = pd.DataFrame(scraped)

            self.bt = Button(master=view_window, text="Save", font=self.font, fg="gray29",
                             bg="gray90", relief="raised", command= lambda: self.saveScrape(df, element))
            self.bt.grid(row=0, column=0,)

            self.bt = Button(master=view_window, font=self.font, fg="gray29", bg="gray90",
                             relief="raised", text="Exit View", command=view_window.destroy)
            self.bt.grid(row=0, column=1)

            height = 0
            width = 30
            if len(scraped)<20:
                height = 25
            elif len(scraped)<10:
                height = 15
            elif len(scraped)<5:
                height = 6
            else:
                height = int(len(scraped)/2)

            self.scrollbar_view = Scrollbar(master=view_window)
            self.scrollbar_view.grid(column=3, row=1, rowspan=3)
            self.data_list = Listbox(master=view_window, fg="gray29", bg="gray95", font=("ms serif", 12),
                                     yscrollcommand=self.scrollbar_view.set, height=height, bd=0,
                                     highlightthickness=1, highlightbackground="IndianRed2", width=width)

            self.scrollbar_view.config(bg="IndianRed2", highlightbackground="gray95",
                                       command = self.data_list.yview)

            self.data_list.grid(row=2, column=0, rowspan=2, columnspan=2, sticky="NSEW",
                                padx=5, pady=5, ipadx=5, ipady=5)

            for s in scraped:
                self.data_list.insert(END, s)

    def saveScrape(self, df, element):
        save_window = Toplevel(self.window)
        save_window.geometry("800x200")
        save_window.title(element+ " - SAVE")
        save_window.configure(background="gray95")

        self.save_entry = StringVar()
        self.s_entry = Entry(master=save_window, textvariable=self.save_entry, bg="gray90", highlightbackground="gray95")
        self.s_entry_text = "File name"
        self.s_entry.insert(0, self.s_entry_text)
        self.s_entry.grid(row=1, column=1, columnspan=3, sticky="NSEW", padx=3, pady=3)

        self.lb = Label(master=save_window, text="Enter name of your file without extension: ",
                        font=self.font, fg="gray17", bg="gray95")
        self.lb.grid(row=1, column=0, sticky="NSEW", padx=3, pady=3)

        self.bt = Button(master=save_window, text="Excel File", font=self.font, fg="gray29",
                         bg="gray90", relief="raised", command= lambda: self.saveBack("excel", self.save_entry.get(), df))
        self.bt.grid(row=2, column=3, sticky="NSEW", padx=3, pady=3)

        self.bt = Button(master=save_window, text="CSV File", font=self.font, fg="gray29",
                         bg="gray90", relief="raised", command=lambda: self.saveBack("csv", self.save_entry.get(), df))
        self.bt.grid(row=2, column=1, sticky="NSEW", padx=3, pady=3)

        self.bt = Button(master=save_window, text="Text File", font=self.font, fg="gray29",
                         bg="gray90", relief="raised", command=lambda: self.saveBack("text", self.save_entry.get(), df))
        self.bt.grid(row=2, column=2, sticky="NSEW", padx=3, pady=3)

        self.bt = Button(master=save_window, font=self.font, fg="gray29", bg="gray90",
                         relief="raised", text="Exit", command=save_window.destroy)
        self.bt.grid(row=0, column=4)

    def saveBack(self, type, name, df): #back end ANTONIO
        file = name+".csv"
        result = ""
        if type =="csv":
            try:
                df.to_csv(r"/Users/chloemartin/Downloads/Fairs/ %s" % file)
                result = "Correctly Saved"
            except:
                result = "Something went wrong when saving..."
        pass

window = Tk()
front = Front(window)
window.mainloop()