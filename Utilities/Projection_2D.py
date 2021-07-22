import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

class Projection_2D():
    
    @staticmethod
    def build_covariance_matrix(X):
        """
        compute mean and compute covarinace matrix
        """
        x_bar = np.mean(X, axis = 0)
        N = X.shape[0]
        tilde_X = X - x_bar      
        S = tilde_X.T.dot(tilde_X)/N        
        return S
    
    @staticmethod
    def get_ordered_EigenVectors(S):
        """
        compute eigenvectors & eigenvalues
        """
        eigenvalues, eigenvectors = np.linalg.eig(S)       
        eigenvectors = eigenvectors.T
        arr1inds = eigenvalues.argsort()
        sorted_eig_vec = eigenvectors[arr1inds[::-1]]
        
        return sorted_eig_vec
    
    @staticmethod
    def pick_top_2_EigenVectors(sorted_eig_vec):
        # pick 2 largest eigenvectors
        top_2 = sorted_eig_vec[:2, :].T
        return top_2
    
    @staticmethod
    def get_projected_data(top_2, X):
        projected_data = X.dot(top_2)
        projected_data = projected_data - np.mean(projected_data, axis = 0)
        pca_df = pd.DataFrame(projected_data)
        pca_dict = pca_df.to_dict(orient = "index")
        return projected_data, pca_df, pca_dict
    
    @staticmethod
    def visualize_projected_data(pca_df, pca_dict):
        plt.figure(figsize = (15, 8))
        sns.scatterplot(x = 0, y = 1, data = pca_df, s = 100)
        for idx, coordindates in pca_dict.items():
            plt.text(coordindates[0], coordindates[1] + .01, idx, fontsize = 20)
        plt.title("Projection to 2D", fontsize = 30)
        plt.xlabel("Dimension 0", fontsize = 20)
        plt.ylabel("Dimension 1", fontsize = 20)
        plt.show()
    
    @staticmethod
    def run(X):
        S = Projection_2D.build_covariance_matrix(X)
        sorted_eig_vec = Projection_2D.get_ordered_EigenVectors(S)
        top_2 = Projection_2D.pick_top_2_EigenVectors(sorted_eig_vec)
        projected_data, pca_df, pca_dict = Projection_2D.get_projected_data(top_2, X)
        return projected_data, pca_df, pca_dict