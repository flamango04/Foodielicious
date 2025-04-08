#%%
from diffusers import StableDiffusionPipeline
import torch
from PIL import Image
import matplotlib.pyplot as plt

# Load Stable Diffusion model
def load_model():
    model_id = "CompVis/stable-diffusion-v1-4"  # You can use other versions if available
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
    pipe = pipe.to("cpu")  
    return pipe

# Generate food image from food name
def generate_food_image(food_name):
    pipe = load_model()
    print(f"Generating image for: {food_name}")
    image = pipe(food_name).images[0]  # Generate the image
    return image

# Display the generated image
def show_image(image):
    plt.imshow(image)
    plt.axis("off")  # Hide axes for better display
    plt.show()

# Example usage
if __name__ == "__main__":
    food_name = "A plate of Spaghetti Bolognese with basil garnish"
    image = generate_food_image(food_name)
    show_image(image)
