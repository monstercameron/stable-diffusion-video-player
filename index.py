import os
import queue
import imageio
import shutil
import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from dotenv import load_dotenv
from lib.img2img import ImageGenerator
from lib.frames2video import BashScriptRunner


# Load the environment variables from the .env file
load_dotenv()

MODEL = os.environ.get('MODEL')
FRAMES = os.environ.get('FRAMES')
OUTPUT = os.environ.get('OUTPUT')
OUTPUTVIDEOS = os.environ.get('OUTPUTVIDEOS')
VIDEO = os.environ.get('VIDEO')
SCRIPT = os.environ.get('SCRIPT')


class VideoPlayer(tk.Tk):
    def __init__(self, video_path):
        super().__init__()
        self.geometry("1280x700")
        self.video_path = video_path
        self.panel1 = tk.Label(self)
        self.panel1.pack(side=tk.LEFT, padx=10, pady=10)
        self.panel2 = tk.Label(self)
        self.panel2.pack(side=tk.RIGHT, padx=10, pady=10)
        self.video = imageio.get_reader(self.video_path)
        self.frame_gen = self.video.iter_data()
        self.total_frames = self.video.get_length()
        self.current_frame = 0

        self.image_generator = ImageGenerator(FRAMES, OUTPUT, MODEL)

        # Create a text box.
        self.text_var = tk.StringVar()
        self.text_var.set('anime')
        self.text_box = tk.Entry(self, textvariable=self.text_var)
        self.text_box.pack(padx=10, pady=10)

        # Create a progress bar.
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self, variable=self.progress_var, maximum=self.total_frames)
        self.progress_bar.pack(fill=tk.X, padx=10, pady=10)

        # Create sliders for strength, guidance_scale, and num_inference_steps.
        self.strength_var = tk.DoubleVar()
        self.strength_var.set(0.7)
        self.strength_slider = tk.Scale(
            self, variable=self.strength_var, from_=0, to=1, resolution=0.05, length=200,
            label="Strength", orient=tk.HORIZONTAL)
        self.strength_slider.pack(padx=10, pady=10)

        self.guidance_var = tk.DoubleVar()
        self.guidance_var.set(1.5)
        self.guidance_slider = tk.Scale(
            self, variable=self.guidance_var, from_=0, to=10, resolution=0.5, length=200,
            label="Guidance Scale", orient=tk.HORIZONTAL)
        self.guidance_slider.pack(padx=10, pady=10)

        self.steps_var = tk.IntVar()
        self.steps_var.set(50)
        self.steps_slider = tk.Scale(
            self, variable=self.steps_var, from_=0, to=150, resolution=1, length=200,
            label="Num Inference Steps", orient=tk.HORIZONTAL)
        self.steps_slider.pack(padx=10, pady=10)

        # Clear and create the ./frames ./output ./outputvideos directory.
        for folders in [FRAMES, OUTPUT, OUTPUTVIDEOS]:
            if os.path.exists(folders):
                shutil.rmtree(folders)
            os.makedirs(folders)

        # Create a queue to communicate between the main thread and the worker thread.
        self.frame_queue = queue.Queue()

        # Start the worker thread to save frames.
        self.worker_thread = threading.Thread(
            target=self.save_frames_worker, daemon=True)
        self.worker_thread.start()

        self.update_frame()

    def update_frame(self):
        try:
            frame = next(self.frame_gen)
            self.current_frame += 1
        except StopIteration:
            # End of video, loop the video.
            self.frame_gen = self.video.iter_data()
            self.current_frame = 0
            self.update_frame()
            return

        # Determine the size of the square crop.
        height, width, _ = frame.shape
        crop_size = min(height, width)

        # Calculate the starting position for the crop.
        start_x = (width - crop_size) // 2
        start_y = (height - crop_size) // 2

        # Crop the frame to a square.
        frame = frame[start_y:start_y + crop_size, start_x:start_x + crop_size]

        # Resize the cropped frame to 512x512 pixels.
        frame = Image.fromarray(frame).resize((512, 512))

        # Put the frame into the queue to be saved by the worker thread.
        self.frame_queue.put((self.current_frame, frame))

        # Convert the frame to a PhotoImage for display in Tkinter.
        image = ImageTk.PhotoImage(frame)

        # Update the label widget with the current frame.
        self.panel1.config(image=image)
        self.panel1.image = image

        # Update the progress bar.
        self.progress_var.set(self.current_frame)

        # Update the window title with the current frame and total frames.
        self.title(
            f"Video Player - Frame {self.current_frame} / {self.total_frames}")

        # Schedule the next frame update.
        self.after(20, self.update_frame)

    def save_frames_worker(self):
        while True:
            frame_number, frame = self.frame_queue.get()
            frame_file_path = os.path.join(
                FRAMES, f'frame{frame_number:04d}.png')
            imageio.imwrite(frame_file_path, frame)
            self.image_generator.generate_image(
                f'frame{frame_number:04d}.png', self.text_var.get(),
                strength=self.strength_var.get(),
                guidance_scale=self.guidance_var.get(),
                num_inference_steps=self.steps_var.get())
            # t = threading.Thread(target=self.generate_image_thread,
            #                      args=(frame_number,))
            # # Start the thread
            # t.start()

            # Get the latest image from the output folder.
            output_image_path = os.path.join(
                OUTPUT, f'frame{frame_number:04d}.png')
            if os.path.exists(output_image_path):
                output_image = Image.open(output_image_path)
                # output_image = output_image.resize((512, 512))
                output_image = ImageTk.PhotoImage(output_image)
                self.panel2.config(image=output_image)
                self.panel2.image = output_image

    def on_closing(self):
        self.video.close()
        self.destroy()

    def make_video(self):
        runner = BashScriptRunner(SCRIPT)
        output = runner.run_script()
        print(output)

    def delete_output_files(self, dir_path):
        files = os.listdir(dir_path)
        for file in files:
            file_path = os.path.join(dir_path, file)
            os.remove(file_path)

    # Define a function to generate an image in a separate thread
    def generate_image_thread(self, frame_number):
        self.image_generator.generate_image(
            f'frame{frame_number:04d}.png',
            self.text_var.get(),
            strength=self.strength_var.get(),
            guidance_scale=self.guidance_var.get(),
            num_inference_steps=self.steps_var.get())


if __name__ == "__main__":
    # print(FRAMES, OUTPUT, MODEL,  VIDEO)
    image_generator = ImageGenerator(FRAMES, OUTPUT, MODEL)
    player = VideoPlayer(VIDEO)
    player.protocol("WM_DELETE_WINDOW", player.on_closing)
    player.mainloop()
