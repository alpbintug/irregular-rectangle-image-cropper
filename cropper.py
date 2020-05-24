#Some variable and button names are in Turkish and some functions are not explained, will be fixed later

import tkinter as tk
from tkinter import Label,Tk
from PIL import Image, ImageTk
from tkinter import filedialog
import cv2
from tkinter import messagebox
import os.path
import imutils
import numpy as np


root = tk.Tk()
image = []
rectList = []
lineList = []
wrapped = []

canvas_width = 600
canvas_height = 400
w = canvas_width // 2
h = canvas_height // 2
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)

def noktaSirala(noktalar):
	# initialzie a list of coordinates that will be ordered
	# such that the first entry in the list is the top-left,
	# the second entry is the top-right, the third is the
	# bottom-right, and the fourth is the bottom-left
	rect = np.zeros((4, 2), dtype = "float32")
	# the top-left point will have the smallest sum, whereas
	# the bottom-right point will have the largest sum
	s = np.sum(noktalar,axis = 1)
	rect[0] = noktalar[np.argmin(s)]
	rect[2] = noktalar[np.argmax(s)]
	# now, compute the difference between the points, the
	# top-right point will have the smallest difference,
	# whereas the bottom-left will have the largest difference
	diff = np.diff(noktalar, axis = 1)
	rect[1] = noktalar[np.argmin(diff)]
	rect[3] = noktalar[np.argmax(diff)]
	
	# return the ordered coordinates
	return rect

def dikdortgeneDonustur(pts):
	# obtain a consistent order of the points and unpack them
	# individually
	rect = noktaSirala(pts)
	(tl, tr, br, bl) = rect
	# compute the width of the new image, which will be the
	# maximum distance between bottom-right and bottom-left
	# x-coordiates or the top-right and top-left x-coordinates
	widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
	widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
	maxWidth = max(int(widthA), int(widthB))
	# compute the height of the new image, which will be the
	# maximum distance between the top-right and bottom-right
	# y-coordinates or the top-left and bottom-left y-coordinates
	heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
	heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
	maxHeight = max(int(heightA), int(heightB))
	# now that we have the dimensions of the new image, construct
	# the set of destination points to obtain a "birds eye view",
	# (i.e. top-down view) of the image, again specifying points
	# in the top-left, top-right, bottom-right, and bottom-left
	# order
	dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype = "float32")
	# compute the perspective transform matrix and then apply it
	M = cv2.getPerspectiveTransform(rect, dst)
	print(M)
	print((maxWidth, maxHeight))

	warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
	# return the warped image
	return warped

def resimKirp(canvas):
	point0 = canvas.coords(rectList[0])
	point0 = ((point0[0]+point0[2])/2,(point0[1]+point0[3])/2)
	point1 = canvas.coords(rectList[1])
	point1 = ((point1[0]+point1[2])/2,(point1[1]+point1[3])/2)
	point2 = canvas.coords(rectList[2])
	point2 = ((point2[0]+point2[2])/2,(point2[1]+point2[3])/2)
	point3 = canvas.coords(rectList[3])
	point3 = ((point3[0]+point3[2])/2,(point3[1]+point3[3])/2)
	global wrapped
	wrapped = dikdortgeneDonustur([point0,point1,point2,point3])
	
	#Converting numpy array into Image
	b,g,r = cv2.split(wrapped)
	im = cv2.merge((r,g,b))
	img = Image.fromarray(im)
	tkimage = ImageTk.PhotoImage(img)
	canvas.config(height = wrapped.shape[0],width = wrapped.shape[1])
	canvas.create_image(0,0,anchor = "nw",image = tkimage)
	canvas.image = tkimage
	global butonResimKirp
	butonResimKirp.configure(text = "Save Image", command = resimKaydet)
