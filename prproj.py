import customtkinter

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")

from sqlite3 import *

con = connect("items.db")
curs = con.cursor()
curs.execute("""CREATE TABLE IF NOT EXISTS ITEMS_TO_CHECK(
    linkToItem TEXT,
    worthOfItem NUM,
    description TEXT
)""")

app = customtkinter.CTk()
app.geometry("512x512")

scroll_frame = customtkinter.CTkScrollableFrame(master=app, width=400, height=300)
scroll_frame.place(relx=0.5, rely=0.2, anchor=customtkinter.CENTER)


def addLink(link1, worth1, desc1):
    curs.execute("INSERT INTO ITEMS_TO_CHECK (linkToItem, worthOfItem, description) VALUES (?,?,?)",
                 (link1, worth1, desc1))

    con.commit()


def button_function():
    linkApplyer = customtkinter.CTk()
    linkApplyer.geometry("512x512")
    link = customtkinter.CTkTextbox(master=linkApplyer, width=100, corner_radius=0, text="past link here")
    link.place(relx=0.1, rely=0.2, anchor=customtkinter.CENTER)

    worthnes = customtkinter.CTkTextbox(master=linkApplyer, width=100, corner_radius=0, text="your wished price")
    worthnes.place(relx=0.5, rely=0.2, anchor=customtkinter.CENTER)

    desc = customtkinter.CTkTextbox(master=linkApplyer, width=100, corner_radius=0, text="description")
    desc.place(relx=0.9, rely=0.2, anchor=customtkinter.CENTER)

    button1 = (customtkinter.CTkButton
        (
        master=linkApplyer,
        text="add link",
        command=lambda: addLink(
            link1=link.get("0.0", "end"),
            worth1=worthnes.get("0.0", "end"),
            desc1=desc.get("0.0", "end")
        )))
    button1.place(relx=0.5, rely=0.8, anchor=customtkinter.CENTER)

    linkApplyer.geometry("512x512")
    linkApplyer.mainloop()


import webbrowser


def goToPage(url):
    webbrowser.open_new_tab(url)


import io
import requests
from PIL import Image


def toShow(itemData):
    row = customtkinter.CTkFrame(master=scroll_frame)
    row.pack(fill="x", pady=5)

    price = customtkinter.CTkLabel(master=row, text=itemData[0])
    imgUrl = itemData[1]
    resp = requests.get(imgUrl)
    imgToShow = customtkinter.CTkImage(light_image=Image.open(io.BytesIO(resp.content)),
                                       dark_image=Image.open(io.BytesIO(resp.content)),
                                       size=(200, 200))
    image_label = customtkinter.CTkLabel(master=row, image=imgToShow, text="")
    buttonLink = customtkinter.CTkButton(master=row, text="check page", command=lambda: goToPage(itemData[2]))
    image_label.pack(side="left")
    price.pack(side="left")
    buttonLink.pack(side="right")


import nodriver as uc
import asyncio
import os
import shutil
from re import finditer

patternCost = "([1-9]+ )*([0-9]+ ₽)"
patternPic = r"https?://[^\s\"']+\.(?:jpg|jpeg|png|webp)"


async def checkWorth(url_string):
    live_user_data = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data')
    bot_user_data = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data Bot')

    if not os.path.exists(bot_user_data):
        print("Cloning your personal Chrome profile for the bot... Please wait.")
        try:
            os.makedirs(os.path.join(bot_user_data, "Default"), exist_ok=True)
            files_to_copy = ['Network', 'Cookies', 'Login Data', 'Local Storage', 'Secure Preferences']
            live_default_path = os.path.join(live_user_data, "Default")
            bot_default_path = os.path.join(bot_user_data, "Default")

            for item in os.listdir(live_default_path):
                if item in files_to_copy or "Preferences" in item:
                    src = os.path.join(live_default_path, item)
                    dst = os.path.join(bot_default_path, item)
                    if os.path.isdir(src):
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                    else:
                        shutil.copyfile(src, dst)
            print("Profile successfully cloned!")
        except Exception as e:
            print(f"Note: Some profile files were locked, skipping them: {e}")

    browser = await uc.start(
        user_data_dir=bot_user_data,
        headless=False,
        sandbox=False
    )

    page = await browser.get(url_string)
    await page.sleep(1)
    htmll = await page.get_content()
    for i in finditer(patternCost, htmll):
        curPrice = str(i.group())
        break
    for i in finditer(patternPic, htmll):
        curImg = str(i.group())
        break
    toShow([curPrice, curImg, url_string])
    browser.stop()


def checkData():
    curs.execute("SELECT * FROM ITEMS_TO_CHECK")

    for widget in scroll_frame.winfo_children():
        widget.destroy()

    datta = curs.fetchall()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    for line in datta:
        url = line[0]
        if url.startswith("http"):
            loop.run_until_complete(checkWorth(url))


buttonAdd = customtkinter.CTkButton(master=app, text="add link", command=button_function)
buttonAdd.place(relx=0.25, rely=0.5, anchor=customtkinter.CENTER)

buttonCheck = customtkinter.CTkButton(master=app, text="check prices", command=lambda: checkData())
buttonCheck.place(relx=0.75, rely=0.5, anchor=customtkinter.CENTER)

app.mainloop()

con.close()
