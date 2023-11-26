# main thread
import multiprocessing
from tkinter import *
from random import sample
from tkinter import Scale, Tk, Frame, Label, Button
from tkinter.ttk import Notebook,Entry
from tkinter import messagebox,simpledialog
from threading import Thread
import time
import os
from queue import Queue
from time import sleep
from turtle import update
from typing import Counter


q_for_of=Queue()
q_counters = Queue()
q_for_gui = Queue()
q_num = Queue()
q_update = Queue()
q_update.put(0)
q_update_gui = Queue()
q_update_gui_OF = Queue()
q_entry_exit = Queue()

#Counter class that defines attributes associated with each counter
class Counter:
        def __init__(self,counter_id):
            self.counter_id = counter_id
            #self.length = 0
            self.queue = []
            self.OF = 0.0
            self.output = 0                 # number of cust exiting counter in interval of five minutes
            self.weightage = 0

#Customer class that defines attributes associated with each customer
class Customer:
        def __init__(self,customer_id):  #instance of the class counter
            self.customer_id = customer_id
            self.counter = 0


global total_counters    
total_counters = [] # total number of available counters at the supermarket

global open_counters
open_counters = []   # number of open counters at a given instance of time

global closed_counters
closed_counters = []  # number of closed counters at a given instance of time

global counters
counters= dict()  #Dictionary that holds the mapping of counter_name to counter class (ey: value :: counter_name: counter_class)

global counter_info
counter_info = dict()

global customer_list # 


