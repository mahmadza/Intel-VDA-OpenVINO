import cv2
import os
from moviepy import VideoFileClip

class VideoProcessor:
    @staticmethod
    def process_video(file_path, output_dir="temp"):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Extract audio
        video = VideoFileClip(file_path)
        audio_path = os.path.join(output_dir, "temp_audio.wav")
        video.audio.write_audiofile(audio_path, codec='pcm_s16le')
        
        # Extract Keyframes (1 frame every 2 seconds for a 1-min video)
        frame_paths = []
        cap = cv2.VideoCapture(file_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        interval = int(fps * 2) # Every 2 seconds
        
        count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            if count % interval == 0:
                p = os.path.join(output_dir, f"frame_{count}.jpg")
                cv2.imwrite(p, frame)
                frame_paths.append(p)
            count += 1
        cap.release()
        
        return audio_path, frame_paths