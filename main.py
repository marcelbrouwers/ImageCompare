from tkinter import *
from tkinter import filedialog
import os
from PIL import Image
import imagehash
from joblib import Parallel, delayed
import multiprocessing
import threading

orientations = [0,90,180,270]
sizeSetA = 0
sizeSetB = 0


def is_image_file(filename, extensions=['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG', '.bmp', '.BMP']):
    return any(filename.endswith(e) for e in extensions)

def vergelijkAfbeeldingen():
    global status
    global hashesSetA
    global hashesSetB
    global padA
    global padB
    global outputcsvfile
    global liveview
    global img
    global imagesProcessed
    global counter
    counter = 0

    if liveview.get() == 1:
        viewimage = 1
    else:
        viewimage = 0

    padSetA = padA
    padSetB = padB
    f = open(outputcsvfile, "w")
    setA = []
    setB = []
    hashesSetA = []
    hashesSetB = []
    for path, subdirs, files in os.walk(padSetA):
        for name in files:
            if is_image_file(name):
                setA.append(os.path.join(path, name))
    sizeSetA.set("size set A: " + str(len(setA)))
    for path, subdirs, files in os.walk(padSetB):
        for name in files:
            if is_image_file(name):
                setB.append(os.path.join(path, name))
    sizeSetB.set("size set B: " + str(len(setB)))



    def processSetA(imageA):
        global hashesSetA
        global status
        global img
        global counter
        global imagesProcessed
        loadedImageA = Image.open(imageA)
        status.set(str(imageA))

        #only setB is rotated, hence orientation is set to 0 for set A.
        orientation = 0
        rotatedImageA = loadedImageA

        if viewimage == 1:
            img.set(rotatedImageA)

        hashA = str(imagehash.phash(rotatedImageA))
        print(hashA)
        print("orientation A:" + str(orientation))
        hashesSetA.append([imageA,orientation,hashA])
        counter = counter + 1
        imagesProcessed.set(str(counter))
    Parallel(n_jobs=multiprocessing.cpu_count(), require='sharedmem')(delayed(processSetA)(imageA) for imageA in setA)

    def processSetB(imageB):
        global hashesSetB
        global status
        global img
        global counter
        global imagesProcessed
        loadedImageB = Image.open(imageB)
        status.set(str(imageB))
        for orientation in orientations:
            rotatedImageB = loadedImageB.rotate(orientation)
            if viewimage == 1:
                img.set(rotatedImageB)
            hashB = str(imagehash.phash(rotatedImageB))
            print(hashB)
            print("orientation B:" + str(orientation))
            hashesSetB.append([imageB, orientation, hashB])
        counter = counter + 1
        imagesProcessed.set(str(counter))
    Parallel(n_jobs=multiprocessing.cpu_count(), require='sharedmem')(delayed(processSetB)(imageB) for imageB in setB)

    for hashA in hashesSetA:
        tempArray = []
        for hashB in hashesSetB:
            match = imagehash.hex_to_hash(hashA[2])-imagehash.hex_to_hash(hashB[2])
            tempArray.append([float(match),hashB[0]])
        #lowest = np.min(tempArray,axis=0)
        lowest = min(tempArray)
        thresholdvalue = threshold.get()
        if lowest[0] < thresholdvalue:
            f.write(str(hashA[0]) + "," + str(lowest[1]) + "," + str(lowest[0]) + ",""\r\n")
        else:
            f.write(str(hashA[0]) + ",nomatch,nomatch,""\r\n")
        status.set(str("comparing..."))
    status.set(str("finished"))





root = Tk()
root.title('ImageCompare')
root.geometry("500x520")
def start_submit_thread():
    global submit_thread
    submit_thread = threading.Thread(target=vergelijkAfbeeldingen)
    submit_thread.daemon = True
    submit_thread.start()

def fileDialogSetA():
    global padsetA
    global padA
    padA = filedialog.askdirectory()
    padsetA.set(padA)
    countsetA=[]
    for path, subdirs, files in os.walk(padA):
        for name in files:
            if is_image_file(name):
                countsetA.append(os.path.join(path, name))
    sizeSetA.set("images in set A: " + str(len(countsetA)))

def fileDialogSetB():
    global padsetB
    global padB
    padB = filedialog.askdirectory()
    padsetB.set(padB)
    countsetB=[]
    for path, subdirs, files in os.walk(padB):
        for name in files:
            if is_image_file(name):
                countsetB.append(os.path.join(path, name))
    sizeSetB.set("images in set B: " + str(len(countsetB)))

def outputFileSet():
    global outputfilepath
    global outputcsvfile
    outputcsvfile = filedialog.asksaveasfile(mode='w', defaultextension=".csv")
    outputcsvfile = outputcsvfile.name
    outputfilepath.set(outputcsvfile)

countsetA = []
countsetB = []
sizeSetA = StringVar()
sizeSetB = StringVar()
padsetA = StringVar()
padsetB = StringVar()
status = StringVar()
outputfilepath = StringVar()
padA=""
padB=""
liveview = IntVar()
img = PhotoImage()
imagesProcessed = StringVar()


button_setA = Button(root, text="Browse...", command=fileDialogSetA)
label_1 = Label(root, text="set A: ")
label_padsetA = Label(root, textvariable=padsetA)
label_1.grid(row=0, sticky=W)
button_setA.grid(row=0,column=1, sticky=W)
label_padsetA.grid(row=1, sticky=W)
label_sizeSetA = Label(root, textvariable=sizeSetA)
label_sizeSetA.grid(row=2, sticky=W)

button_setB = Button(root, text="Browse...", command=fileDialogSetB)
label_2 = Label(root, text="set B: ")
label_padsetB = Label(root, textvariable=padsetB)
label_2.grid(row=3, sticky=W)
button_setB.grid(row=3, column=1, sticky=W)
label_padsetB.grid(row=4, sticky=W)
label_sizeSetB = Label(root, textvariable=sizeSetB)
label_sizeSetB.grid(row=5, sticky=W)

c = Checkbutton(root, text="Live view images (recommended = off)", variable=liveview)
#c.grid(row=7, columnspan=2, sticky=W, padx=10, pady=10)

button_OutputFile = Button(root, text="Output file...", command=outputFileSet)
label_OutputFile = Label(root, text="Output file: ")
label_OutputFilePath = Label(root, textvariable=outputfilepath)

button_OutputFile.grid(row=8, sticky=W, padx=10, pady=10)

label_OutputFile.grid(row=9, sticky=W, padx=10, pady=10)
label_OutputFilePath.grid(row=10, columnspan=2, sticky=W, padx=10, pady=10)

label_Threshold = Label(root, text="Threshold (recommended = 10):")
label_Threshold.grid(row=11, sticky=W)

threshold = Scale(root, from_=0, to=30, tickinterval=2, orient=HORIZONTAL, length = 300)
threshold.set(10)
threshold.grid(row=12, sticky=W, padx=10, pady=10)

button_start = Button(root, text="Start", command=start_submit_thread)
button_start.grid(row=13, sticky=W, padx=10, pady=10)

status_bar = Label(root, textvariable=status, bd=1, relief=SUNKEN, anchor=W)
status_bar.grid(row=14, sticky=NSEW, columnspan=2, padx=10, pady=10)


label_imagesProcessed = Label(root, text="images processed: ")
label_imagesProcessedCounter = Label(root, textvariable=imagesProcessed)

label_imagesProcessed.grid(row=15, sticky=W)
label_imagesProcessedCounter.grid(row=16, sticky=W)


footer = Label(root, text="ImageCompare; Marcel Brouwers - Maastricht University")
footer.grid(row=18)

root.mainloop()