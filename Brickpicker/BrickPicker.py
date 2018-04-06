from tkinter import *
#import tkinter.ttk

from tkinter.ttk import Treeview
#import ttk

import csv, colorsys, time
from PIL import Image
from PIL import ImageTk as ITK
import numpy as np

def hextorgb(hexw):
    if hexw[0] == "#":
        hexw = hexw[1:]
    r = eval("0x"+hexw[0:2])
    g = eval("0x"+hexw[2:4])
    b = eval("0x"+hexw[4:6])
    return r, g, b
def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    l.sort(reverse=reverse)

    # rearrange items in sorted positions
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    # reverse sort next time
    tv.heading(col, command=lambda: \
           treeview_sort_column(tv, col, not reverse))
def treeview_sort_column_numeric(tv, col, index, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    #print(l)
    try:
        l.sort(reverse=reverse, key=lambda x: int(x))
    except:
        l.sort(reverse=reverse, key=lambda x: int(x[index]))

    # rearrange items in sorted positions
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    # reverse sort next time
    tv.heading(col, command=lambda: \
           treeview_sort_column(tv, col, not reverse))
def get_partimage(part_id, color_id):
    return "../../lsorter_notgit/images/parts_" + str(color_id)+"/" + str(part_id) + ".png"

with open('./library/parts_sorted.csv', 'r') as f:
    reader = csv.reader(f)
    partarray = np.array(list(reader))
with open('./library/part_categories.csv', 'r') as f:
    reader = csv.reader(f)
    categoriesarray = np.array(list(reader))
with open('./library/colors.csv', 'r') as f:
    reader = csv.reader(f)
    colorsarray = np.array(list(reader))
colorsarray = colorsarray[1:]
catstrs = []
for i in range(1, 58):
    catstrs.append(categoriesarray[i, 1])
#print(catstrs)
categoriesarray

def category_from_id(id):
    if not id:
        return
    for c in categoriesarray:
        if c[0] == str(id):
            return c[1]
    raise ValueError("Category with Id {} doesn't exist!".format(id))
def category_to_id(cat):
    if not cat:
        return
    for c in categoriesarray:
        if c[1] == cat:
            return c[0]
    raise ValueError("Category with Id {} doesn't exist!".format(cat))
def color_name_and_hex_from_id(id):
    if not id:
        return
    for c in colorsarray:
        if c[0] == str(id):
            return c[1], c[2]
    raise ValueError("Color with Id {} doesn't exist!".format(id))
def brick_name_and_category_id_from_brick_id(id):
    if not id:
        return
    for p in partarray:
        print(p[0])
        if p[0] == str(id):
            return p[1], p[2]
    raise ValueError("Part with Id {} doesn't exist!".format(id))
    

print("parts loaded.")

root = Tk()
selectionframe = Frame(root)
selectionframe.grid(row=0, column=0)

brickchooser = LabelFrame(selectionframe)
brickchooser["text"] = "Choose Brick"
brickchooser.pack(side="left", fill="y")
btree = Treeview(brickchooser)
bscrollb = Scrollbar(brickchooser)

btree["columns"]=("num")
btree.column("num", width=100)
btree.heading("num", text="ID", command=lambda: treeview_sort_column_numeric(btree, "num", 0, False))
btree["yscrollcommand"] = bscrollb.set
bscrollb["command"] = btree.yview
btree.pack(side = "left", expand=True, fill="both")
bscrollb.pack(side = "left", anchor = "w", expand=True, fill="y")

i_part = 1
i_cat = 1
parts_in_cats = []
for cat in catstrs:
    #print("Loading category", cat)
    parts_in_cats.append([])
    btree.insert("", 3, cat, text=cat, values=(i_cat))
    while int(partarray[i_part, 2]) == i_cat:
        #btree.insert(cat, 3, text=partarray[i_part, 1],values=(partarray[i_part, 0]))
        parts_in_cats[-1].append(list(partarray[i_part]))
        i_part += 1
        if i_part > 27614:
            break
    i_cat += 1
    
for i_cat in range(57):
    #print(i_cat)
    ps = parts_in_cats[i_cat]
    ps.sort(key=lambda n: n[1])
    #print(ps)
    for p in ps:
        btree.insert(catstrs[i_cat], 3, text=p[1],values=(p[0]))

#---------------------------------------------------------------------------

colorchooser = LabelFrame(selectionframe)
colorchooser["text"] = "Choose Color"
colorchooser.pack(side="left", fill="y")
ctree = Treeview(colorchooser)
cscrollb = Scrollbar(colorchooser)

ctree["columns"]=("id", "is_trans", "html", "rgb", "hls")
for n in ctree["columns"]:
    ctree.column(n, width=100)
ctree.heading("id", text="ID")
ctree.heading("is_trans", text="Transparent")
ctree.heading("html", text="HEX")
ctree.heading("rgb", text="RGB")
ctree.heading("hls", text="HLS")

ctree["yscrollcommand"] = cscrollb.set
cscrollb["command"] = ctree.yview
ctree.pack(side = "left", expand=True, fill="both")
cscrollb.pack(side = "left", anchor = "w", expand=True, fill="y")

for col_list in colorsarray:
    ctree.insert("" , 0,    text=col_list[1], values=(col_list[0], col_list[3], col_list[2], hextorgb(col_list[2]), [round(p, 3) for p in colorsys.rgb_to_hls(*hextorgb(col_list[2]))]))
    

#---------------------------------------------------------------------------
def search(*args):
    global sitems
    term = sentryvar.get()
    terms = term.split(" ")
    print("searching for:", terms)
    results = []
    stree.delete(*sitems)
    sitems=[]
    start = time.perf_counter()
    for part in partarray:
        n = True
        for term in terms:
            if not (term in part[1] and n):
                n = False
                break
        if n:
            results.append(part)
    if term =="*":
        results=partarray.copy()
    results.sort(key=lambda x: x[1], reverse=True)
    for r in results:
        sitems.append(stree.insert("" , 0,    text=r[1], values=(r[0])))
    if not results:
        sitems.append(stree.insert("" , 0,    text="Nothing found for"+term, values=()))
    stop = time.perf_counter()
    print("Found {} items in {} sec.".format(len(results), round(stop-start, 5)))
sitems=[]
brickfinder = LabelFrame(selectionframe)
brickfinder["text"] = "Find Brick"
brickfinder.pack(side="left", fill="y")
stree = Treeview(brickfinder)
sscrollb = Scrollbar(brickfinder)

stree["columns"]=("id")
for n in stree["columns"]:
    stree.column(n, width=20)
stree.heading("id", text="ID")

stree["yscrollcommand"] = sscrollb.set
sscrollb["command"] = stree.yview
ssearch = Frame(brickfinder)
sentry = Entry(ssearch)
sentryvar = StringVar()
sentry["textvariable"] = sentryvar
sentry.bind("<Key-Return")
sbutton = Button(ssearch)
sbutton["text"] = "Search"
sbutton["command"] = search

sentry.pack(side="left", fill="x", anchor="e")
sbutton.pack(anchor="e")
ssearch.pack(side="top", fill="x")
stree.pack(side = "left", expand=True, fill="both")
sscrollb.pack(side = "left", anchor = "w", expand=True, fill="y")

#---------------------------------------------------------------------------

def preciseaddcmd(*args):#from brickchooser
    apds = []
    cs = list(ctree.selection())
    bs = list(btree.selection())
    print(cs, bs)
    if not bs:
        coloraddcmd()
        return
    if not cs:
        brickaddcmd()
        return
    cids = []
    bids = []
    catids = []
    for i in cs:
        cids.append(ctree.item(i)["values"][0])
    for i in bs:
        if i[0] == "I":#i is a part, not a category
            bids.append(btree.item(i)["values"][0])
        else:
            catids.append(category_to_id(i))
    print(cids, bids, catids)
    for co in cids:
        for br in bids:
            apds.append([br, None, co])
        for ca in catids:
            apds.append([None, ca, co])
    for a in apds:
        add_to_selection(*a)
    
def preciseadd1cmd(*args):#from search
    apds = []
    ss = list(stree.selection())
    cs = list(ctree.selection())
    print(ss, cs)
    if not ss:
        coloraddcmd()
        return
    if not cs:
        brickaddcmd()
        return
    cids = []
    sids = []
    catids = []
    for i in cs:
        cids.append(ctree.item(i)["values"][0])
    for i in ss:
        if i[0] == "I":#i is a part, not a category
            sids.append(stree.item(i)["values"][0])
        else:
            catids.append(category_to_id(i))
    print(cids, sids, catids)
    for co in cids:
        for sr in sids:
            apds.append([sr, None, co])
        for ca in catids:
            apds.append([None, ca, co])
    for a in apds:
        add_to_selection(*a)

def brickaddcmd(*args):
    apds = []
    bs = list(btree.selection())
    print(bs)
    if not bs:
        preciseaddcmd()
        return
    bids = []
    catids = []
    for i in bs:
        if i[0] == "I":#i is a part, not a category
            bids.append(btree.item(i)["values"][0])
        else:
            catids.append(category_to_id(i))
    print(bids, catids)
    for br in bids:
        apds.append([br, None, None])
    for ca in catids:
        apds.append([None, ca, None])
    for a in apds:
        add_to_selection(*a)
def coloraddcmd(*args):
    pass
def unselectcmd(*args):
    stree.selection_remove(stree.selection())
    ctree.selection_remove(ctree.selection())
    btree.selection_remove(btree.selection())


addframe = Frame(root)
addframe.grid(row=1, column=0)

preciseadd = Button(addframe)
preciseadd["text"] = "Add only this selection (Choose Brick Frame)"
preciseadd["command"] = preciseaddcmd
#preciseadd["background"] = "lightgray"
preciseadd.pack(side="left", fill="x", ipadx=20, ipady=20, pady=10, padx=10)

preciseadd1 = Button(addframe)
preciseadd1["text"] = "Add only this selection (Search Frame)"
preciseadd1["command"] = preciseadd1cmd
#preciseadd1["background"] = "lightgray"
preciseadd1.pack(side="left", fill="x", ipadx=20, ipady=20, pady=10, padx=10)

brickadd = Button(addframe)
brickadd["text"] = "Add this Brick(s) in every color"
brickadd["command"] = brickaddcmd
#brickadd["background"] = "lightgray"
brickadd.pack(side="left", fill="x", ipadx=20, ipady=20, pady=10, padx=10)

coloradd = Button(addframe)
coloradd["text"] = "Add every Brick in this color(s)"
coloradd["command"] = coloraddcmd
#coloradd["background"] = "lightgray"
coloradd.pack(side="left", fill="x", ipadx=20, ipady=20, pady=10, padx=10)

unselect = Button(addframe)
unselect["text"] = "Unselect all"
unselect["command"] = unselectcmd
#unselect["background"] = "lightgray"
unselect.pack(side="left", fill="x", ipadx=20, ipady=20, pady=10, padx=10)
#---------------------------------------------------------------------------

selectionlist = []

viewframe = Frame(root)
viewframe.grid(row=2, column=0)
view = LabelFrame(viewframe)
view["text"] = "Selection"
view.pack(side="left", fill="y")
vtree = Treeview(view)
vscrollb = Scrollbar(view)

vtree["columns"]=("Category", "Brick ID", "Color")
vtree.column("Category", width=50)
vtree.heading("Category", text="Category", command=lambda: treeview_sort_column_numeric(vtree, "Category", 0, False))
vtree.column("Brick ID", width=50)
vtree.heading("Brick ID", text="Brick ID", command=lambda: treeview_sort_column_numeric(vtree, "Brick ID", 0, False))
vtree.column("Color", width=100)
vtree.heading("Color", text="Color", command=lambda: treeview_sort_column_numeric(vtree, "Color", 0, False))
vtree["yscrollcommand"] = vscrollb.set
vscrollb["command"] = vtree.yview
vtree.pack(side = "left", expand=True, fill="both")
vscrollb.pack(side = "left", anchor = "w", expand=True, fill="y")

infoframe = LabelFrame(viewframe)
infoframe["text"] = "Brick Detail"
infoframe.pack(fill="y")
pimgcv = Canvas(infoframe, width=125, height=125)
pimg = ITK.PhotoImage(Image.open(get_partimage(1, 0)).resize((125, 125)))
print(pimg)
pimgcv.create_image(0, 0, image=pimg, anchor="nw")
pimgcv.grid(row=0, column=0, columnspan=2)

namelbl = Label(infoframe)
namelbl["text"] = "Name:"
namelbl.grid(row=1, column=0, sticky="w")
namelbl2 = Label(infoframe)
namelbl2.grid(row=1, column=1, sticky="w")

idlbl = Label(infoframe)
idlbl["text"] = "ID:"
idlbl.grid(row=2, column=0, sticky="w")
idlbl2 = Label(infoframe)
idlbl2.grid(row=2, column=1, sticky="w")

catlbl = Label(infoframe)
catlbl["text"] = "Category:"
catlbl.grid(row=3, column=0, sticky="w")
catlbl2 = Label(infoframe)
catlbl2.grid(row=3, column=1, sticky="w")

colorlbl = Label(infoframe)
colorlbl["text"] = "Color:"
colorlbl.grid(row=4, column=0, sticky="w")
colorlbl2 = Label(infoframe)
colorlbl2.grid(row=4, column=1, sticky="w")

def add_to_selection(brick_id, category_id, color_id):#None if not specified
    bid = (brick_id if brick_id else "")
    if brick_id:
        brick_name = brick_name_and_category_id_from_brick_id(brick_id)
    else:
        brick_name = "All"
    if category_id:
        category_name = category_from_id(category_id)
        catstr = "{} ({})".format(category_name, category_id)
    else:
        catstr = "All"
    if color_id:
        color_name, color_hex = color_name_and_hex_from_id(color_id)
        color_rgb = hextorgb(color_hex)
        colstr = "{} ({}, {}, {})".format(color_name, *color_rgb)
    else:
        colstr = "All"
    vtree.insert("", 3, brick_name, text=brick_name, values=(catstr, bid, colstr))
    update_brickdetail(brick_id, color_id)
    selectionlist.append([brick_id, category_id, color_id])

def update_brickdetail(brick_id, color_id):
    brick_name = ""
    category_name = ""
    color_name = ""
    color_rgb = ()
    brick_name, category_id = brick_name_and_category_id_from_brick_id(brick_id)
    category_name = category_from_id(category_id)
    color_name, color_hex = color_name_and_hex_from_id(color_id)
    color_rgb = hextorgb(color_hex)
    namelbl2["text"] = brick_name
    idlbl2["text"] = brick_id
    catlbl2["text"] = "{} ({})".format(category_name, category_id)
    colorlbl2["text"] = "{} ({}, {}, {})".format(color_name, *color_rgb)
    colorlbl2["fg"] = "#" + color_hex
    pimg = ITK.PhotoImage(Image.open(get_partimage(brick_id, color_id)).resize((125, 125)))
    print(pimg)
    pimgcv.create_image(0, 0, image=pimg, anchor="nw")
#tree.insert("" , 0,    text="Line 1", values=("1A","1b"))

#id2 = tree.insert("", 1, "dir2", text="Dir 2")
#tree.insert(id2, "end", "dir 2", text="sub dir 2", values=("2A","2B"))

##alternatively:
#tree.insert("", 3, "dir3", text="Dir 3")
#tree.insert("dir3", 3, text=" sub dir 3",values=("3A"," 3B"))






root.mainloop()