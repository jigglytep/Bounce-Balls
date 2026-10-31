import os
import glob
import cv2
import numpy as np

#############################################
#   Andrew Chao - andrewchao7000@gmail.com  #
#   6/1/2026                                #
#############################################

def do_nothing(val):
    pass
def get_bounds():
    h_lower = cv2.getTrackbarPos("hue min", 'Color Calibration Window')
    h_upper = cv2.getTrackbarPos("hue max", 'Color Calibration Window')

    s_lower = cv2.getTrackbarPos("sat min", 'Color Calibration Window')
    s_upper = cv2.getTrackbarPos("sat max", 'Color Calibration Window')

    v_lower = cv2.getTrackbarPos("val min", 'Color Calibration Window')
    v_upper = cv2.getTrackbarPos("val max", 'Color Calibration Window')

    lower_bound = np.array([h_lower, s_lower, v_lower])
    upper_bound = np.array([h_upper, s_upper, v_upper])

    return lower_bound, upper_bound
def mouse_function(event, x, y, flags, param):
    if event == cv2.EVENT_FLAG_LBUTTON:
        update_calibration_points(param, x,y)

def update_calibration_points(points_list, x,y):
    if len(points_list) < 4:
        points_list.append((x,y))

#updates lower and upper
def calibrate_color(camera_num, current_lower_bound, current_upper_bound):
    lower_bound, upper_bound = current_lower_bound, current_upper_bound

    capture = cv2.VideoCapture(camera_num, cv2.CAP_V4L2)
    window_name = 'Color Calibration Window'
    cv2.namedWindow(window_name)
    cv2.moveWindow(window_name, 100, 100)

    #trackerbars
    cv2.createTrackbar("hue min", window_name, int(lower_bound[0]), 179, do_nothing)
    cv2.createTrackbar("hue max", window_name, int(upper_bound[0]), 179, do_nothing)

    cv2.createTrackbar("sat min", window_name, int(lower_bound[1]), 255, do_nothing)
    cv2.createTrackbar("sat max", window_name, int(upper_bound[1]), 255, do_nothing)

    cv2.createTrackbar("val min", window_name, int(lower_bound[2]), 255, do_nothing)
    cv2.createTrackbar("val max", window_name, int(upper_bound[2]), 255, do_nothing)

    latest_hsv = [None]

    def on_color_click(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and latest_hsv[0] is not None:
            hsv_img = latest_hsv[0]
            h_img, w_img = hsv_img.shape[:2]
            if 0 <= y < h_img and 0 <= x < w_img:
                # Sample a small 5x5 patch around the click for stability
                y0, y1 = max(0, y - 2), min(h_img, y + 3)
                x0, x1 = max(0, x - 2), min(w_img, x + 3)
                patch = hsv_img[y0:y1, x0:x1]
                h_val = int(np.median(patch[:, :, 0]))
                s_val = int(np.median(patch[:, :, 1]))
                v_val = int(np.median(patch[:, :, 2]))

                cv2.setTrackbarPos("hue min", window_name, max(0, h_val - 20))
                cv2.setTrackbarPos("hue max", window_name, min(179, h_val + 20))
                cv2.setTrackbarPos("sat min", window_name, max(25, s_val - 60))
                cv2.setTrackbarPos("sat max", window_name, 255)
                cv2.setTrackbarPos("val min", window_name, max(25, v_val - 70))
                cv2.setTrackbarPos("val max", window_name, 255)
                print(f"Sampled tape HSV=({h_val}, {s_val}, {v_val})")

    cv2.setMouseCallback(window_name, on_color_click)

    #instructions
    text = "Click tape to auto-pick color (or use sliders), press ENTER to save"
    position = (15, 30)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    color = (0, 255, 0)
    thickness = 2


    while True:
        ret, frame = capture.read()
        if not ret:
            print("failed to capture video")
            break

        #mask
        lower_bound, upper_bound = get_bounds()
        hsv_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        latest_hsv[0] = hsv_frame
        mask = cv2.inRange(hsv_frame, lower_bound, upper_bound)

        #combine original & mask (keep dim background visible so you can click the tape)
        masked_frame = cv2.bitwise_and(frame, frame, mask=mask)
        display_frame = cv2.addWeighted(frame, 0.2, masked_frame, 0.8, 0)
        # Highlight detected mask outline in bright green
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(display_frame, contours, -1, (0, 255, 0), 2)

        #display text
        cv2.putText(display_frame, text, position, font, font_scale, color, thickness, cv2.LINE_AA)

        #display video
        cv2.imshow(window_name, display_frame)

        if cv2.waitKey(1) & 0xFF == 13:
            break

    capture.release()
    cv2.destroyAllWindows()

    print("Calibrated Color")
    #like c++ pass by reference (i think loll)
    current_lower_bound[:] = lower_bound
    current_upper_bound[:] = upper_bound

#returns calibration points
def find_calibration_points(video_capture_device_number):
    calibration_points = []
    capture = cv2.VideoCapture(video_capture_device_number, cv2.CAP_V4L2)
    cv2.namedWindow('Projection Calibration Window')
    cv2.moveWindow('Projection Calibration Window', 100, 100)

    # mouse click detection event
    cv2.setMouseCallback('Projection Calibration Window', mouse_function, param=calibration_points)

    # instructions
    text = ["UPPER LEFT", "UPPER RIGHT", "LOWER RIGHT", "LOWER LEFT"]
    position = (15, 30)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    color = (0, 255, 0)
    thickness = 2

    #colors
    pink = (140,20,255)


    while True:
        ret, frame = capture.read()

        if not ret:
            print("failed to capture video")
            break

        #display text
        if len(calibration_points) < 4:
            cv2.putText(frame, "Click " + text[len(calibration_points)] + " Corner",
                    position, font, font_scale, color, thickness, cv2.LINE_AA)
        else:
            cv2.putText(frame, "hit ENTER to confirm", position, font, font_scale, color, thickness, cv2.LINE_AA)
            cv2.putText(frame, "hit 'r' to redo ", (15,60), font, font_scale, color, thickness, cv2.LINE_AA)

        #display points
        for point in calibration_points:
            cv2.drawMarker(frame,point, pink, markerType=cv2.MARKER_CROSS, markerSize=15, thickness=3)

        #display lines between points
        overlay = frame.copy()
        if len(calibration_points) > 0:
            points = np.array(calibration_points, dtype=np.int32)
            cv2.fillPoly(overlay, [points], pink)

        #combine overlay and video
        frame_with_overlay = cv2.addWeighted(frame, 0.7, overlay, 0.3, 0)

        #display video
        cv2.imshow('Projection Calibration Window', frame_with_overlay)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('r'):
            calibration_points.clear()
        elif key == 13 and len(calibration_points) == 4:
            print("Projection Calibration Success")
            break

    capture.release()
    cv2.destroyAllWindows()
    return calibration_points

#returns homography matrix
def calculate_homography_matrix(calibration_points,pygame_width, pygame_height):
    if len(calibration_points) != 4:
        print("Warning: 4 calibration points were not selected; defaulting to full 640x480 camera frame.")
        calibration_points = [(0, 0), (640, 0), (640, 480), (0, 480)]
    source_points = np.array(calibration_points, dtype=np.float32)
    destination_points = np.array([[0, 0], [pygame_width, 0], [pygame_width, pygame_height], [0, pygame_height]], dtype=np.float32)
    homography_matrix = cv2.getPerspectiveTransform(source_points, destination_points)

    return homography_matrix

#returns mapped_frame
def map_frame(original_frame, homography_matrix, pygame_width, pygame_height):
    mapped_frame = cv2.warpPerspective(original_frame, homography_matrix, (pygame_width, pygame_height))
    return mapped_frame

#returns mapped polygon <-- we dont use loll just keeping just in case
def map_polygon(polygon, homography_matrix):
    points = np.array(polygon, dtype=np.float32).reshape(-1, 1, 2)

    transformed_points = cv2.perspectiveTransform(points, homography_matrix)
    mapped_polygon = transformed_points.reshape(-1, 2).astype(np.int32).tolist()


    return mapped_polygon

#returns mask frame
def _get_mask(frame, lower_bound, upper_bound):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    masked_frame = cv2.inRange(hsv_frame, lower_bound, upper_bound)

    return masked_frame

def _get_platform_polygons(frame, lower_bound, upper_bound):
    accuracy = 0.001 #smaller means more points
    minimum_area = 200 #minimum area threshold
    max_area = 0.4 * frame.shape[0] * frame.shape[1]
    platform_polygons = []

    masked_frame = _get_mask(frame, lower_bound, upper_bound)
    contour_list, ret = cv2.findContours(masked_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contour_list:
        contour_perimeter = cv2.arcLength(contour, True)
        epsilon = accuracy * contour_perimeter

        polygon_approximation_of_contour_perimeter = cv2.approxPolyDP(contour, epsilon, True)
        reshaped_polygon_approximation_of_contour_perimeter = polygon_approximation_of_contour_perimeter.reshape(-1, 2)

        area = cv2.contourArea(reshaped_polygon_approximation_of_contour_perimeter)
        if len(reshaped_polygon_approximation_of_contour_perimeter) >= 3 and minimum_area < area < max_area:
            platform_polygons.append(reshaped_polygon_approximation_of_contour_perimeter)

    return platform_polygons

#returns mapped_polygons
def get_mapped_platform_polygons(frame, lower_bound, upper_bound, homography_matrix):
    mapped_platform_polygon_list = []
    platform_polygon_list = _get_platform_polygons(frame, lower_bound, upper_bound)

    for platform_polygon in platform_polygon_list:
        mapped_platform_polygon_list.append(map_polygon(platform_polygon, homography_matrix))

    return mapped_platform_polygon_list

def run_debug_webcam_window(video_capture_device_number, pygame_width, pygame_height):
    lower_bound = np.array([0, 0, 0])
    upper_bound = np.array([179, 255, 255])

    calibrate_color(lower_bound, upper_bound)

    calibration_points = find_calibration_points()
    homography_matrix = calculate_homography_matrix(calibration_points, pygame_width, pygame_height)

    capture = cv2.VideoCapture(video_capture_device_number)
    while True:
        ret, frame = capture.read()

        #exit options
        if not ret:
            print(f"Failed to grab frame at index {video_capture_device_number}")
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


        mapped_frame = map_frame(frame, homography_matrix, pygame_width, pygame_height)
        platform_polygons = _get_platform_polygons(mapped_frame, lower_bound, upper_bound)

        frame_overlay = mapped_frame.copy()
        frame_overlay = cv2.fillPoly(frame_overlay,platform_polygons,(0,255,0))

        mapped_frame_with_overlay = cv2.addWeighted(mapped_frame, 0.6, frame_overlay, 0.4, 0)

        cv2.imshow("webcam debug window", mapped_frame_with_overlay)

    capture.release()
    cv2.destroyAllWindows()

def capture_webcam_frame_and_get_platform_polygons(capture, homography_matrix, lower_bound, upper_bound, pygame_width, pygame_height):

    ret, frame = capture.read()
    if not ret:
        print("failed to read capture")
        return []

    mapped_frame = map_frame(frame, homography_matrix, pygame_width, pygame_height)
    platform_polygons = _get_platform_polygons(mapped_frame, lower_bound, upper_bound)

    return platform_polygons

def get_capture(capture_device_number):
    return cv2.VideoCapture(capture_device_number, cv2.CAP_V4L2)

def get_video_capture_number():
    # Automatically prefer external USB webcam over integrated webcam on Linux
    usb_candidates = []
    fallback_candidates = []

    for name_path in sorted(glob.glob("/sys/class/video4linux/video*/name")):
        try:
            dev_dir = os.path.dirname(name_path)
            dev_node = os.path.basename(dev_dir)  # e.g. "video2"
            idx = int(dev_node.replace("video", ""))
            with open(name_path, "r") as f:
                cam_name = f.read().strip()
            if "integrated" not in cam_name.lower():
                usb_candidates.append((idx, cam_name))
            else:
                fallback_candidates.append((idx, cam_name))
        except Exception:
            pass

    for idx, cam_name in usb_candidates + fallback_candidates:
        cap = cv2.VideoCapture(idx, cv2.CAP_V4L2)
        if cap.isOpened():
            ret, _ = cap.read()
            cap.release()
            if ret:
                print(f"Using camera index {idx}: {cam_name}")
                return idx

    window_name = "Choose Video Capture Device Number: HIT ENTER TO SELECT"
    cv2.namedWindow(window_name)
    cv2.moveWindow(window_name, 100, 100)
    cv2.resizeWindow(window_name,800,100)
    cv2.createTrackbar("Camera num", window_name, 2, 5, do_nothing)

    while True:
        if cv2.waitKey(1) & 0xFF == 13:
            break

    selected_number = cv2.getTrackbarPos("Camera num", window_name)
    cv2.destroyWindow(window_name)

    return selected_number