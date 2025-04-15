from PyQt5.QtCore import QPoint
import pyautogui
import numpy as np
# from sam_predictor import FastSAMPredictor
from sam2_predictor import FastSAMPredictor



class ImageFrameManager:
    def __init__(self, image_frame, star_marker):
        self.image_frame = image_frame
        self.star_marker = star_marker

        # self.sam = FastSAMPredictor(model_type='vit_b', device='cpu')
        self.sam = FastSAMPredictor(model_cfg="configs/sam2.1/sam2.1_hiera_s.yaml",checkpoint="sam2.1_hiera_small.pt", device='cpu')


    def get_star_position(self):
        return self.star_marker.pos()

    def get_star_position_global(self):
        return self.star_marker.mapToGlobal(QPoint(0, 0))

    def get_screenshot(self):
        self.star_marker.move(2, 2)
        top_left = self.image_frame.mapToGlobal(self.image_frame.pos())
        width = self.image_frame.width()
        height = self.image_frame.height()
        screenshot = pyautogui.screenshot(region=(top_left.x(), top_left.y(), width, height))
        return np.array(screenshot.convert("RGB"))
    
    def run_sam(self):
        # Run SAM
        star_position=self.get_star_position()
        screenshot_np=self.get_screenshot()

        self.sam.set_image(screenshot_np)
        segmented_image, binary_mask = self.sam.segment_point(star_position.x(), star_position.y())
        return segmented_image, binary_mask
