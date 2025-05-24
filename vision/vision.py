import cv2
import multiprocessing
import time


# Constants
WINDOW_NAME = "Object Tracker"
MOTION_LINE = [(500, 50), (25, 100)] # The approximate line of motion along which the basket moves
PREDEFINED_RECT = (MOTION_LINE[0][0], MOTION_LINE[0][1], 50, 50)  # (x, y, w, h) of the area to place the object

LOWER_THRESHOLD = 75 # The threshold to use to determine whether the basket has been lowered
POS_THRESHOLD = 0.05 # The threshold for considering the basket to be at a certain location as a fraction of distance along the motion line

class Vision:
    def __init__(self):
        self._bbox_manager = multiprocessing.Manager()
        self._bbox = self._bbox_manager.list([None])  # Shared list for bbox
        self._process = multiprocessing.Process(target=self._run, args=(self._bbox,))
        self._process.daemon = True
        self._process_started = False
        # For calculations
        self.slope = (MOTION_LINE[1][1] - MOTION_LINE[0][1]) / (MOTION_LINE[1][0] - MOTION_LINE[0][0])
        self.x_range = (MOTION_LINE[1][0] - MOTION_LINE[0][0])

    def start(self):
        if not self._process_started:
            self._process.start()
            self._process_started = True

    def get_bbox(self):
        """Returns the current bounding box as a tuple (x, y, w, h) or None if not tracking."""
        curr_bbox = self._bbox[0]
        if curr_bbox is None:
            return None
        return tuple(curr_bbox)
    
    def get_info(self, checkpoint_ref):
        """
        checkpoint_ref: the "checkpoint" along the motion line (one at each end and one in the middle) to compare the current position against
        returns where the current position is relative to the checkpoint (1 = to the left, 0 = at, -1 = to the right) as well as whether the bucket should be considered lowered
        """
        bbox = self.get_bbox()
        if bbox is None:
            return None
        x, y = bbox[0:2]
        x_offset = x - MOTION_LINE[0][0] # The x offset from the reference point
        x_frac = x_offset / self.x_range
        y_ref = MOTION_LINE[0][1] + self.slope * x_offset # The reference for the y coordinate based on the motion line and the x position
        is_lowered = abs(y - y_ref) >= LOWER_THRESHOLD
        
        if checkpoint_ref == 0:
            checkpoint_frac = 0.0
        elif checkpoint_ref == 1:
            checkpoint_frac = 0.5
        elif checkpoint_ref == 2:
            checkpoint_frac = 1.0
        if abs(x_frac - checkpoint_frac) <= POS_THRESHOLD:
            checkpoint_rel = 0
        elif x_frac < checkpoint_frac:
            checkpoint_rel = 1
        elif x_frac > checkpoint_frac:
            checkpoint_rel = -1

        return checkpoint_rel, is_lowered


    def stop(self):
        if self._process_started:
            self._process.terminate()
            self._process.join()
            self._process_started = False

    @staticmethod
    def _run(shared_bbox):

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Cannot open webcam.")
            return

        tracker = cv2.TrackerCSRT_create() #type: ignore
        tracking = False
        bbox = None

        print("Move the object into the green box. Press 's' to start tracking. Press 'q' to quit.")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            x, y, w, h = PREDEFINED_RECT
            if not tracking:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, "Place object here & press 's'", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            if tracking:
                cv2.line(frame, MOTION_LINE[0], MOTION_LINE[1], (0, 255, 0), 2)
                cv2.line(frame, (MOTION_LINE[0][0], MOTION_LINE[0][1] + LOWER_THRESHOLD), (MOTION_LINE[1][0], MOTION_LINE[1][1] + LOWER_THRESHOLD), (40, 100, 40), 2)
                success, bbox = tracker.update(frame)
                if success:
                    x, y, w, h = [int(v) for v in bbox]
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    shared_bbox[0] = [x, y, w, h]
                else:
                    cv2.putText(frame, "Tracking lost", (50, 80),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    shared_bbox[0] = None

            cv2.imshow(WINDOW_NAME, frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('s'):
                bbox = PREDEFINED_RECT
                tracker.init(frame, bbox)
                tracking = True
                shared_bbox[0] = list(bbox)
                print(f"Started tracking")

            elif key == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        shared_bbox[0] = None
        # --- End main logic ---

if __name__ == "__main__":
    vis = Vision()
    vis.start()
    for i in range(10):
        time.sleep(5)
        print(vis.get_bbox())
        print(vis.get_info(0))
        print(vis.get_info(1))
        print(vis.get_info(2))