def customer_map(threadname, q_for_of,q_num,q_update,q_for_gui):
    # Environment setup established here --> max counters, max length and total number of counters
    global isValidcounter, counter_info
    isValidcounter = 0
    mobile_counter_customer = []
    clear = lambda: os. system('cls')
    global customer_list
    customer_list = dict()
    max_length = int(input("Enter maximum length for each counter:\n"))
    max_num_counters = int(input("Enter max number of counters:\n"))
    isValidcounter = False
    while(not isValidcounter):
        num_counters = int(input("Enter number of counters:\n"))
        if num_counters <= max_num_counters:
            isValidcounter = True
    q_num.put(num_counters)
    threshold = max_length//2   # threshold provides the cutoff range for the load balancer funtion
  
    #Assigning numbers to each counter and moving them into closed (initial setup)
    for i in range(num_counters): 
        counter_num = "counter_%d" % (i+1)
        counters[counter_num] = Counter(i+1)
        closed_counters.append(counters[counter_num])

        # Each counter initially has no queue or no exit rate
        counter_info[counter_num] = dict()
        counter_info[counter_num]['weightage'] = 0.0
        counter_info[counter_num]['queue'] = []
    #Load the GUI Page
    update_gui = q_update_gui.get()

    def Entry(customer):
            # The load balancing function that maps the user to the appropriate counter
            if open_counters== []:     # first customer condition
                open_counters.append(closed_counters.pop(0)) #move the first closed counter to open counter array
                open_counters[-1].queue.append(customer.customer_id)
                customer.counter = open_counters[-1].counter_id
                print("customer" + str(customer.customer_id) +  " is assigned to counter: " + str(open_counters[-1].counter_id))
                update_gui(customer.counter,0)
            else: 
               
                potential = -1 # to check for the counter with the highest weightage
                count_below_threshold = 0     # to check later how many counters are above threshold
                for item in open_counters:
                    if len(item.queue) < threshold:
                        count_below_threshold = 1
                        if(item.weightage>potential):
                            potential = item.weightage # Finding that node that holds the largest weightage
                            potential_data = item
                
                if count_below_threshold == 1:    # if there is a counter with less than threshold customers
                    customer.counter = potential_data.counter_id    # assign that counter to customer
                    potential_data.queue.append(customer.customer_id) # add customer to that counter's queue
                    print ("customer" + str(customer.customer_id) +  " is assigned to counter:", potential_data.counter_id)
                            # update weightage of that counter

                elif count_below_threshold==0: # all open counters have reached threshold length
                    if closed_counters!=[]: # all open counters have a queue greater than threshold AND closed counters EXIST
                            open_counters.append(closed_counters.pop(0))  # open the next available closed counter
                            customer.counter = open_counters[-1].counter_id 
                            update_gui(customer.counter,0)
                            open_counters[-1].queue.append(customer.customer_id)  # add customer to that counter's queue'
                            print("customer" + str(customer.customer_id) + " is assigned to counter:", open_counters[-1].counter_id)
                        
                    else:  # all open counters have reached threshold AND NO closed counters exist 
                            max_weightage_allOpen_allAboveThreshold = -1
                            not_all_counters_full = 0
                            for i in open_counters:
                                if i.weightage > max_weightage_allOpen_allAboveThreshold and len(i.queue) < max_length: # finding the counter with the largest weightage and counter is not full
                                    
                                        not_all_counters_full = 1
                                        max_weightage_allOpen_allAboveThreshold = i.weightage
                                        max_weightage_allOpen_allAboveThreshold_data = i
                        
                            if not_all_counters_full==1:# at least one counter which is not FULL
                                customer.counter = max_weightage_allOpen_allAboveThreshold_data.counter_id
                                max_weightage_allOpen_allAboveThreshold_data.queue.append(customer.customer_id)
                                print("customer" + str(customer.customer_id) +  " is assigned to counter:" , max_weightage_allOpen_allAboveThreshold_data.counter_id)
                            
                            else:  # all counters are open and full
                                print("OPEN MOBILE COUNTERS")
                                mobile_counter_customer.append(customer)
                                customer.counter = -1  # -1 for customer indicates mobile counters
                                
            #customer is mapped to counter and updated into the dictionary
            customer_list.update({customer.customer_id:[customer, customer.counter]})
            num_temp = "counter_%d" % (customer.counter)
            if customer.counter != -1: #mobile counter details are not updated
                counter_info[num_temp]['queue'].append(customer.customer_id)
                update_gui(customer.counter,1)




    #function that handles the exit of customers     
    def Exit(customer):
        counter_of_exit_id = customer.counter # identify the counter where customer wishes to exit              
        print("first cust",counters["counter_%d" % counter_of_exit_id].queue[0]) #find "id" of the counter from which customer exits
        if customer.customer_id == counters["counter_%d" % counter_of_exit_id].queue[0]:
            customer_counter_info = customer.counter
            print("customer " , customer.customer_id,  "exited from counter ", counter_of_exit_id)
        
            counters["counter_%d" % counter_of_exit_id].queue.pop(0)   
            #set the counter associated with a given customer to 0 (no longer associated with queue)                                 
            customer.counter = 0  #remove customer: counter relationship
        
            # if all customers leave the counter then move the counter from open to closed
            if (len((counters["counter_%d" % counter_of_exit_id]).queue) == 0):
                closed_counters.append(open_counters.pop(open_counters.index(counters["counter_%d" % counter_of_exit_id])))
                update_gui(counter_of_exit_id,0) # update the GUI appropropriately 
                closed_counters[-1].OF = 0 # The rate of exit is set to 0
                
            else:
                #increment 1 to indicate the number of customers exiting from a given counter
                counters["counter_%d" % counter_of_exit_id].output += 1
            
            customer_list.pop(customer.customer_id) #delete the customer from the customer list
           
            num_temp = "counter_%d" % (customer_counter_info)
            counter_info[num_temp]['queue'].remove(customer.customer_id)
            update_gui(counter_of_exit_id,1)
        else:
            print("Invalid Exit\n\n")


    q_entry_exit.put([Entry,Exit])

   # the main function that runs on the main thread
    def main():
        cont = 0
        # while the user wishes to continue interacting with the application 
        while(cont==0):
            choice = int(input("Enter \n 1.Entry \n 2.Exit \n 3.Exit Program \n"))
            # new customer enters the supermarket 
            if(choice==1):
                q_for_of.put(choice) # update the other threads running
                q_for_gui.put(choice) # update the GUI Thread
                cust_id = int(input("Enter customer id:\n"))
                if cust_id not in customer_list.keys():
                    Entry(Customer(cust_id)) # new customer, new instance created and Entry function called for it
                
                else:
                    print("Customer", cust_id, "already present in counter: ", customer_list[cust_id][1])
                print(counter_info)

            #existing customer leaves the counter queue after successful shopping
            elif(choice==2):
                q_for_of.put(choice)
                q_for_gui.put(choice)
                cust_id = int(input("Enter customer id:\n"))
                if cust_id in customer_list.keys():
                    Exit(customer_list[cust_id][0]) # Call exit function to update the exit rates
                else:
                    print("Invalid Exit")
                print(counter_info)

            #if manager wants to close the running application 
            elif(choice==3):
                q_for_of.put(choice)
                q_for_gui.put(choice)
                exit()

            # any other choice/key press
            else:
                q_for_of.put(choice)
                q_for_gui.put(choice)
                print("Invalid key")
           


    main() # executed on the main thread

