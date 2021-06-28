from threading import Thread
import Tweet_Impact as replies
import PySimpleGUI as sg
import requests
import validators
import base64

# Add some color
# to the window
from PIL import ImageTk, ImageSequence

sg.theme('DarkTanBlue')


def loading_sus_screen():
    with open("loading_sus.gif", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    # Next demo is to show how to create custom windows with animations
    layout = [[sg.Image(data=encoded_string, enable_events=True, background_color='white', key='-IMAGE-',
                        right_click_menu=['UNUSED', ['Exit']])], ]

    window = sg.Window('Loading...', layout,
                       grab_anywhere=True,
                       keep_on_top=True,
                       background_color='white',
                       alpha_channel=0.5,
                       margins=(0, 0))

    offset = 0
    gif = encoded_string
    while True:  # Event Loop
        event, values = window.read(
            timeout=0)  # loop every 10 ms to show that the 100 ms value below is used for animation
        if event in (sg.WIN_CLOSED, 'Exit', 'Cancel'):
            break
        # update the animation in the window
        window['-IMAGE-'].update_animation(gif, time_between_frames=1000)


def loading_screen():
    with open("loading_sus.gif", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    layout = [[sg.Text('Loading....', font='ANY 15')],
              [sg.Image(data=encoded_string, key='_IMAGE_')]
              ]

    window = sg.Window('Loading...').Layout(layout)

    while True:  # Event Loop
        event, values = window.Read(timeout=0.)
        if event in (None, 'Exit', 'Cancel'):
            break
        window.Element('_IMAGE_').UpdateAnimation(encoded_string, time_between_frames=25)


def open_window():
    layout = [[sg.Text("New Window", key="new")]]
    window = sg.Window("Second Window", layout, modal=True)
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
    window.close()


def loading_search(url):
    sus = Thread(target=loading_sus_screen())
    data = Thread(target=replies.main(url))
    sus.start()
    data.start()
    sus.join()
    data.join()


def main():
    layout = [
        [[sg.Text('Welcome to Tweet Impact Software!'), sg.Text(""), sg.Text(size=(15, 1), key='-Warning')]],
        [sg.Text('Input a Tweet Link to get data from it: '), sg.InputText(key='-IN')],
        [[sg.Button("Search", key="open"), sg.Button("Close", key="Exit")]]
    ]
    window = sg.Window("Tweet Impact", layout)
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        if event == "open":
            try:
                HEADERS = {
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
                }
                # html = requests.get("https://twitter.com/NintendoUK/status/1386953264055218177",timeout=5, headers=HEADERS)
                requests.get(values['-IN'], timeout=5, headers=HEADERS)
                # loading_screen()
                loading_search(values['-IN']) #Sustituir
                break
            except:
                window['-Warning'].update("URL not valid or not possible connection to the tweet. Try another tweet.")
        if event == "loading":
            pass
            # loading_sus_screen()
    window.close()


if __name__ == "__main__":
    main()
