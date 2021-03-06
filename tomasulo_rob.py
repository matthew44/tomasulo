#!/usr/bin/python
# -*- coding: utf-8 -*-

# Tomasulo ROB

class ROBobject:
    rob = []
    rob_check_counter = 0 # puntero commit
    rob_add_counter = 0   # puntero issue
    rob_total_entries = 0
    rob_empty_entry = {
        "busy" : "no",
        "instruction" : "-",
        "state" : "-", # possible states = ["ISSUE", "EX", "MEM", "WB", "COMMIT"]
        "destination" : "-", # “dest" field of a store instruction records its location in the load/store queue
        "value" : "-",
        "timing_table_entry_index" : "-"        # would like to have access to timing entry from here for convenience
    }

    def rob_initialize(self, num_rob_entries):
        # initialize rob

        for i in range(num_rob_entries):
            self.rob.append(self.rob_empty_entry.copy())
    
    def rob_instr_add(self, instruction, rob_dest, timing_table_entry_index):
        #add entry after you fetch instruction
        
        #rob_dest = instruction.split()[1] # destination register
        
        if self.rob_total_entries != len(self.rob): # if ROB isn't full
            # update ROB entry
            self.rob[self.rob_add_counter]["busy"] = "yes"
            self.rob[self.rob_add_counter]["instruction"] = instruction
            self.rob[self.rob_add_counter]["state"] = "ISSUE"
            self.rob[self.rob_add_counter]["destination"] = rob_dest # for l/s -> updated after execute stage; for branches -> "-"
            self.rob[self.rob_add_counter]["timing_table_entry_index"] = timing_table_entry_index
            return_value = "ROB" + str(self.rob_add_counter)
            # update counters for the next time
            if self.rob_add_counter + 1 == len(self.rob): # rotate ROB current entry counter
                self.rob_add_counter = 0
            else:
                self.rob_add_counter = self.rob_add_counter + 1 # point to the next entry to ROB 
            self.rob_total_entries = self.rob_total_entries + 1 # increment total number of entries 
            return return_value
        else:
            print ("ROB full!")
            return -1 
    
    def rob_available(self):
        if self.rob_total_entries != len(self.rob):
            return 1
        else:
            return -1
    
    def rob_empty(self):
        # returns 1 if rob is empty
        if self.rob_total_entries == 0:
            return 1
        else:
            return -1
    
    #rob_check_counter es una puntero que controla hasta donde se hizo commit, en base al puntero obtengo una entrada para commit
    def rob_check_if_ready_to_commit(self):
        if self.rob_total_entries != 0 and self.rob[self.rob_check_counter]["busy"] == "no":
            # return_value = [tt_index, destination, value, instruction_id, rob_entry_name]
            return_value = [self.rob[self.rob_check_counter]["timing_table_entry_index"], self.rob[self.rob_check_counter]["destination"], self.rob[self.rob_check_counter]["value"], self.rob[self.rob_check_counter]["instruction"].split(" ")[0], "ROB"+str(self.rob_check_counter)]
            return return_value
        else:
            return -1

    def rob_commit(self):
        self.rob[self.rob_check_counter] = self.rob_empty_entry.copy()
        if self.rob_check_counter + 1 == len(self.rob):
            self.rob_check_counter = 0
        else:
            self.rob_check_counter = self.rob_check_counter + 1
        self.rob_total_entries = self.rob_total_entries - 1
            
    def rob_get_instruction_id(self, rob_entry):
        return self.rob[int(rob_entry.split("ROB")[1])]["instruction"].split(" ")[0]
            
    def rob_get_destination(self, rob_entry):
        return self.rob[int(rob_entry.split("ROB")[1])]["destination"]
    
    def rob_update_sd_destination(self, rob_entry, ls_address):
        if self.rob[int(rob_entry.split("ROB")[1])]["instruction"].split(" ")[0] == "SD":
            self.rob[int(rob_entry.split("ROB")[1])]["destination"] = ls_address
    
    def rob_get_value(self, rob_entry):
        return self.rob[int(rob_entry.split("ROB")[1])]["value"]
    
    def rob_get_state(self, rob_entry):
        return self.rob[int(rob_entry.split("ROB")[1])]["state"]
            
    def rob_update_value(self, rob_entry, rs_value):
        #Saco el valor del registro de las estaciones de reserva
        rob_update_index = int(rob_entry.split("ROB")[1])
        self.rob[rob_update_index]["value"] = rs_value
        # Aviso que esta entrada de la ROB esta lista para commit
        self.rob[rob_update_index]["busy"] = "no"
        
    def rob_update_state(self, rob_entry, rs_state):
        #use reservation stations to update rob state field
        
        rob_update_index = int(rob_entry.split("ROB")[1])
        self.rob[rob_update_index]["state"] = rs_state
        
    def rob_get_tt_index(self, rob_entry):
        # return timing table index

        rob_update_index = int(rob_entry.split("ROB")[1])
        return self.rob[rob_update_index]["timing_table_entry_index"]        

    #Devuelve la proxima entrada pra hacer commit de la ROB
    def rob_head_node(self, instruction_issue_indicator):
        if self.rob_add_counter == 0:
            rob_add_counter_previous = len(self.rob) - 1
        else:
            rob_add_counter_previous = self.rob_add_counter - 1
        if (self.rob_total_entries == 0) or (instruction_issue_indicator != "-" and self.rob_check_counter == rob_add_counter_previous): #returns -1 si la ROB esta vacia
            return -1
        else:
            return "ROB" + str(self.rob_check_counter)
        
    #Devuelve la proxima entrada a la ROB ocuapara repecto a rob_entry
    def rob_next(self, rob_entry, instruction_issue_indicator):
        rob_index = int(rob_entry.split("ROB")[1])
        if rob_index == len(self.rob) - 1:
                rob_index = 0
        else:
            rob_index = rob_index + 1
        if self.rob_add_counter == 0:
            rob_add_counter_previous = len(self.rob) - 1
        else:
            rob_add_counter_previous = self.rob_add_counter - 1
        
        if (rob_index == self.rob_add_counter) or (instruction_issue_indicator != "-" and rob_index == rob_add_counter_previous): 
            return -1
        else:
            return "ROB" + str(rob_index)
    
    def rob_print(self):
        print ("------------------------------------------------------------------------------------")
        print ("ROB")
        print ("------------------------------------------------------------------------------------")    
        column_names = ["", "BUSY", "INSTRUCTION", "STATE", "DESTINATION", "VALUE"]
        row_format ="{:^16}" * len(column_names)
        print (row_format.format(*column_names))
        for index, rob_entry in enumerate(self.rob):
            rob_entry_list = ["ROB"+str(index), rob_entry["busy"], rob_entry["instruction"], rob_entry["state"], rob_entry["destination"], rob_entry["value"]]
            print (row_format.format(*rob_entry_list))
        print   