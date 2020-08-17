# This files defines the Database class, used by the module to quickly query the database and extract the label

# Imports
import os
import h5py
import numpy as np
import warnings
from sklearn.neighbors import KDTree
from scipy.optimize import linear_sum_assignment
from scipy.stats import mode

class Database():
    """
        - For different modality we require a quick search
        in the database to return the label of the person present. 

        - This class has 2 public functions:
        => query(input_feature): return the k closest labels 
                                    and their distance
        => addLabel(name,features,images): create a new .h5 file to store 
                                    the new features.       
        
        - Format of stored data in a folder: 
            -- datadir 
                -- name1.h5
                -- name2.h5 
                    .
                    .   
                    .   
                -- nameN.h5

        - To reduce computation time, I will use sklearn's Kdtree during query time         
    """
    def __init__(self, datadir):
        super(Database, self).__init__()
        """
            Initialize class, 
            @param => datadir : path to folder containing data : str
        """

        # If folder does not exist create one 
        if not os.path.isdir(datadir):
            os.mkdir(datadir)

        self.datadir = datadir # Store the folder path containing on the h5 files

        self.__feature_list = [] # Store the features from the database
        self.__image_list = []   # Store the images from the database
        self.__ind2label_list = [] # Store labels for every feature

        for filename in os.listdir(datadir):
            # Parse the files 

            if filename.split('.')[-1] != 'h5': # All files must be .h5 
                raise TypeError(f"Expected h5py file format, found {filename}")

            data = h5py.File(os.path.join(datadir,filename),'r')
            if 'feature' not in data or 'image' not in data: # All files must contain 'feature' , 'image' dataset
                raise KeyError(f"Data corrupted, h5py.dataset does not contain feature or image")

            features = np.array(data['feature'])
            images = np.array(data['image'])
            name = filename[:-3] # eg. John_Doe.h5 => John Doe  

            # Store data    
            self.__feature_list.extend(features)
            self.__image_list.extend(images)
            self.__ind2label_list.extend(len(features)*[name])

        # Convert to numpy format    
        self.__feature_list = np.array(self.__feature_list)    
        self.__image_list   = np.array(self.__image_list)    
        self.__ind2label_list = np.array(self.__ind2label_list)
            
        if len(self.__feature_list):     

            assert len(self.__feature_list) == len(self.__ind2label_list), \
                    "dimension of features of different labels are not same"

            # Create a kdtree for faster query, reference: https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KDTree.html
            self.kdtree = KDTree(self.__feature_list)     
        else:
            self.kdtree = None   

    def query(self,query_features,thresh):
        """
            Given query features return the nearest neighbours 
            and their distance from the database
            
            @params: 
                query_features: input features to find neighbors 
                                    NxD np.ndarray  
                thresh: distance threshold, if disance less than this then accepted as match

            @returns: 
                label : 2D string array shape: Nxnn np.str_    
                distance: distance to each neighbor: Nxnn np.ndarray  
        """

        # type check
        assert type(query_features) == np.ndarray,\
                f"query feature not np.ndarray but {type(query_features)}"
        assert len(query_features.shape) == 2,\
                f"Expected query feature to be a 2D np.ndarray got {query_features.shape}"        


        # Main code
        N,D = query_features.shape
        
        if len(self.__feature_list) == 0: # If no person exists in database
            return list(range(N)),[],[] 

        # Check dimension size
        assert D==self.__feature_list.shape[1],\
                "query dimension and feature dimension not same"

        # Search index and dist
        ninds,dists = self.kdtree.query_radius(query_features,r=thresh,return_distance=True)  
        
        found = []
        found_labels = []
        not_found = []

        for i,nind in enumerate(ninds):
            if len(nind) == 0: # If could not find any match
                not_found.append(i)    
            elif len(nind) == len(np.unique(nind)): # If all matches are unique
                found.append(i) 
                # Chose the id closet to query
                ind = nind[np.argmin(dists[i])]
                found_labels.append(self.__ind2label_list[ind])
            else: # Or choose the ind most common
                found.append(i)
                label = mode(self.__ind2label_list[ind])[0][0]
                found_labels.append(label)

        return not_found,found,found_labels
        

    def addLabel(self,name,features,images,k=10):
        """
            Add a new person to the database
            
            @params: 
                name: name of the person: string  
                eatures: Features for a particular modality
                              NxD np.ndarray 
                images: Images/Gait Sequence stored for future use
                            NxD np.ndarray 
                k: Number of samples to save 
        """

        # type check
        assert type(name) == str,\
                f"name not str but {type(name)}"

        features = np.array(features)
        images = np.array(images)

        assert type(features) == np.ndarray,\
                f"feature not np.ndarray but {type(features)}"
        assert type(images) == np.ndarray, f"images not np.ndarray but {type(images)}"

        if len(features) == 0 or len(images) == 0:
            return 

        assert len(features.shape) == 2,\
                 f"Expected feature to be a 2D np.ndarray got {features.shape}"        

        # Assert images and features same size
        assert len(features) == len(images), \
                    f"size of features and images not same:{len(features)} {len(images)}"


        print("Reached Here")
        if os.path.isfile(os.path.join(self.datadir,name+'.h5')):
            raise FileExistsError("Unable to save. {name} already exists")

        # Store data in h5 format
        hf = h5py.File(os.path.join(self.datadir,name+'.h5'),'w')
        N = len(features)

        if k >= N: 
            # If k >= number of samples store all samples
            inds = range(N)
        else: 
            # Choose random k
            inds = np.random.permutation(N)[:k]  
        print("Inds:",inds)

        hf.create_dataset('feature',data=features[inds])        
        hf.create_dataset('image',data=images[inds])

        print(hf,hf.keys(),hf['feature'],hf['image'])

        hf.close()

        # Add to current list    
        print(self.__feature_list.shape)
        print(features[inds].shape)

        if len(self.__feature_list) == 0:
            self.__feature_list = features[inds]
            self.__image_list = images[inds]
        else:
            self.__feature_list = np.concatenate([self.__feature_list,features[inds]],axis=0)    
            self.__image_list   = np.concatenate([self.__image_list,images[inds]],axis=0)    
        self.__ind2label_list = np.concatenate([self.__ind2label_list, [name]*len(inds) ])


    def deleteLabel(self,name):
        """
            Delete person from the database 
            @param: name: name of the person: string
        """
        # type check
        assert type(name) == str,\
                f"name not str but {type(name)}"

        path = os.path.join(self.datadir,name+'.h5')        
        if os.path.isfile(path): # Check if file exists
            os.remove(path)

        # Delete from current list    
        with warnings.catch_warnings():
            warnings.simplefilter(action='ignore', category=FutureWarning)
            inds = np.where(self.__ind2label_list == name)[0] # Bug in numpy which cause problems in future versions, basically comparing np.string_array and str creates the warning


        self.__feature_list = np.delete(self.__feature_list,inds,axis=0)    
        self.__image_list = np.delete(self.__image_list,inds,axis=0)    
        self.__ind2label_list = np.delete(self.__ind2label_list,inds)  


