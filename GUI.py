from tkinter import *

window = Tk()
window.title("Wikipedia Summarizer")
window.geometry("1600x900")
window.resizable(False, False)

link = StringVar()
summaryLength = StringVar()

def summary():
    print("Summary")

linkLabel = Label(window, text = "Link", font = ("courier", 15), bg = "red", padx = 20, pady = 20)
linkLabel.place(x = 0, y = 0)
linkInput = Entry(window, textvariable = link, font = ("courier", 15), bg = "blue", width = 50)
linkInput.place(x = 95, y = 15)

summaryLengthLabel = Label(window, text = "No. of sentences in the summary", font = ("courier", 15), bg = "yellow", padx = 20, pady = 20)
summaryLengthLabel.place(x = 0, y = 55)
summaryLengthInput = Entry(window, textvariable = summaryLength, font = ("courier", 15), bg = "blue", width = 23)
summaryLengthInput.place(x = 420, y = 75)

summarize = Button(window, text = "Summarize", font = ("courier", 15), bg = "green", command = summary)
summarize.place(x = 310, y = 120)

window.mainloop()