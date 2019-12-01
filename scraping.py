from tkinter import *
from PIL import ImageTk, Image
from selenium import webdriver
from bs4 import BeautifulSoup as bs
from subprocess import call
import requests
from bs4 import BeautifulSoup
from time import sleep
#import urllib.request
from urllib.parse import urlsplit, urlparse
from collapsiblepane import CollapsiblePane as cp
import upsidedown

class Front(object):
    def __init__(self, window):
        self.window = window
        self.window.title("Antonio Colmenares & Chloe Martin - Automated Scraping")
        self.window.configure(background="gray95")
        self.font = ("ms serif", 16)

        furthest_label_column=12

        self.exit_bt = Button(master=self.window, text="Exit", fg="black", highlightbackground='red',
                              highlightthickness=2, font=self.font, command=sys.exit)
        self.exit_bt.grid(row=0, column=furthest_label_column, sticky = "E")

        self.webFrame = Frame(master=self.window, padx=5, pady=5, bg="gray95")
        self.webFrame.grid(row=1, column=1, columnspan=furthest_label_column, rowspan=2, sticky="NSEW")
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

        self.bt = Button(self.webFrame, text="Search", fg="gray29", bg="gray90", relief = "raised",
                         font=self.font, command=self.openWebsite)
        self.bt.grid(row=2, column=furthest_label_column, sticky="NSEW")

    def openWebsite(self):
        if self.url_entry.get()== self.entry_text or self.url_entry.get() == "":
            return
        else:
            '''
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
            '''

            #display website screenshot on canvas
            self.canvas = Canvas(master=self.window, width=512, height=320, bg="gray95")
            screenshot = Image.open("screenshot.jpg")
            size = 512, 320
            screenshot.thumbnail(size)
            self.canvas.image = ImageTk.PhotoImage(screenshot)

            self.canvas.create_image(259, 3, image=self.canvas.image, anchor="n")
            self.canvas.grid(row=3, column=1, columnspan=7, rowspan=5, padx=5, pady=5, sticky="NSEW")

            #user URL validation
            self.val_bt = Button(master=self.window, text="Validate", fg="gray29", font=self.font,
                             command=self.showOptions)
            self.val_bt.grid(row=10, column=4, sticky="NSEW")

    def clearWebsiteEntry(self, event):
        self.url_entry.delete(0, END)

    def clearAll(self):
        pass

    def showOptions(self):
        self.val_bt.destroy()

        option_row = 10

        self.options = Frame(master=self.window, padx=5, pady=5, bg="gray95")
        self.options.grid(row=option_row, column=1, rowspan=20, columnspan=1)

        self.bt = Button(self.options, text="Scrape", fg="gray29", bg="gray90", relief = "raised",
                         font=self.font, command=self.executeScrape)
        self.bt.grid(row=option_row+10, column=1)

        #get emails
        self.all_email_cvalue = BooleanVar()
        self.email_checkbox = Checkbutton(self.options, text="", font=self.font,
                                          fg="gray29", bg="gray95", highlightbackground="gray95",
                                          variable = self.all_email_cvalue)
        self.email_checkbox.grid(row=option_row, column=0, sticky="W")

        self.cpane = cp(self.options, "Get emails", "Get emails")
        self.cpane.grid(row=option_row, column=1, sticky="W", columnspan=2)

        self.all_email_checkbox = Checkbutton(self.cpane.frame, text="From the entire website", font=self.font,
                                              fg="gray29", bg="gray95", highlightbackground="gray95",
                                              variable=self.all_email_cvalue)
        self.all_email_checkbox.grid(row=option_row + 1, column=3, sticky="NSW")

        # get linkedin urls from main url page
        self.lin_cvalue = BooleanVar()
        self.lin_checkbox = Checkbutton(self.options, text="Get linkedin URL profiles from main", font=self.font,
                                          fg="gray29", bg="gray95", highlightbackground="gray95",
                                          variable=self.lin_cvalue, command=self.linkedinMoreOptions)
        self.lin_checkbox.grid(row=option_row+2, column=2, sticky="NSW")

        # get twitter urls from main url page
        self.tw_cvalue = BooleanVar()
        self.tw_checkbox = Checkbutton(self.options, text="Get twitter URL profiles from main", font=self.font,
                                        fg="gray29", bg="gray95", highlightbackground="gray95",
                                        variable=self.tw_cvalue)
        self.tw_checkbox.grid(row=option_row + 2, column=2, sticky="NSW")

        # get facebook urls from main url page
        self.fb_cvalue = BooleanVar()
        self.fb_checkbox = Checkbutton(self.options, text="Get facebook URL profiles from main", font=self.font,
                                       fg="gray29", bg="gray95", highlightbackground="gray95",
                                       variable=self.fb_cvalue)
        self.fb_checkbox.grid(row=option_row + 3, column=2, sticky="NSW")

        # get instagram profile urls from main
        self.in_cvalue = BooleanVar()
        self.in_checkbox = Checkbutton(master=self.options, text="Get instagram URL profiles from main", font=self.font,
                                       fg="gray29", bg="gray95", highlightbackground="gray95",
                                       variable=self.in_cvalue)
        self.in_checkbox.grid(row=option_row + 4, column=2, sticky="NSW")

        # get foreign URLs
        self.foreign_cvalue = BooleanVar()
        self.foreign_checkbox = Checkbutton(self.options, text="Get all foreign URLs", font=self.font,
                                        fg="gray29", bg="gray95", highlightbackground="gray95",
                                        variable=self.foreign_cvalue)
        self.foreign_checkbox.grid(row=option_row + 5, column=2, sticky="NSW")

        # get all local URLs
        self.local_cvalue = BooleanVar()
        self.local_checkbox = Checkbutton(self.options, text="Get all local URLs", font=self.font,
                                         fg="gray29", bg="gray95", highlightbackground="gray95",
                                         variable=self.local_cvalue)
        self.local_checkbox.grid(row=option_row+6, column=2, sticky="NSW")

        # get all location urls from main
        self.geo_cvalue = BooleanVar()
        self.geo_checkbox = Checkbutton(self.options, text="Get Google Maps location coordinate URL", font=self.font,
                                         fg="gray29", bg="gray95", highlightbackground="gray95",
                                         variable=self.geo_cvalue)
        self.geo_checkbox.grid(row=option_row+7, column=2, sticky="NSW")

        # get all phone numbers
        self.ph_cvalue = BooleanVar()
        self.ph_checkbox = Checkbutton(self.options, text="Get phone numbers",
                                        font=self.font,
                                        fg="gray29", bg="gray95", highlightbackground="gray95",
                                        variable=self.ph_cvalue)
        self.ph_checkbox.grid(row=option_row + 8, column=2, sticky="NSW")


    def linkedinMoreOptions(self):
        #create a new window for choosing options
        new_window = Toplevel()
        new_window.geometry("400x300")
        new_window.title("Linkedin Scrape Options")
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

    def executeScrape(self):
        '''
        email = []
        linkedin = []
        twitter = []
        facebook = []
        urls = []
        href = []
        all_email = []
        '''

        if self.email_cvalue.get()==True:
            self.atSearch("email")

        if self.lin_cvalue.get() == True:
            self.generalSearch("linkedin")

        if self.tw_cvalue.get() == True:
            self.generalSearch("twitter")

        if self.fb_cvalue.get() == True:
            self.generalSearch("facebook")

        if self.in_cvalue.get() == True:
            self.generalSearch("instagram")

        if self.foreign_cvalue.get() == True:
            self.linkSearch("foreign")

        if self.local_cvalue.get() == True:
            self.linkSearch("local")

        if self.geo_cvalue.get() == True:
            self.atSearch("location")

        if self.ph_cvalue.get() == True:
            self.phoneSearch()

    def atSearch(self, search_item):
        items = []

        content = requests.get(self.url_entry.get())
        soup = BeautifulSoup(content.text, 'lxml')
        itemselector = soup.select('a')

        for each in itemselector:
            i = each.attrs['href']
            if "@" in i:
                items.append(i)

        for item in items:
            if search_item=='location':
                if 'google' and 'maps' not in item:
                    items.remove(item)
            elif search_item=='email': #CHECK SI EL EMAIL ES VALIDO ANTONIO
                if 'google.com/maps/place' in item:
                    items.remove(item)

                # only keep emails (with no "mailto:" text at the beginning)
                if 'mailto:' in item:
                    email_index = items.index(item)
                    items.remove(item)
                    temp = item.split(':')
                    items.insert(email_index, temp[1])

    def generalSearch(self, search_item):
        items = []
        items_dic = {}

        content = requests.get(self.url_entry.get())
        soup = BeautifulSoup(content.text, 'lxml')
        itemselector = soup.select('a')

        for each in itemselector:
            i = each.attrs['href']
            if search_item in i:
                items.append(i)

        if search_item=='linkedin':
            # check and save type of linkedin profile
            for l in items:
                if self.lin_user_cvalue.get() == True:
                    if '/in/' in l:
                        items_dic = {search_item.capitalize()+" User": l}
                if self.lin_corp_cvalue.get() == True:
                    if '/company/' in l:
                        items_dic = {search_item.capitalize()+"Company": l}
                if self.lin_group_cvalue.get() == True:
                    if '/groups/' in l:
                        items_dic = {search_item.capitalize()+"Group": l}

            return items_dic

        print(items)
        return items

    def phoneSearch(self):
        phones = []

        content = requests.get(self.url_entry.get())
        soup = BeautifulSoup(content.text, 'lxml')

        #Select phone number by common used class names for showing phones
        class_items = ['tel', 'phone']

        a_selector = soup.select('a')
        for each in a_selector:
            href = each.attrs['href']

            for class_item in class_items:
                if class_item in href:
                    phones.append(href)

        #p_selector = soup.select('p')
        for class_item in class_items:
            p_selector = soup.select('p.'+class_item)

            for each in p_selector:
                ph= each.text
                phones.append(ph)

        print(phones)

        '''
        area_code = 43
        with urllib.request.urlopen(self.url_entry.get()) as open_website:
            content = open_website.read().decode('utf-8')
        phones = re.findall(r"\+\d{2}\s?0?\d{10}", content)
        phones2 = re.compile()
        #phones2 = re.findall(r"(?:1[-.])*(?[2-9]\d{2})?[-. ]\d{3}[-. ]\d{4}", content)
        print(phones, phones2)
        '''

    def linkSearch(self, type):
        local_links = []
        foreign_links = []

        input_url = self.url_entry.get()
        content = requests.get(input_url)
        soup = BeautifulSoup(content.text, 'lxml')
        itemselector = soup.select('a')

        #get base URL of website - code partially copied and adapted from
        #https://medium.com/swlh/how-to-build-a-url-crawler-to-map-a-website-using-python-3e7db83feb7a
        parts = urlsplit(input_url)
        base = "{0.netloc}".format(parts)
        strip_base = base.replace("www.", "")
        base_url = "{0.scheme}://{0.netloc}".format(parts)
        path = input_url[:input_url.rfind('/')+1] if '/' in parts.path else input_url

        for each in itemselector:
            href = each.attrs['href']

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
            print(foreign_links)
            return foreign_links

        elif type=="local":
            print(local_links)
            return local_links

    def searchAllEmails(self):
        pass

    def searchHelp(self):
        pass


window = Tk()
front = Front(window)
window.mainloop()

'''
        #show complete URL
        url_label = "URL: "+self.url_entry.get()
        self.lb = Label(master=self.window, text=url_label, font=self.font, fg="gray29", bg="gray95")
        self.lb.grid(row=9, column=1, sticky="W")
'''