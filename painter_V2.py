import requests
import pyautogui
import re
import json
import os
import time
import shutil
import keyboard
from subprocess import Popen
from PIL import Image, ImageColor


class PAINTER:
    # Create func that get positions in painter class
    def get_position(self, url, where, colors, how):
        if where == 'net': # If image from internet download it
            try:
                print("downloading image...")
                resp = requests.get(url)
                resp.raise_for_status()
            except:
                print("Couldn't download this image....")
                time.sleep(2)
                return start()

            name = input("Enter image name: ") + '.png'
            image = open(name, 'wb')
            print(f"Downloading {name}")
            for chunk in resp.iter_content(100000): # Download image
                image.write(chunk)
            
            image.close()
        
        else: # If image in divce get Image name
            name = re.compile(r'.*\\(.*\..*)').findall(url)[-1]

        try:
            try:
                draw = Image.open(name) # Try to open image if it in the cwd.
            except:
                draw = Image.open(url) # If it's not in cwd.
        
        except: 
            print("This image not found!!")
            return start()

        try:
            os.makedirs('.\\paints')
        
        except:
            pass

        os.chdir('.\\paints')
        try:
            shutil.copy(url, name)
        except:
            pass
        
        
        width, height = draw.size # Get image size

        axiyX, axiyY = pyautogui.size() # Get os size
        axiyX = axiyX - 4 # Subtract the bar size
        axiyY = axiyY - 194 # subtract the paint bar
        ratioW, ratioH = 1, 1 # Add ratio to width and height
        if  width > axiyX:
            ratioH =  width // axiyX # Save new height ratio
            width = axiyX # Save new width size
        
        if height > axiyY:
            ratioW = height // axiyY # Save new width ratio
            height = axiyY # Save new height ratio

        draw = draw.resize((width * ratioW, height * ratioH)) # Resize the image the make it fit to paint board
        pixelPose = [] # Save pixel poses and colors
        pixelPoseJSON = open(name + '.json', 'w') # Make json file to store data
        print("Geting drawing data...")
        cont = 0
        # Check if the users want to ignore the color that he entred
        op = int(input("Do you want the color you entered to be skiped[0] or to be drawed[1]: "))
        for color in colors:
            # Get color range
            if not(how[cont]): tend = int(input("Enter number will be range to compare the colors:"))
            try:
                color = eval(color) # check if user inter a list of color
                if len(tuple(set(color))) == 1: # if red = blue = green 
                    color = color[0]
            except NameError: # If user enter color name get color rgb.
                color = ImageColor.getrgb(color)
            pixelPose.append(color) # Save color

            # Analyzing colors of pixels in image
            for x in range(width):
                for y in range(height):
                    pixelRGB = draw.getpixel((x, y)) # Get pixel color in (x, y) position
                    if type(pixelRGB) == int == type(color): # If the color is not tuple
                        if how[cont]: # If user want to get the color with out range
                            if pixelRGB == color and op: # Add given colors
                                pixelPose.append((x, y))
                            
                            elif pixelRGB != color and not(op): # skip given colors
                                pixelPose.append((x, y))
                        else: # with range
                            if pixelRGB in range(color - tend, color + tend) and op: # add color
                                pixelPose.append((x, y))
                            
                            elif pixelPose in range(color - tend, color + tend) and not(op): # skip color
                                pixelPose.append((x, y))
                    elif type(pixelRGB) == tuple == type(color): # If the color is tuple 
                        if how[cont]: # without range
                            if pixelRGB == color and op: # add color
                                pixelPose.append((x, y))
                            
                            elif pixelRGB != color and not(op): # skip color
                                pixelPose.append((x, y))

                        else: # with range
                            # add color if rgb of the pixel in the given range
                            add = [True for i in range(3) if pixelRGB[i] in range(color[i] - tend, color[i] + tend)]
                            if len(add) == 3 and op: # add color
                                pixelPose.append((x, y))
                            
                            elif len(add) != 3 and not(op): # skip color
                                pixelPose.append((x, y))
            
            cont += 1 # Go to the next color range
        if len(pixelPose) == len(colors): # If no pixels found with the given colors
            print("No data pixel found with the specified colors")
            os.remove(name + 'json')
        
        else: # If there is pixel ...
            pixelPoseJSON.write(json.dumps(pixelPose)) # Save data to json file
            pixelPoseJSON.close()
            print(f"All data is saved, you can now draw {name.replace('.png', '')}")
    
    # Create drawer func
    def draw_image(self):
        try: os.chdir('.\\paints') # Try to change the dirctory
        except FileNotFoundError: pass
        # Get image that can be drawed
        paints = [name for name in os.listdir() if name.endswith('.json')]
        print("Choose image to draw:")
        for paint in range(len(paints)):
            if paints[paint].endswith('backup.json'): # skip backup data
                continue

            print(f"\t*[{paint + 1}] {paints[paint].split('.')[0]}.") # Print choose
        
        choose = paints[int(input('\t*[choose]=> ')) - 1] # Get wanted draw
        try:
            # search for backup file to the selected image.
            pixelPoseJson = open(choose.replace('.json', 'backup.json'))
            # If there is no error that mean the backup is found.
            print("Backup point found!!")
            # If user want to continue else rise error.
            assert int(input("Do you want to continue from backup point[1] or no[0]:"))
            print("Getting bakup point...")
            pixelPose = json.loads(pixelPoseJson.read()) # Add backup data
            pixelPoseJson.close()
            boardName = pixelPose[0] # Get Image name
            del pixelPose[0] # Delete image name
            board = Image.open(boardName) # Open image
        
        except: # If there is no backup or user want to start again
            pixelPoseJson = open(choose) # Open the choosen file
            pixelPose = json.loads(pixelPoseJson.read()) # add data
            pixelPoseJson.close()
            width, height = 0, 0
            for pose in pixelPose: # searching for the larges pixel poseition
                if type(pose) == int or len(pose) == 3: continue # If it a color skip
                
                if pose[0] > width: width = pose[0] # If pixel axiyX bigger then width add it as the new width
                
                if pose[1] > height: height = pose[1] # If pixel axiyY bigger then height add it as the new height

            board = Image.new('RGB', (width, height)) # Open a board
            boardName = choose.split('.')[0] + '.png' # Get image name
            board.save(boardName) # save the board with the name
            
        print("While drawing if you want to stop, prees [q], the drawing will be stoped and backup file will be made.")
        replColor = int(input("To replace draw color enter[1], no enter[0]: "))
        if replColor: # If user want to change the colors
            for pos in range(len(pixelPose)):
                if type(pixelPose[pos]) == int or len(pixelPose[pos]) == 3: 
                    # If it a color get the new color as rgb
                    newColor = input(f'Enter new color of {pixelPose[pos]}: ')
                    
                    if type(newColor) == str: newColor = ImageColor.getrgb(newColor)
                    # If it a color as string name get the rgb
                    
                    pixelPose[pos] = newColor # Add the new color
            print("All colors replaces")
        
        # If user want to draw with paint
        if int(input("To draw the image with paint enter[1], to draw it faster without paint (low quality) enter[0]: ")):
            # Open paint
            Popen(['C:\\Windows\\system32\\mspaint.exe', boardName])
            time.sleep(1)
            
            # This func change drawing color
            def get_color(color):
                pyautogui.PAUSE = 0.2
                pyautogui.click(colPos[0], colPos[1]) # Click color editor
                if type(color) == int: color = [color] * 3 # If color is intger make it as a list
                pyautogui.hotkey('shift', 'tab')
                pyautogui.hotkey('shift', 'tab')
                # Go to blue fild and add the rate
                pyautogui.typewrite(str(color[2]))
                pyautogui.hotkey('shift', 'tab')
                # Go to green filed and add the rate
                pyautogui.typewrite(str(color[1]))
                pyautogui.hotkey('shift', 'tab')
                # Go to red filed and add the rate
                pyautogui.typewrite(str(color[0]))
                # Save the color
                pyautogui.press('enter')
                pyautogui.PAUSE = 10 ** (-300) # Change the speed
                return color

            backupColor = None # Save what the current color
            # Get the position of the borad in paint (doesn't work with the rtl os) and
            loc = list(pyautogui.locateOnScreen('..\\start.png')); loc[0] += 5; loc[1] += 145
            if not(loc): loc = [7, 144] # If os is ltr. this is a random positions.
            # Get the color editor position in paint
            colPos = pyautogui.locateOnScreen('..\\color.png')
            for pos in range(len(pixelPose)):
                if keyboard.is_pressed('q'): # If users want to stop drawing
                    # Crate a backup.json file
                    backupFile = open(choose.replace('.json', 'backup.json'), 'w')
                    # Save the remaining pixels
                    backupData = pixelPose[pos:]
                    backupData.insert(0, backupColor) # Insert the current color
                    backupData.insert(0, boardName) # insert the current image name
                    backupFileJson = json.dumps(backupData) # Change the python data to js data
                    backupFile.write(backupFileJson)# Save the backup to json file
                    backupFile.close()
                    break
                
                pos = pixelPose[pos]
                try:

                    if len(pos) == 3: backupColor = get_color(pos) # If color
                    elif len(pos) == 2: pyautogui.click(pos[0] + loc[0], pos[1] + loc[1]) # If position of pixel
                except: 
                    backupColor = get_color(pos) # If it int value (color with rgb with same rate)

                if pos == pixelPose[-1]: # If all done delete the backup if it there
                    try: os.remove(choose.replace('.json', 'backup.json'))
                    except: pass

            pyautogui.hotkey('ctrl', 's') # Save the image
        
        else: # If users chose draw without paint it will draw with pillow.
            color = 0
            for pos in pixelPose:

                try:
                    if len(pos) == 3: # If it a color
                        color = pos
                    
                    else: # if it a position
                        try: board.putpixel((pos[0], pos[1]), tuple(color)) # draw the pixel with the current color
                        except: pass
                
                except:
                    color = [pos] * 3 # If it a color rgb with the same rate "0 convert (0, 0, 0)"
            board.save(boardName) # Save the image
            board.show() # show the image
        



