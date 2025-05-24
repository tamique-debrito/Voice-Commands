import cv2
import numpy as np

ref_img = cv2.imread('./vision/ref.jpg', cv2.IMREAD_GRAYSCALE)
target_img = cv2.imread('./vision/target1.jpg', cv2.IMREAD_GRAYSCALE)

def run_sift():
    sift = cv2.SIFT_create()

    # Find keypoints and descriptors
    kp1, des1 = sift.detectAndCompute(ref_img, None)
    kp2, des2 = sift.detectAndCompute(target_img, None)

    # Use FLANN-based matcher (fast and suitable for SIFT's float descriptors)
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)

    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)

    # Apply Lowe's ratio test to filter good matches
    good = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good.append(m)

    # Proceed if enough good matches are found
    MIN_MATCH_COUNT = 10
    if len(good) >= MIN_MATCH_COUNT:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

        # Compute homography
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        matches_mask = mask.ravel().tolist()

        # Get dimensions of reference image
        h, w = ref_img.shape
        pts = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)

        # Transform points using homography
        dst = cv2.perspectiveTransform(pts, M)

        # Draw the detected object boundary in the scene
        img2_color = cv2.cvtColor(target_img, cv2.COLOR_GRAY2BGR)
        result_img = cv2.polylines(img2_color, [np.int32(dst)], True, (0, 255, 0), 3, cv2.LINE_AA)

        # Draw keypoint matches
        matched_img = cv2.drawMatches(ref_img, kp1, result_img, kp2, good, None, 
                                    matchesMask=matches_mask, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

        cv2.imshow('SIFT Object Detection', matched_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print(f"Not enough matches are found - {len(good)}/{MIN_MATCH_COUNT}")

run_sift()

def run_template_match():
    # Get dimensions of template
    h, w = ref_img.shape

    # Perform ref_img matching
    result = cv2.matchTemplate(target_img, ref_img, cv2.TM_CCOEFF_NORMED)

    # Find location with the highest match
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # Draw rectangle on the match
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)

    # Show result
    target_color = cv2.cvtColor(target_img, cv2.COLOR_GRAY2BGR)
    cv2.rectangle(target_color, top_left, bottom_right, (0, 255, 0), 2)

    cv2.imshow('Detected ref_img', target_color)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def run_orb():
    orb = cv2.ORB_create(nfeatures=5000)

    kp1, des1 = orb.detectAndCompute(ref_img, None)
    kp2, des2 = orb.detectAndCompute(target_img, None)

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)

    # Sort them by distance (lower distance is better)
    matches = sorted(matches, key=lambda x: x.distance)

    matched_img = cv2.drawMatches(ref_img, kp1, target_img, kp2, matches[:3], None, flags=2)
    cv2.imshow('Matches', matched_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
