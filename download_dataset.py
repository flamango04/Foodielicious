#%%
import os
import shutil
import kagglehub

# Specify the target folder
custom_folder = "/Users/macbook/Documents/GitHub/Foodielicious/dataset"

# Create the folder if it does not exist
os.makedirs(custom_folder, exist_ok=True)

# Download the dataset to the default location
path = kagglehub.dataset_download("shuyangli94/food-com-recipes-and-user-interactions")

# Move downloaded files to the custom folder
for file_name in os.listdir(path):
    shutil.move(os.path.join(path, file_name), custom_folder)

print(f"Dataset moved to: {custom_folder}")
