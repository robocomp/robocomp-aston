# This files defines the TrackingId2Label class, used by the module to find out which tracking index maps to which label from the database

# Imports
import os
import numpy as np

class TrackingId2Label():
    """
        -  In a dictionary we store the mapping from a tracking Id(obtained from Center Track) of a person to the string label 
        # label =
            # "unknown:tracking_id" if id2label[id] = -1 
            # "name" if id2label[id] = string
            # id2label[id2label[id]] if id2label[id] = int # A person can have multiple tracking id (due to occlusion or re-apperance) 

        - This class has these public functions:
        => query(inds): Return labels for every tracking id
        => not_present(inds): Check for tracking ids not present in the dict   
        => find_unknown(inds): Check if tracking id maps to a known or unkown person, return the parent tracking ids for persons not present in the database  
        => add(inds,labels): Add new tracking ids 
        => update(inds, new_label): update tracking ids with new labels 
        
        This is similiar to how union find is used for Krushkal's method in minimum spanning tree
    """
    def __init__(self):
        super(TrackingId2Label, self).__init__()
        """
            Initialize class, 
        """
        self.dict = {} # Store the tracking index and corresponding label

    def _find(self,ind):
        if ind not in self.dict:
            raise KeyError(f"Unable to find {ind} in dictionary")
        try:
            if type(self.dict[ind]) == int:
                if self.dict[ind] == -1:
                    return ind
                else: 
                    return self._find(self.dict[ind])
            elif type(self.dict[ind]) == str:
                return self.dict[ind]

            else: 
                raise KeyError(f"During query ind got:{type(self.dict[ind])} only int/str accepted")
        except RecursionError as r:
            print(f"[RecursionError]: dict[{ind}]:{self.dict[ind]}::",r) 

    def children(self,ind):
        """
            If we self.dict[ind] == -1 then its defined as parent
            For every parent return all the associated tracking ids

            @param: 
                int: tracking id
        """
        return [ k for k in self.dict if self._find(k) == ind]

    def query(self,inds):
        """
            Given query int/list return the labels             
            @param: inds: list of tracking ind : list  

            @returns: 
                    unknown_index: list of index where tracking ind maps to unknown person
                    known_index  : list of index where tracking ind maps to   known person
                    known_labels : list of name  where tracking ind maps to   known person
        """

        # type check
        assert type(inds) in [list,np.ndarray],\
                f"inds not list/np.ndarray but {type(inds)}"        

        labels = []
        for i,index in enumerate(inds):
            if index not in self.dict:
                raise KeyError(f"Unable to find tracking:{index} in dictionary")
            else:
                label = self._find(index)
                if type(label) == int:
                    labels.append(f"unknown:{label}")
                else:
                    labels.append(label)
        return labels                     

    def not_present(self,inds):
        """
            Given id list find out which id is not present in the dictionary 
            and return the parent tracking index
            
            @param: inds: list of tracking id

            @returns: 
                    not_inds: list of index where tracking id maps no one 
        """
        assert type(inds) in [list,np.ndarray],\
                f"inds not list/np.ndarray but {type(inds)}"         
        
        not_inds = []
        for i,x in enumerate(inds):
            if x not in self.dict:
                not_inds.append(i)
        return not_inds

    def find_unknown(self,inds):
        """
            Given id list find out which id is not present in the database 
            and return the parent tracking index
            
            @param: inds: list of tracking id

            @returns: 
                    unkown_inds: list of index where tracking id maps no one 
                    unkown_ids: list of parent tracking ids for each unkown_inds 
        """
        assert type(inds) in [list,np.ndarray],\
                f"inds not list/np.ndarray but {type(inds)}"         
        
        unknown_inds = []
        unknown_ids = []
        for i,ind in enumerate(inds):
            assert ind in self.dict,f"Index {ind} not present int id2label"

            # ids = self._find(ind)
            # if type(ids) == str: 
            #     continue
            if self.dict[ind] == -1:
                unknown_inds.append(i)
                # unknown_ids.append(ids)
                unknown_ids.append(ind)

        return unknown_inds,unknown_ids

    def add(self,tracking_inds,labels):
        """
            Add new tracking ids into id2label

            @param: tracking_inds: list of tracking ids: int array 
            @param: labels: list of labels: int/str array 
        """

        # Iterate over the input
        for tr_id,l in zip(tracking_inds,labels):

            # If already present, the raise error
            assert tr_id not in self.dict,f"Index {tr_id} already present"

            # Convert from any numpy format to python format
            if np.issubdtype(type(l), np.integer): 
                l = int(l)
            elif np.issubdtype(type(l), np.character): 
                l = str(l)

            # Assert only int or str type passed as input            
            assert type(l) == int or type(l) == str,f"Label of type:{type(l)} only int/str allowed"

            # Assert tr_id != l 
            assert l != tr_id, "Error tr_id and label passes as same value"            
            self.dict[tr_id] = l # Add label

    def update(self,tracking_inds,new_label):
        """
            Update tracking ids of id2label with new labels

            @param: tracking_inds: list of tracking ids: int array 
            @param: labels: list of labels: int/str array 
        """
        # print("Updating Dict:")

        # Iterate over the input
        for tr_id,l in zip(tracking_inds,new_label):
            print(f"Tr Id:{tr_id} New Label:{l}")

            # If already present, the raise error
            assert tr_id in self.dict,f"Index {tr_id} not present int id2label"

            # Convert from any numpy format to python format
            if np.issubdtype(type(l), np.integer): 
                l = int(l)
            elif np.issubdtype(type(l), np.character): 
                l = str(l)

            # Assert only int or str type passed as input            
            assert type(l) == int or type(l) == str,f"Label of type:{type(l)} only int/str allowed"

            if l == -1:
                continue


            ptr_id = self._find(tr_id) # id2label can have multiple tracking ids for same person, hence similiar to union-find find the parent
            # TODO convert search from logn to log*n by updating every children also 
            assert self.dict[ptr_id] == -1, f"Expected id2label[{tr_id}] be -1, found:{self.dict[tr_id]}"


            if type(l) == int: # If linking tracking_id with new tracking id, then make sure new tracking id != parent of tracking id
               if ptr_id == self._find(l):
                    continue  
            self.dict[ptr_id] = l