#this function runs on a different thread --> it constantly polls the main thread and updates the exit rate
def poller(threadname,q_for_of,q_update_gui_OF):
    update_gui = q_update_gui_OF.get()
    while(True):  # Poller keeps running in background
            choice = q_for_of.get()
            if choice==3:  # if the main thread exits, then the poller thread also exits
                quit()
           
            time.sleep(3) #time delay introduced before starting the re-calculation
            # code contains the metric that is used for load balancing
            for i in open_counters:
                i.OF = i.output / 2    # OF--> output frequency          
                i.weightage = i.OF / len(i.queue) #custom weightage calculated
                i.output = 0 # output set to 0 to prevent result from clashing 
                print("\n",i.counter_id, i.OF)
                num_temp = "counter_%d" % (i.counter_id)
                counter_info[num_temp]['weightage'] = i.weightage
                update_gui(i.counter_id,1)
            
# The GUI interface runs on another thread
def gui_thread(threadname,q_num,q_for_gui,q_update):

    def getValue2(value):
        thresh = scale2.get()
        print(thresh)

    num_counters = q_num.get()
    count=0

    global last_row
    last_row = 0

    window=Tk()
    window.title("Counter management")
    window.geometry("600x400")
      

    #displays the Threshold bar on the GUI (manager can change it)
    scale2=Scale(window,label="Threshold",from_=0,to=10,command=getValue2,fg="white",bg="green",activebackground="red",troughcolor="orange",orient="horizontal",showvalue=1)
    scale2.pack(fill="x")
    thresh = scale2.get()
    print(thresh)
    frame2=Frame(window)
    frame2.pack(fill="both")

   
    tablayout=Notebook(frame2)
    tab1=Frame(tablayout)
    tab1.pack(fill="both")
    #Counter details highlighted here 
    counter_num_l = Label(tab1, text = "Number of counters:"+str(num_counters),bg="black",fg="white",padx=3,pady=3)
    counter_num_l.grid(row = 20, column= 2)
    print(counter_num_l)

    #Displays all the associated data on the GUI 
    def showData(btn):
        global customer_list
        Entry,Exit = q_entry_exit.get()
        row1=btn.grid_info()['row']

        key = "counter_%d" % (row1)
        try:
            widget = tab1.grid_slaves(row=row1,column=1)[0]
            widget.grid_forget()
            widget.grid(row=row1,column=0,padx=3,pady=2)
            open_counters.append(closed_counters.pop(closed_counters.index(counters[key])))
            print(open_counters)
        except IndexError:
            widget=tab1.grid_slaves(row=row1,column=0)[0]
            widget.grid_forget()
            widget.grid(row=row1,column=1,padx=3,pady=2)
            num=0
            while counter_info[key]['queue']!=[]:
                r = counter_info[key]['queue'][0]
                Exit(customer_list[r][0])
                print(counter_info[key]['queue'])
                Entry(Customer(r))
                print(counter_info)
            closed_counters.append(open_counters.pop(open_counters.index(counters[key])))
            print("closed counters",closed_counters)

    
        widget.config(padx = 3,pady=15,text="Counter_"+str(row1)+
                    "\nWeightage:"+str(counter_info[key]['weightage'])+"\nQueue:"+
                    str(counter_info[key]['queue']))
    
       
    # When the manager adds or removes counters 
    def Change_num_counter():
        res = messagebox.askquestion('Are you sure?', 'Click yes to change total number of counters')
        if res == 'yes':
            new_num_counters = simpledialog.askinteger("Input", "Enter number of counters:",parent=tab1,minvalue=0, maxvalue=15)
            print("new:",new_num_counters)
            global num_counters
            num_counters = new_num_counters
            q_num.put(num_counters)
            print(num_counters)
            global last_row
            print("last row:",last_row)
            
            if new_num_counters > last_row:
                for row in range(last_row+1,new_num_counters+1):
                    for column in range(3):
                        
                        if column==2:
                            button=Button(tab1,text="Change counter status",bg="blue",fg="white",padx=3,pady=3)
                            button.grid(row=row,column=column,sticky="nsew",padx=1,pady=1)
                            button['command']=lambda btn=button:showData(btn)
                            tab1.grid_columnconfigure(column,weight=1)
                        elif column ==1:
                            counter_num = "counter_%d" % (row)
                            counters[counter_num] = Counter(row)
                            closed_counters.append(counters[counter_num])
                            counter_info[counter_num] = dict()
                            counter_info[counter_num]['weightage'] = 0.0
                            counter_info[counter_num]['queue'] = []
                            label=Label(tab1,text="Counter_"+str(counters[counter_num].counter_id)+
                            "\nWeightage:"+str(counter_info[counter_num]['weightage'])+"\nQueue:"+
                            str(counter_info[counter_num]['queue']),bg="black",fg="white",padx=1,pady=10)
                            label.grid(row=row,column=column,sticky="nsew",padx=1,pady=2)
                            tab1.grid_columnconfigure(column,weight=1)
                last_row = new_num_counters

            elif new_num_counters < last_row:
                for row1 in range(new_num_counters+1,last_row+1):
                    for column1 in range(3):
                        try:
                            widget=tab1.grid_slaves(row=row1,column=column1)[0]
                            widget.grid_forget()
                        except IndexError:
                            continue
                    
                    counter_num = "counter_%d" % (row1)
                    counters.pop(counter_num)
                last_row = new_num_counters

            counter_num_l.config(text = "Number of counters:"+ str(num_counters))

    for row_disp in range(num_counters+1):
        for column in range(3):
            if row_disp==0:
                if column==2:
                    label = Label(tab1, text="Action", bg="white", fg="black", padx=3, pady=3)
                    label.config(font=('Arial', 14))
                    label.grid(row=row_disp, column=column, sticky="nsew", padx=1, pady=1)
                    tab1.grid_columnconfigure(column, weight=1)

                else:
                    if column ==0:
                        label = Label(tab1, text="Open counters " , bg="white", fg="black", padx=3, pady=3)
                        label.config(font=('Arial', 14))
                        label.grid(row=row_disp, column=column, sticky="nsew", padx=1, pady=1)
                        tab1.grid_columnconfigure(column, weight=1)

                    else:

                        label = Label(tab1, text="Closed counters " , bg="white", fg="black", padx=3, pady=3)
                        label.config(font=('Arial', 14))
                        label.grid(row=row_disp, column=column, sticky="nsew", padx=1, pady=1)
                        tab1.grid_columnconfigure(column, weight=1)

            else:
                if column==2:
                    button=Button(tab1,text="Change counter status",bg="blue",fg="white",padx=3,pady=3)
                    button.grid(row=row_disp,column=column,sticky="nsew",padx=1,pady=1)
                    button['command']=lambda btn=button:showData(btn)
                    tab1.grid_columnconfigure(column,weight=1)
                elif column ==1:
                    counter_num = "counter_%d" % (row_disp)
                    label=Label(tab1,text="Counter_"+str(row_disp)+
                    "\nWeightage:"+str(counter_info[counter_num]['weightage'])+"\nQueue:"+
                    str(counter_info[counter_num]['queue']),bg="black",fg="white",padx=1,pady=10)
                    label.grid(row=row_disp,column=column,sticky="nsew",padx=1,pady=2)
                    tab1.grid_columnconfigure(column,weight=1)

    last_row = row_disp
    button = Button(tab1, text="Click here if you want to change number of counters:\n",bg="black",fg="white",padx=3,pady=3,command=Change_num_counter).grid(row=23,column=2)
    tablayout.add(tab1,text="TAB 1")
    tablayout.pack(fill="both")
    a = 0

    # function that updates the GUI and changes contents on it
    def update_gui(counter_id,num):
        key = "counter_%d" % (counter_id)
        print("update start\n")
        if num:
            try:
                widget = tab1.grid_slaves(row=counter_id,column=1)[0]
                widget.config(padx = 3,pady=15,text="Counter_"+str(counter_id)+
                        "\nWeightage:"+str(counter_info[key]['weightage'])+"\nQueue:"+
                        str(counter_info[key]['queue']))
            except IndexError:
                widget=tab1.grid_slaves(row=counter_id,column=0)[0]
                widget.config(padx = 3,pady=15,text="Counter_"+str(counter_id)+
                        "\nWeightage:"+str(counter_info[key]['weightage'])+"\nQueue:"+
                        str(counter_info[key]['queue']))
        else:
            row1=counter_id
            key = "counter_%d" % (row1)
            try:
                widget = tab1.grid_slaves(row=row1,column=1)[0]
                widget.grid_forget()
                widget.grid(row=row1,column=0,padx=3,pady=2)
            except IndexError:
                widget=tab1.grid_slaves(row=row1,column=0)[0]
                widget.grid_forget()
                widget.grid(row=row1,column=1,padx=3,pady=2)

            num_temp = "counter_%d" % (row1)
            widget.config(padx = 3,pady=15,text="Counter_"+str(row1)+
                        "\nWeightage:"+str(counter_info[num_temp]['weightage'])+"\nQueue:"+
                        str(counter_info[num_temp]['queue']))
        
    q_update_gui.put(update_gui)
    q_update_gui_OF.put(update_gui)

    window.mainloop()

# The three threads that run concurrently     
t1 = Thread(target = customer_map,args = ("thread1",q_for_of,q_num,q_update,q_for_gui))
t2 = Thread(target= poller, args = ("thread2",q_for_of,q_update_gui_OF))
t4 = Thread(target = gui_thread, args = ("thread4",q_num,q_for_gui,q_update))
t1.start() # the main thread is started first
t2.start() # the poller is started next
t4.start() # the GUI is brought up next
t1.join() # The main thread waits for the other threads to join it
t2.join()
t4.join()