def resimAc(canvas,butonKirp):
	rectList.clear()
	lineList.clear()
	path=filedialog.askopenfilename(filetypes=[("Image File",'.jpg'),("Image File",'.png'),("Image File",'.jpeg')])
	if(os.path.isfile(path) == False):
		messagebox.showerror("Hata", "Resim Açılamadı")
		return
	global image
	image = cv2.imread(path)
	sizeX, sizeY,_ = image.shape
	if(sizeX > 720):
		image = imutils.resize(image,height = 720)
	elif(sizeY > 1280):
		image = imutils.resize(image, width = 1280)

	
	b,g,r = cv2.split(image)
	im = cv2.merge((r,g,b))
	img = Image.fromarray(im)
	tkimage = ImageTk.PhotoImage(img)
	canvas.config(height = image.shape[0],width = image.shape[1])
	canvas.create_image(0,0,anchor = "nw",image = tkimage)
	canvas.image = tkimage
	l1 = canvas.create_line(0,0,0,image.shape[0], fill = "blue", width = 5, tags = "r1r3")
	lineList.append(l1)
	l2 = canvas.create_line(0,0,image.shape[1],0, fill = "black", width = 5, tags = "r1r2")
	lineList.append(l2)
	l3 = canvas.create_line(0,image.shape[0],image.shape[1],image.shape[0], fill = "green", width = 5, tags = "r3r4")
	lineList.append(l3)
	l4 = canvas.create_line(image.shape[1],0,image.shape[1],image.shape[0], fill = "red", width = 5, tags = "r2r4")
	lineList.append(l4)
	r1 = canvas.create_rectangle(0,0,10,10,fill = "orange", tags = "r1")
	rectList.append(r1)
	r2 = canvas.create_rectangle(image.shape[1]-10,0,image.shape[1],10,fill = "yellow", tags = "r2")
	rectList.append(r2)
	r3 = canvas.create_rectangle(0,image.shape[0]-10,10,image.shape[0],fill = "gray", tags = "r3")
	rectList.append(r3)
	r4 = canvas.create_rectangle(image.shape[1]-10,image.shape[0]-10,image.shape[1],image.shape[0],fill = "red", tags = "r4")
	rectList.append(r4)
	butonKirp.config(state = "normal",text = "Resmi Kırp", command = lambda: resimKirp(canvas))
	print(image)

def resimKaydet():
	path = filedialog.asksaveasfilename(filetypes=[("PNG",'.png'),("JPG",'.jpg'),("JPEG",'.jpeg')],defaultextension = [("PNG",'.png'),("JPG",'.jpg'),("JPEG",'.jpeg')])
	print(path)
	cv2.imwrite(path,wrapped)
def hareketEttir(event):
	x = event.x
	y = event.y
	item = canvas.find_closest(x,y)
	for i in range(len(rectList)):
		if(item[0]==rectList[i]):
			canvas.coords(rectList[i],x-5,y-5,x+5,y+5)
			if(i==0):
				_,_,x2,y2 = canvas.coords(lineList[0])
				canvas.coords(lineList[0],x,y,x2,y2)
				_,_,x1,y1= canvas.coords(lineList[1])
				canvas.coords(lineList[1],x,y,x1,y1)
			if(i==1):
				x1,y1,_,_ = canvas.coords(lineList[1])
				canvas.coords(lineList[1],x1,y1,x,y)
				_,_,x2,y2 = canvas.coords(lineList[3])
				canvas.coords(lineList[3],x,y,x2,y2)
			if(i==2):
				x1,y1,_,_ = canvas.coords(lineList[0])
				canvas.coords(lineList[0],x1,y1,x,y)
				_,_,x2,y2 = canvas.coords(lineList[2])
				canvas.coords(lineList[2],x,y,x2,y2)
			if(i==3):
				x1,y1,_,_ = canvas.coords(lineList[2])
				canvas.coords(lineList[2],x1,y1,x,y)
				x2,y2,_,_ = canvas.coords(lineList[3])
				canvas.coords(lineList[3],x2,y2,x,y)




canvas.tag_bind("r1","<B1-Motion>",hareketEttir)
canvas.tag_bind("r2","<B1-Motion>",hareketEttir)
canvas.tag_bind("r3","<B1-Motion>",hareketEttir)
canvas.tag_bind("r4","<B1-Motion>",hareketEttir)
canvas.pack()

butonResimKirp = tk.Button(root,text = "Crop Image",state = "disabled")
butonResimKirp.pack()

butonResimAc = tk.Button(root,text = "Open Image", command = lambda:resimAc(canvas,butonResimKirp))
butonResimAc.pack()

root.mainloop()
