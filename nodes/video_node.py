import os
import configparser
import torch
from PIL import Image
import tempfile
import numpy as np
import requests
from urllib.parse import urlparse
import cv2
from fal_client.client import SyncClient

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
config_path = os.path.join(parent_dir, "config.ini")
config = configparser.ConfigParser()
config.read(config_path)

# First set environment variable
try:
    fal_key = config['API']['FAL_KEY']

    os.environ["FAL_KEY"] = fal_key

except KeyError:
    print("Error: FAL_KEY not found in config.ini")

# Create the client with your API key
fal_client = SyncClient(key=fal_key)

def upload_image(image):
    try:
        # Convert the image tensor to a numpy array
        if isinstance(image, torch.Tensor):
            image_np = image.cpu().numpy()
        else:
            image_np = np.array(image)

        # Ensure the image is in the correct format (H, W, C)
        if image_np.ndim == 4:
            image_np = image_np.squeeze(0)  # Remove batch dimension if present
        if image_np.ndim == 2:
            image_np = np.stack([image_np] * 3, axis=-1)  # Convert grayscale to RGB
        elif image_np.shape[0] == 3:
            image_np = np.transpose(image_np, (1, 2, 0))  # Change from (C, H, W) to (H, W, C)

        # Normalize the image data to 0-255 range
        if image_np.dtype == np.float32 or image_np.dtype == np.float64:
            image_np = (image_np * 255).astype(np.uint8)

        # Convert to PIL Image
        pil_image = Image.fromarray(image_np)

        # Save the image to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            pil_image.save(temp_file, format="PNG")
            temp_file_path = temp_file.name

        # Use the client instance instead of the imported function
        image_url = fal_client.upload_file(temp_file_path)
        return image_url
    except Exception as e:
        print(f"Error uploading image: {str(e)}")
        return None
    finally:
        # Clean up temp file
        if 'temp_file_path' in locals():
            os.unlink(temp_file_path)

class MiniMaxNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "image": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate_video"
    CATEGORY = "FAL/VideoGeneration"

    def generate_video(self, prompt, image):
        try:
            image_url = upload_image(image)
            if not image_url:
                return ("Error: Unable to upload image.",)

            arguments = {
                "prompt": prompt,
                "image_url": image_url,
            }

            handler = fal_client.submit("fal-ai/minimax-video/image-to-video", arguments=arguments)
            result = handler.get()
            video_url = result["video"]["url"]
            return (video_url,)
        except Exception as e:
            print(f"Error generating video: {str(e)}")
            return ("Error: Unable to generate video.",)
        
class MiniMaxTextToVideoNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate_video"
    CATEGORY = "FAL/VideoGeneration"

    def generate_video(self, prompt):
        try:
            arguments = {
                "prompt": prompt,
            }

            handler = fal_client.submit("fal-ai/minimax-video", arguments=arguments)
            result = handler.get()
            video_url = result["video"]["url"]
            return (video_url,)
        except Exception as e:
            print(f"Error generating video: {str(e)}")
            return ("Error: Unable to generate video.",)

class KlingNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "duration": (["5", "10"], {"default": "5"}),
                "aspect_ratio": (["16:9", "9:16", "1:1"], {"default": "16:9"}),
            },
            "optional": {
                "image": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate_video"
    CATEGORY = "FAL/VideoGeneration"

    def generate_video(self, prompt, duration, aspect_ratio, image=None):
        arguments = {
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
        }

        try:
            if image is not None:
                image_url = upload_image(image)
                if image_url:
                    arguments["image_url"] = image_url
                    handler = fal_client.submit("fal-ai/kling-video/v1/standard/image-to-video", arguments=arguments)
                else:
                    return ("Error: Unable to upload image.",)
            else:
                handler = fal_client.submit("fal-ai/kling-video/v1/standard/text-to-video", arguments=arguments)

            result = handler.get()
            video_url = result["video"]["url"]
            return (video_url,)
        except Exception as e:
            print(f"Error generating video: {str(e)}")
            return ("Error: Unable to generate video.",)

class KlingProNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "duration": (["5", "10"], {"default": "5"}),
                "aspect_ratio": (["16:9", "9:16", "1:1"], {"default": "16:9"}),
            },
            "optional": {
                "image": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate_video"
    CATEGORY = "FAL/VideoGeneration"

    def generate_video(self, prompt, duration, aspect_ratio, image=None):
        arguments = {
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
        }

        try:
            if image is not None:
                image_url = upload_image(image)
                if image_url:
                    arguments["image_url"] = image_url
                    handler = fal_client.submit("fal-ai/kling-video/v1/pro/image-to-video", arguments=arguments)
                else:
                    return ("Error: Unable to upload image.",)
            else:
                handler = fal_client.submit("fal-ai/kling-video/v1/pro/text-to-video", arguments=arguments)

            result = handler.get()
            video_url = result["video"]["url"]
            return (video_url,)
        except Exception as e:
            print(f"Error generating video: {str(e)}")
            return ("Error: Unable to generate video.",)

class RunwayGen3Node:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "image": ("IMAGE",),
                "duration": (["5", "10"], {"default": "5"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate_video"
    CATEGORY = "FAL/VideoGeneration"

    def generate_video(self, prompt, image, duration):
        try:
            image_url = upload_image(image)
            if not image_url:
                return ("Error: Unable to upload image.",)

            arguments = {
                "prompt": prompt,
                "image_url": image_url,
                "duration": duration,
            }

            handler = fal_client.submit("fal-ai/runway-gen3/turbo/image-to-video", arguments=arguments)
            result = handler.get()
            video_url = result["video"]["url"]
            return (video_url,)
        except Exception as e:
            print(f"Error generating video: {str(e)}")
            return ("Error: Unable to generate video.",)

class LumaDreamMachineNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "mode": (["text-to-video", "image-to-video"], {"default": "text-to-video"}),
                "aspect_ratio": (["16:9", "9:16", "4:3", "3:4", "21:9", "9:21"], {"default": "16:9"}),
            },
            "optional": {
                "image": ("IMAGE",),
                "loop": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate_video"
    CATEGORY = "FAL/VideoGeneration"

    def generate_video(self, prompt, mode, aspect_ratio, image=None, loop=False):
        arguments = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "loop": loop,
        }

        try:
            if mode == "image-to-video":
                if image is None:
                    return ("Error: Image is required for image-to-video mode.",)
                image_url = upload_image(image)
                if not image_url:
                    return ("Error: Unable to upload image.",)
                arguments["image_url"] = image_url
                endpoint = "fal-ai/luma-dream-machine/image-to-video"
            else:
                endpoint = "fal-ai/luma-dream-machine"

            handler = fal_client.submit(endpoint, arguments=arguments)
            result = handler.get()
            video_url = result["video"]["url"]
            return (video_url,)
        except Exception as e:
            print(f"Error generating video: {str(e)}")
            return ("Error: Unable to generate video.",)

class LoadVideoURL:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "url": ("STRING", {"default": "https://example.com/video.mp4"}),
                "force_rate": ("INT", {"default": 0, "min": 0, "max": 60, "step": 1}),
                "force_size": (["Disabled", "Custom Height", "Custom Width", "Custom", "256x?", "?x256", "256x256", "512x?", "?x512", "512x512"],),
                "custom_width": ("INT", {"default": 512, "min": 0, "max": 8192, "step": 8}),
                "custom_height": ("INT", {"default": 512, "min": 0, "max": 8192, "step": 8}),
                "frame_load_cap": ("INT", {"default": 0, "min": 0, "max": 1000000, "step": 1}),
                "skip_first_frames": ("INT", {"default": 0, "min": 0, "max": 1000000, "step": 1}),
                "select_every_nth": ("INT", {"default": 1, "min": 1, "max": 1000000, "step": 1}),
            },
        }

    RETURN_TYPES = ("IMAGE", "INT", "VHS_VIDEOINFO")
    RETURN_NAMES = ("frames", "frame_count", "video_info")
    FUNCTION = "load_video_from_url"
    CATEGORY = "video"

    def load_video_from_url(self, url, force_rate, force_size, custom_width, custom_height, frame_load_cap, skip_first_frames, select_every_nth):
        # Download the video to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
            response = requests.get(url, stream=True)
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        # Load the video using OpenCV
        cap = cv2.VideoCapture(temp_file_path)
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / fps

        # Calculate target size
        if force_size != "Disabled":
            if force_size == "Custom Width":
                new_height = int(height * (custom_width / width))
                new_width = custom_width
            elif force_size == "Custom Height":
                new_width = int(width * (custom_height / height))
                new_height = custom_height
            elif force_size == "Custom":
                new_width, new_height = custom_width, custom_height
            else:
                target_width, target_height = map(int, force_size.replace("?", "0").split("x"))
                if target_width == 0:
                    new_width = int(width * (target_height / height))
                    new_height = target_height
                else:
                    new_height = int(height * (target_width / width))
                    new_width = target_width
        else:
            new_width, new_height = width, height

        frames = []
        frame_count = 0

        for i in range(total_frames):
            ret, frame = cap.read()
            if not ret:
                break

            if i < skip_first_frames:
                continue

            if (i - skip_first_frames) % select_every_nth != 0:
                continue

            if force_size != "Disabled":
                frame = cv2.resize(frame, (new_width, new_height))

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = torch.from_numpy(frame).float() / 255.0
            frames.append(frame)

            frame_count += 1

            if frame_load_cap > 0 and frame_count >= frame_load_cap:
                break

        cap.release()
        os.unlink(temp_file_path)

        frames = torch.stack(frames)

        video_info = {
            "source_fps": fps,
            "source_frame_count": total_frames,
            "source_duration": duration,
            "source_width": width,
            "source_height": height,
            "loaded_fps": fps if force_rate == 0 else force_rate,
            "loaded_frame_count": frame_count,
            "loaded_duration": frame_count / (fps if force_rate == 0 else force_rate),
            "loaded_width": new_width,
            "loaded_height": new_height,
        }

        return (frames, frame_count, video_info)

class VideoUpscalerNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_url": ("STRING", {"default": ""}),
                "scale": ("FLOAT", {"default": 2.0, "min": 1.0, "max": 4.0, "step": 0.5}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "upscale_video"
    CATEGORY = "FAL/VideoGeneration"

    def upscale_video(self, video_url, scale):
        try:
            arguments = {
                "video_url": video_url,
                "scale": scale
            }

            handler = fal_client.submit("fal-ai/video-upscaler", arguments=arguments)
            result = handler.get()
            video_url = result["video"]["url"]
            return (video_url,)
        except Exception as e:
            print(f"Error upscaling video: {str(e)}")
            return ("Error: Unable to upscale video.",)

class MiniMaxSubjectReferenceNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "subject_reference_image": ("IMAGE",),
                "prompt_optimizer": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate_video"
    CATEGORY = "FAL/VideoGeneration"

    def generate_video(self, prompt, subject_reference_image, prompt_optimizer):
        try:
            image_url = upload_image(subject_reference_image)
            if not image_url:
                return ("Error: Unable to upload subject reference image.",)

            arguments = {
                "prompt": prompt,
                "subject_reference_image_url": image_url,
                "prompt_optimizer": prompt_optimizer
            }

            handler = fal_client.submit("fal-ai/minimax/video-01-subject-reference", arguments=arguments)
            result = handler.get()
            video_url = result["video"]["url"]
            return (video_url,)
        except Exception as e:
            print(f"Error generating video: {str(e)}")
            return ("Error: Unable to generate video.",)

class Veo2ImageToVideoNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "image": ("IMAGE",),
                "aspect_ratio": (["auto", "auto_prefer_portrait", "16:9", "9:16"], {"default": "auto"}),
                "duration": (["5s", "6s", "7s", "8s"], {"default": "5s"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate_video"
    CATEGORY = "FAL/VideoGeneration"

    def generate_video(self, prompt, image, aspect_ratio, duration):
        try:
            image_url = upload_image(image)
            if not image_url:
                return ("Error: Unable to upload image.",)

            arguments = {
                "prompt": prompt,
                "image_url": image_url,
                "aspect_ratio": aspect_ratio,
                "duration": duration,
            }

            handler = fal_client.submit("fal-ai/veo2/image-to-video", arguments=arguments)
            result = handler.get()
            video_url = result["video"]["url"]
            return (video_url,)
        except Exception as e:
            print(f"Error generating video: {str(e)}")
            return ("Error: Unable to generate video.",)

# Update Node class mappings
NODE_CLASS_MAPPINGS = {
    "Kling_fal": KlingNode,
    "KlingPro_fal": KlingProNode,
    "RunwayGen3_fal": RunwayGen3Node,
    "LumaDreamMachine_fal": LumaDreamMachineNode,
    "LoadVideoURL": LoadVideoURL,
    "MiniMax_fal": MiniMaxNode,
    "MiniMaxTextToVideo_fal": MiniMaxTextToVideoNode,
    "MiniMaxSubjectReference_fal": MiniMaxSubjectReferenceNode,
    "VideoUpscaler_fal": VideoUpscalerNode,
    "Veo2ImageToVideo_fal": Veo2ImageToVideoNode,
}

# Update Node display name mappings
NODE_DISPLAY_NAME_MAPPINGS = {
    "Kling_fal": "Kling Video Generation (fal)",
    "KlingPro_fal": "Kling Pro Video Generation (fal)",
    "RunwayGen3_fal": "Runway Gen3 Image-to-Video (fal)",
    "LumaDreamMachine_fal": "Luma Dream Machine (fal)",
    "LoadVideoURL": "Load Video from URL",
    "MiniMax_fal": "MiniMax Video Generation (fal)",
    "MiniMaxTextToVideo_fal": "MiniMax Text-to-Video (fal)",
    "MiniMaxSubjectReference_fal": "MiniMax Subject Reference (fal)",
    "VideoUpscaler_fal": "Video Upscaler (fal)",
    "Veo2ImageToVideo_fal": "Google Veo2 Image-to-Video (fal)",
}