import os
import torch
from PIL import Image
from pathlib import Path
from diffusers import StableDiffusionImg2ImgPipeline


class ImageGenerator:
    def __init__(self, folder_path, output_path, model):
        self.folder_path = folder_path
        self.output_path = output_path

        # Load the stable diffusion model
        self.pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
            model,
            revision="fp16",
            torch_dtype=torch.float16,
        ).to("cuda")

        # Set the random seed for reproducibility
        torch.manual_seed(1000)

    def generate_image(self, image_name, prompt, strength=0.7, guidance_scale=1.5, num_inference_steps=10):
        print(f'image --> {image_name} with prompt: {prompt}')
        image_path = os.path.join(self.folder_path, image_name)
        image_loaded = Image.open(image_path).convert("RGB")
        images = self.pipe(prompt=prompt, image=image_loaded,
                           strength=strength, guidance_scale=guidance_scale,
                           num_inference_steps=num_inference_steps).images
        output_image_path = os.path.join(self.output_path, image_name)
        images[0].save(output_image_path)

    def generate_images(self, prompt, num_images=10):
        file_names = os.listdir(self.folder_path)[:num_images]
        for file_name in file_names:
            self.generate_image(file_name, prompt)


if __name__ == "__main__":
    MODEL = os.environ.get('MODEL')
    FRAMES = os.environ.get('FRAMES')
    OUTPUT = os.environ.get('OUTPUT')
    prompt = 'anime'
    num_images = 10
    image_generator = ImageGenerator(FRAMES, OUTPUT, MODEL)
    image_generator.generate_images(prompt, num_images)
