from ultralytics import YOLO
import cv2

model = YOLO('../../YOLO-weights/yolo11l.pt')
results = model("Images/3.png")
img = results[0].plot()

cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
cv2.imshow("Image", img)
cv2.resizeWindow("Image", 1200, 800)
cv2.waitKey(0)
cv2.destroyAllWindows()


