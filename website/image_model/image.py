import os
import subprocess
import torch
import torch.nn.functional as F
from facenet_pytorch import MTCNN, InceptionResnetV1
import numpy as np
from PIL import Image
import cv2
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
from pytorch_grad_cam.utils.image import show_cam_on_image

class FaceForgeryDetector:
    def __init__(self):
        self.device = 'cuda:0' if torch.cuda.is_available() else 'cpu'

        self.mtcnn = MTCNN(
            select_largest=False,
            post_process=False,
            device=self.device
        ).to(self.device).eval()

        self.model = InceptionResnetV1(
            pretrained="vggface2",
            classify=True,
            num_classes=1,
            device=self.device
        )

        checkpoint = torch.load("image_model/image_model_weights.pth", map_location=torch.device('cpu'))
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.to(self.device)
        self.model.eval()

    def predict_image(self, input_image: Image.Image):
        """Predict the label of the input_image"""
        face = self.mtcnn(input_image)
        if face is None:
            raise Exception('No face detected')
        face = face.unsqueeze(0)
        face = F.interpolate(face, size=(256, 256), mode='bilinear', align_corners=False)

        # Convert the face into a numpy array to be able to plot it
        prev_face = face.squeeze(0).permute(1, 2, 0).cpu().detach().int().numpy()
        prev_face = prev_face.astype('uint8')

        face = face.to(self.device)
        face = face.to(torch.float32)
        face = face / 255.0
        face_image_to_plot = face.squeeze(0).permute(1, 2, 0).cpu().detach().int().numpy()

        target_layers = [self.model.block8.branch1[-1]]
        cam = GradCAM(model=self.model, target_layers=target_layers)
        targets = [ClassifierOutputTarget(0)]

        grayscale_cam = cam(input_tensor=face, targets=targets, eigen_smooth=True)
        grayscale_cam = grayscale_cam[0, :]
        visualization = show_cam_on_image(face_image_to_plot, grayscale_cam, use_rgb=True)
        face_with_mask = cv2.addWeighted(prev_face, 1, visualization, 0.5, 0)

        with torch.no_grad():
            output = torch.sigmoid(self.model(face).squeeze(0))
            prediction = "real" if output.item() < 0.5 else "fake"

            real_prediction = 1 - output.item()
            
            fake_prediction = output.item()

            confidences = {
                'real': real_prediction,
                'fake': fake_prediction
            }
        return confidences, face_with_mask

    def predict_video(self, video_path):
        # Open the video file
        cap = cv2.VideoCapture(video_path)

        # Get video properties
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
        fps = cap.get(5)

        # Create VideoWriter object to save the output
        UPLOAD_FOLDER = os.getcwd() + '/temp/output_video.mp4'
        out = cv2.VideoWriter(UPLOAD_FOLDER, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

        while True:
            # Read a frame from the video
            ret, frame = cap.read()
            if not ret:
                break

            # Convert the frame to PIL Image
            input_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            try:
                # Use the predict function for a single image
                confidences, face_with_mask = self.predict_image(input_image)

                # Display the result on the video frame
                cv2.putText(frame, f"Prediction: {max(confidences, key=confidences.get)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # Save the frame to the output video
                out.write(frame)

            except Exception as e:
                # Handle exceptions (e.g., no face detected)
                cv2.putText(frame, f"Error processing frame: {e}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Release the video capture and writer objects
        cap.release()
        out.release()
        
        web_friendly_video = os.getcwd() + '/temp/web_friendly_output_video.mp4'
        ffmpeg_command = f"ffmpeg -i {UPLOAD_FOLDER} -vcodec h264 -acodec aac {web_friendly_video}"
        subprocess.run(ffmpeg_command, shell=True, check=True)
        
        os.remove(UPLOAD_FOLDER)