def start():
        print("""\
        \t___________________________________
        \t|            ___________           |
        \t|           |PAINTER BOT|          |
        \t|           -------------          |
        \t|           | By ZAHIR  |          |
        \t|           -------------          |
        \t|__________________________________|
        """)
        option = ''
        try:
            # Check if there is an old data and add new option.
            if [i for i in os.listdir('.\\paints\\') if i.endswith('.json')]:
                option = '\t*[S] Start drawing.\n'
        except: pass
        
        # Get user choose
        start = input(f"{option}\t*[A] Add a draw.\n\t*[X] Exit.\n\t[choose]=> ").upper()
        # Make a new object
        draw = PAINTER()
        if start == 'S':
            # Call draw func
            draw.draw_image()
        
        elif start == 'A':
            print("You can add image from internet or from your dives (c:\\users\\name\\desktop\\image_name.png)")
            # Get image address
            url = input("Enter draw address: ")
            colors = [] # Colors data
            how = [] # Store is user wanna to range the color
            print("You can and more then one color.")
            while True:
                try:
                    color = input("[ctrl + c] to stop adding colors.\nEnter color name 'black', or color RGB (0, 0, 0): ")
                    colors.append(color) # Add color
                    how.append(int(input(f"Do you wnat to get the {color} precisely [1] or no [0]: ")))
                except KeyboardInterrupt:
                    break
            
            # Get image src is it net or divce
            where = input("\nThis image in your pc or from internet: [pc/net]=> ").lower()
            # Call func that get color position
            draw.get_position(url, where, colors, how)
        
        elif start == 'X':
            # Quit
            print("Salam!!")
            time.sleep(1)
            quit()
        
        # Go back if the code is end.
        os.chdir('..\\')
        os.system('cls')


if __name__ == "__main__":
    while True:
        # Run the code
        start()