class LiveDatabase():
    """
        When the component is running we would need to store data about unknown classes 

        This class has 2 main public functions callable:
        => query(input_feature) return the closest labels and their distance using hungarian algorithm
        => addLabel(ids,features,images) add new traking ids to the list      
    """
    def __init__(self):
        super(LiveDatabase, self).__init__()

        self.__feature_list = []    # Stores features as list 
        self.__image_list = []      # Stores images as list
        self.__unknown_id_dict = {} # Each tracking id can have multiple frames, the dict stores their indices

    def query(self,query_features,thresh):
        """
            Given query features return the nearest neighbours 
            and their distance from the database
            
            @params: 
                query_features: input features to find neighbors 
                                    NxD np.ndarray
                thresh: distance threshold, if disance less than this then accepted as match

            @returns: 
                labels : 1D int array shape: N int array    
                distance: distance to each label: N np.ndarray  
        """

        # type check
        assert type(query_features) == np.ndarray,\
                f"query feature not np.ndarray but {type(query_features)}"
        assert len(query_features.shape) == 2,\
                f"Expected query feature to be a 2D np.ndarray got {query_features.shape}"        

        # Main code
        N,D = query_features.shape

        if len(self.__feature_list) == 0: # If no person exists in database
            return np.full(N,-1),np.full(N,np.inf) 

        # Check dimension size
        assert D==self.__feature_list[0].shape[0],\
                f"query dimension and feature dimension not same:{D} != {self.__feature_list[0].shape[0]}"


        # Search index and dist
        featurelist = np.array(self.__feature_list)
        dist_matrix = np.linalg.norm(query_features[:,None,:] - featurelist[None,...],axis=2)

        tracking_id_list = np.array(list(self.__unknown_id_dict.keys()))
        cost_matrix = np.zeros((N,len(tracking_id_list)))


        for i,id in enumerate(tracking_id_list):
            cost_matrix[:,i] = np.min(dist_matrix[:,self.__unknown_id_dict[id]],axis=1)

        # print(cost_matrix)

        # Using hungarian algorithm(linear assungment for bipartite matching) to find the best match 
        row_ind,col_ind = linear_sum_assignment(cost_matrix)

        # If no match found assign label as -1 and distance as np.inf
        dists = np.full(N,np.inf)
        dists[row_ind] = cost_matrix[row_ind,col_ind]

        labels = np.full(N,-1,dtype=np.int32)
        labels[row_ind] = tracking_id_list[col_ind]

        # print("Labels:",labels)
        # print("Dist:",dists)

        # Apply thresholding
        labels[ dists > thresh] = -1
        dists[  dists > thresh] = np.inf

        return labels,dists
        

    def addLabel(self,ids,features,images):
        """
            Add a new persons to the lists
            
            @params: 
                ids: tracking id of persons: int array  
                features: Features for a particular modality
                              NxD np.ndarray 
                images: Images/Gait Sequence stored for future use
                            NxD np.ndarray 
        """

        # type check
        assert type(ids) == np.ndarray or type(ids) == list,\
                f"ids not list/array but {type(ids)}"
        assert type(features) == np.ndarray,\
                f"feature not np.ndarray but {type(features)}"
        assert type(images) == np.ndarray, f"images not np.ndarray but {type(images)}"

        if len(ids) == 0 or len(features) == 0 or len(images)==0: # Nothing to add
            return 

        assert len(features.shape) == 2,\
                 f"Expected feature to be a 2D np.ndarray got {features.shape}"        

        # Assert images and features same size
        assert len(features) == len(images), \
                    f"size of features and images not same:{len(features)} {len(images)}"


        # check dims 
        if len(self.__feature_list) > 0:
            assert features.shape[1] == self.__feature_list[0].shape[0],\
                     f"dimension of new features do not match: {features.shape[1]} {self.__feature_list[0].shape[0]}"
            assert images.shape[1:] == self.__image_list[0].shape,\
                     f"dimension of new images do not match:{images.shape[1:]} {self.__image_list[0].shape}"

        # Update the dict containing all the tracking ids and index for correspoding features    
        for i,n in enumerate(ids):
            if n not in self.__unknown_id_dict:
                self.__unknown_id_dict[n] = []

            self.__unknown_id_dict[n].append( i + len(self.__feature_list) )

        self.__feature_list.extend(features)
        self.__image_list.extend(images)     

        if sum([ len(self.__unknown_id_dict[x]) for x in self.__unknown_id_dict ]) != len(self.__feature_list) or len(self.__feature_list) != len(self.__image_list):
            raise NotImplementedError("Error in implementation of adding new labels to database")


    def deleteLabel(self,tr_ids):
        """
            Delete the person whose tracking ids is marked 
            
            @param: 
                inds: tracking id of persons: int array  

            @returns:
                features: Features for a particular tracking id
                              NxD np.ndarray 
                images: Images/Gait Sequence stored for future use
                            NxD np.ndarray 
        """

        print(self.__unknown_id_dict,tr_ids)

        if len(self.__unknown_id_dict) == 0: # Nothing in database
            return [],[]

        inds = []
        for c in tr_ids:
            assert c in self.__unknown_id_dict, f"{c} not present in dataset" 
            inds.extend(self.__unknown_id_dict[c])
            del self.__unknown_id_dict[c]
        
        featurelist = np.array(self.__feature_list)    
        image_list = np.array(self.__image_list)
            
        features = featurelist[inds]
        images   = image_list[inds]

        self.__feature_list = list(np.delete(features,inds,axis=0))
        self.__image_list = list(np.delete(images,inds,axis=0))

        return features,images

    def refresh(self,k=1000):
        # If array becomes too large remove the first k numbers
        pass  
