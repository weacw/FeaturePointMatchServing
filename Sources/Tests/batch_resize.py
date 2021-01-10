import os 
import cv2
import numpy as np

class batch_resize():
    def __init__(self):        
        pass


    def batchResize(self,images_path):
        result = {}
        files = [os.path.join(images_path, p) for p in sorted(os.listdir(images_path))]
        scale_percent = 2
        for f in files:       
            img = self.path_to_image(f)
            #get size
            height, width,channels = img.shape
            
            # Create a black image
            x = height if height > width else width
            y = height if height > width else width
            square= np.zeros((x,y,channels), np.uint8)
            #
            #This does the job
            #
            square[int((y-height)/2):int(y-(y-height)/2), int((x-width)/2):int(x-(x-width)/2)] = img
            path,fileName = os.path.split(f)
            cv2.imwrite(f"../Tests/Batch/{fileName}",square)
            # cv2.imwrite(out_img,square)
            # cv2.imshow("original", img)
            # cv2.imshow("black square", square)
            # cv2.waitKey(0)     
            # img = self.path_to_image(f)
            # width_scale_percent = 800/img.shape[1]
            # height_scale_percent = 800/img.shape[0]
            # width = int(img.shape[1] * width_scale_percent )
            # height = int(img.shape[0] * height_scale_percent)
            # dsize = (width, height)
            # output = cv2.resize(img, dsize)
            # rezie_img = output
            # path,fileName = os.path.split(f)              
            # cv2.imwrite(f"../Tests/Batch/{fileName}",rezie_img)

    def path_to_image(self, path):
        return cv2.imread(path, cv2.IMREAD_COLOR)    

    def crop_center(self, img, dim=[512, 512]):
        width, height = img.shape[1], img.shape[0]
        crop_width = dim[0] if dim[0] < img.shape[1] else img.shape[1]
        crop_height = dim[1] if dim[1] < img.shape[0] else img.shape[0]
        mid_x, mid_y = int(width/2), int(height/2)
        cw2, ch2 = int(crop_width/2), int(crop_height/2)
        crop_img = img[mid_y-ch2:mid_y+ch2, mid_x-cw2:mid_x+cw2]
        print(crop_img.shape)
        crop_img = np.uint8(
            np.clip((2 * (np.int16(crop_img) - 60) +50), 0, 255))
        return crop_img        


if __name__ == "__main__":
   batchResize = batch_resize() 
   batchResize.batchResize("../Tests/Markers/")